"""AI-рекрутинг: парсинг резюме и подбор подходящего отдела."""

import json
import logging
import re
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.integrations.resume_screening.client import ResumeScreeningClient
from app.models.department import Department
from app.models.employee import Employee
from app.models.recruiting import (
    Candidate,
    DepartmentMatch,
    RecruitingSettings,
    Resume,
    ResumeAnalysis,
)
from app.schemas.employee import EmployeeCreate
from app.services.knowledge_index_service import KnowledgeIndexService
from app.services.llm_service import LlmService

logger = logging.getLogger(__name__)

RESUMES_DIR = Path(__file__).resolve().parents[1] / "data" / "resumes"

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024

PARSE_SYSTEM_PROMPT = (
    "Вы — HR-аналитик. Извлеките структурированные данные из текста резюме. "
    "Ответьте строго в JSON: "
    '{"full_name":"...","email":"...","phone":"...",'
    '"skills":["..."],"experience_years":0,'
    '"education":"...","positions":["..."],"summary":"краткое резюме кандидата в 2-3 предложениях"}. '
    "Если данных нет, используйте null или пустой список."
)

MATCH_SYSTEM_PROMPT = (
    "Вы — HR-эксперт по подбору персонала. Оцените соответствие кандидата каждому отделу "
    "по навыкам, опыту и образованию. Ответьте строго в JSON: "
    '{"matches":[{"code":"КОД_ОТДЕЛА","score":0-100,"reasoning":"краткое обоснование"}]}. '
    "Включите все отделы из списка, отсортируйте по убыванию score."
)


class RecruitingAiService:
    @staticmethod
    def get_settings(db: Session) -> RecruitingSettings:
        settings_row = db.query(RecruitingSettings).first()
        if not settings_row:
            settings_row = RecruitingSettings(id=1)
            db.add(settings_row)
            db.commit()
            db.refresh(settings_row)
        return settings_row

    @staticmethod
    def save_resume_file(file_name: str, content: bytes) -> Path:
        RESUMES_DIR.mkdir(parents=True, exist_ok=True)
        suffix = Path(file_name).suffix.lower()
        stored_name = f"{uuid.uuid4().hex}{suffix}"
        target = RESUMES_DIR / stored_name
        target.write_bytes(content)
        return target

    @staticmethod
    def extract_text(file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            text, _ = KnowledgeIndexService.extract_pdf_text(file_path)
            return text
        if suffix == ".docx":
            return KnowledgeIndexService.extract_docx_text(file_path)
        return ""

    @staticmethod
    def parse_resume_llm(text: str) -> dict | None:
        truncated = text[:6000]
        return LlmService.generate_json(
            PARSE_SYSTEM_PROMPT,
            f"Текст резюме:\n{truncated}\n\nИзвлеките данные кандидата в JSON.",
        )

    @staticmethod
    def _fallback_parse(text: str) -> dict:
        email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text)
        phone_match = re.search(r"(?:\+7|8)[\s(-]*\d{3}[\s)-]*\d{3}[\s-]*\d{2}[\s-]*\d{2}", text)
        first_line = next(
            (line.strip() for line in text.splitlines() if line.strip()),
            "Кандидат",
        )
        return {
            "full_name": first_line[:120],
            "email": email_match.group(0) if email_match else None,
            "phone": phone_match.group(0) if phone_match else None,
            "skills": [],
            "experience_years": None,
            "education": None,
            "positions": [],
            "summary": text[:400],
        }

    @staticmethod
    def _fallback_match(
        text: str,
        departments: list[Department],
    ) -> list[dict]:
        """Keyword-matching по компетенциям отделов, если LLM недоступен."""
        lowered = text.lower()
        results: list[dict] = []
        for department in departments:
            keywords = [
                keyword.strip().lower()
                for keyword in (department.competencies or "").split(",")
                if keyword.strip()
            ]
            if not keywords:
                results.append(
                    {"code": department.code, "score": 0, "reasoning": "Нет компетенций для сравнения."}
                )
                continue
            hits = [keyword for keyword in keywords if keyword in lowered]
            score = round(100 * len(hits) / len(keywords))
            reasoning = (
                f"Совпадения по ключевым словам: {', '.join(hits[:6])}."
                if hits
                else "Совпадений по ключевым словам не найдено."
            )
            results.append({"code": department.code, "score": score, "reasoning": reasoning})
        results.sort(key=lambda item: item["score"], reverse=True)
        return results

    @staticmethod
    def match_departments_llm(
        parsed: dict,
        text: str,
        departments: list[Department],
        prompt_template: str | None = None,
    ) -> list[dict] | None:
        departments_block = "\n".join(
            f"- code: {department.code}, название: {department.name}, "
            f"профиль: {department.description or '—'}, "
            f"компетенции: {department.competencies or '—'}"
            for department in departments
        )
        candidate_block = json.dumps(parsed, ensure_ascii=False)
        user_prompt = (
            f"Отделы компании:\n{departments_block}\n\n"
            f"Профиль кандидата (JSON):\n{candidate_block}\n\n"
            f"Фрагмент резюме:\n{text[:3000]}\n\n"
            "Оцените соответствие кандидата каждому отделу."
        )
        system_prompt = prompt_template or MATCH_SYSTEM_PROMPT
        response = LlmService.generate_json(system_prompt, user_prompt)
        if not response:
            return None
        matches = response.get("matches")
        if not isinstance(matches, list):
            return None
        valid_codes = {department.code for department in departments}
        cleaned: list[dict] = []
        for item in matches:
            if not isinstance(item, dict):
                continue
            code = str(item.get("code", "")).strip()
            if code not in valid_codes:
                continue
            try:
                score = max(0, min(100, int(item.get("score", 0))))
            except (TypeError, ValueError):
                score = 0
            cleaned.append(
                {
                    "code": code,
                    "score": score,
                    "reasoning": str(item.get("reasoning", "")).strip() or None,
                }
            )
        cleaned.sort(key=lambda entry: entry["score"], reverse=True)
        return cleaned or None

    @staticmethod
    def screen_with_external_service(
        text: str,
        file_name: str,
        content: bytes,
        departments: list[Department],
        top_n: int,
    ) -> tuple[dict, list[dict]] | None:
        """Скрининг через внешний сервис AI-CheckResume.

        Сервис проверяет резюме против одной «вакансии», поэтому для подбора
        отдела вызываем его по top-N отделам (предотбор — keyword-matching
        по компетенциям), используя компетенции отдела как требуемые навыки.
        """
        client = ResumeScreeningClient()
        if not client.is_available():
            return None

        prefiltered = RecruitingAiService._fallback_match(text, departments)
        departments_by_code = {
            department.code: department for department in departments
        }
        target_codes = [item["code"] for item in prefiltered[:top_n]]

        matches: list[dict] = []
        candidate_info: dict = {}
        all_matched_skills: list[str] = []
        experience_years: int | None = None
        top_hr_message: str | None = None

        for code in target_codes:
            department = departments_by_code[code]
            response = client.screen(
                file_name=file_name,
                content=content,
                vacancy_title=department.name,
                required_skills=department.competencies or department.name,
            )
            if not response:
                continue

            screening = response.get("screening", {})
            if not candidate_info:
                candidate_info = response.get("candidate", {}) or {}
            if experience_years is None:
                experience_years = screening.get("experience_years_detected")

            matched_skills = screening.get("matched_required_skills", []) or []
            for skill in matched_skills:
                if skill not in all_matched_skills:
                    all_matched_skills.append(skill)

            decision = screening.get("decision")
            reason = screening.get("reason") or ""
            hr_message = screening.get("hr_message") or ""
            matches.append(
                {
                    "code": code,
                    "score": int(screening.get("score", 0)),
                    "reasoning": reason or hr_message or None,
                    "decision": decision,
                }
            )

        if not matches:
            return None

        matches.sort(key=lambda item: item["score"], reverse=True)
        if matches and not top_hr_message:
            top_code = matches[0]["code"]
            top_department = departments_by_code[top_code]
            top_hr_message = (
                f"Лучшее соответствие: {top_department.name} "
                f"({matches[0]['score']}%, решение скрининга: {matches[0].get('decision') or '—'})."
            )

        parsed = {
            "full_name": candidate_info.get("full_name"),
            "email": candidate_info.get("email"),
            "phone": candidate_info.get("phone"),
            "skills": all_matched_skills,
            "experience_years": experience_years,
            "education": None,
            "positions": [],
            "summary": top_hr_message,
        }
        return parsed, matches

    @staticmethod
    def analyze_resume(
        db: Session,
        file_name: str,
        content: bytes,
    ) -> tuple[Candidate, bool]:
        """Полный pipeline: сохранение файла, извлечение текста, AI-анализ, matching.

        Приоритет движков:
        1. Внешний сервис AI-CheckResume (resume-screening) — скрининг по отделам.
        2. Встроенный LLM-анализ через Ollama.
        3. Keyword-matching по компетенциям отделов.
        """
        settings_row = RecruitingAiService.get_settings(db)
        file_path = RecruitingAiService.save_resume_file(file_name, content)
        text = RecruitingAiService.extract_text(file_path)

        departments = (
            db.query(Department).filter(Department.is_active.is_(True)).all()
        )

        llm_used = False
        parsed: dict | None = None
        matches: list[dict] | None = None

        if settings_row.llm_enabled and text.strip() and departments:
            external = RecruitingAiService.screen_with_external_service(
                text, file_name, content, departments, settings_row.top_n
            )
            if external:
                parsed, matches = external
                llm_used = True

        if parsed is None and settings_row.llm_enabled and text.strip():
            parsed = RecruitingAiService.parse_resume_llm(text)
            llm_used = parsed is not None
        if not parsed:
            parsed = RecruitingAiService._fallback_parse(text)
        elif not parsed.get("full_name"):
            parsed["full_name"] = RecruitingAiService._fallback_parse(text)["full_name"]

        candidate = Candidate(
            full_name=str(parsed.get("full_name") or "Кандидат")[:255],
            email=(parsed.get("email") or None),
            phone=(parsed.get("phone") or None),
            source="manual",
            status="analyzed",
        )
        db.add(candidate)
        db.flush()

        resume = Resume(
            candidate_id=candidate.id,
            file_path=str(file_path),
            file_name=file_name,
            extracted_text=text or None,
        )
        db.add(resume)
        db.flush()

        analysis = ResumeAnalysis(
            resume_id=resume.id,
            parsed_json=parsed,
            llm_summary=parsed.get("summary"),
        )
        db.add(analysis)
        db.flush()

        if matches is None and settings_row.llm_enabled and departments:
            matches = RecruitingAiService.match_departments_llm(
                parsed, text, departments, settings_row.prompt_template
            )
        if matches is None and departments:
            matches = RecruitingAiService._fallback_match(text, departments)

        departments_by_code = {department.code: department for department in departments}
        for rank, item in enumerate((matches or [])[: settings_row.top_n], start=1):
            department = departments_by_code.get(item["code"])
            if not department:
                continue
            db.add(
                DepartmentMatch(
                    analysis_id=analysis.id,
                    department_id=department.id,
                    score=item["score"],
                    reasoning=item.get("reasoning"),
                    rank=rank,
                    decision=item.get("decision"),
                )
            )

        db.commit()
        db.refresh(candidate)
        return candidate, llm_used

    @staticmethod
    def get_candidates(db: Session) -> list[Candidate]:
        return db.query(Candidate).order_by(Candidate.id.desc()).all()

    @staticmethod
    def get_candidate(db: Session, candidate_id: int) -> Candidate | None:
        return db.query(Candidate).filter(Candidate.id == candidate_id).first()

    @staticmethod
    def get_latest_analysis(db: Session, candidate: Candidate) -> ResumeAnalysis | None:
        if not candidate.resumes:
            return None
        latest_resume = candidate.resumes[-1]
        if not latest_resume.analyses:
            return None
        return latest_resume.analyses[-1]

    @staticmethod
    def confirm_department(
        db: Session,
        candidate: Candidate,
        department: Department,
    ) -> Candidate:
        candidate.confirmed_department_id = department.id
        db.commit()
        db.refresh(candidate)
        return candidate

    @staticmethod
    def hire(
        db: Session,
        candidate: Candidate,
        position: str | None,
        manager_name: str | None,
        start_date,
        bitrix_user_id: int | None,
    ) -> Employee:
        from datetime import date as date_type

        from app.services.employee_service import EmployeeService

        department = (
            db.query(Department)
            .filter(Department.id == candidate.confirmed_department_id)
            .first()
            if candidate.confirmed_department_id
            else None
        )

        payload = EmployeeCreate(
            full_name=candidate.full_name,
            email=candidate.email,
            position=position,
            department=department.name if department else None,
            department_id=department.id if department else None,
            manager_name=manager_name,
            start_date=start_date or date_type.today(),
            bitrix_user_id=bitrix_user_id,
        )
        employee = EmployeeService.create(db, payload)
        employee.candidate_id = candidate.id
        candidate.status = "hired"
        db.commit()
        db.refresh(employee)
        return employee
