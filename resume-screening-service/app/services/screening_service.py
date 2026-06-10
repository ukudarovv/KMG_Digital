from typing import Literal

from app.config import Settings
from app.schemas import (
    CandidateInfo,
    LLMResponse,
    MetaInfo,
    ScreeningResult,
    ScreenResumeResponse,
    VacancyInfo,
)
from app.services.llm_client import OllamaClient
from app.utils.json_parser import extract_json_from_text

SYSTEM_PROMPT = """Ты локальный HR screening assistant.
Твоя задача — проверить резюме кандидата по требованиям вакансии.
Ты не принимаешь финальное решение о найме.
Ты только даёшь рекомендацию для HR.

Правила:

1. Не выдумывай факты.
2. Используй только информацию из резюме.
3. Если навык явно не указан, считай, что он не подтверждён.
4. Если опыт не указан явно, верни null.
5. Не делай выводы по имени, полу, возрасту, национальности, фото, адресу, религии или другим личным признакам.
6. Оценивай только профессиональные требования: навыки, опыт, технологии, образование, проекты.
7. Верни только валидный JSON.
8. Не добавляй текст до или после JSON.

Формат ответа:

{
  "candidate": {
    "full_name": null,
    "email": null,
    "phone": null
  },
  "screening": {
    "decision": "pass | reject | review",
    "score": 0,
    "matched_required_skills": [],
    "missing_required_skills": [],
    "matched_optional_skills": [],
    "experience_years_detected": null,
    "reason": "",
    "hr_message": ""
  }
}"""


def _parse_skills(skills_str: str) -> list[str]:
    if not skills_str or not skills_str.strip():
        return []
    return [skill.strip() for skill in skills_str.split(",") if skill.strip()]


def _normalize_skill_lists(
    required_skills: list[str],
    llm_matched: list[str],
    llm_missing: list[str],
) -> tuple[list[str], list[str]]:
    """Keep only skills from the vacancy list; infer missing from required if needed."""
    required_lower = {s.lower(): s for s in required_skills}
    matched: list[str] = []
    for skill in llm_matched:
        canonical = required_lower.get(skill.lower())
        if canonical and canonical not in matched:
            matched.append(canonical)

    missing: list[str] = []
    for skill in llm_missing:
        canonical = required_lower.get(skill.lower())
        if canonical and canonical not in missing:
            missing.append(canonical)

    if not missing:
        matched_set = {s.lower() for s in matched}
        missing = [s for s in required_skills if s.lower() not in matched_set]

    return matched, missing


def _normalize_optional_skills(optional_skills: list[str], llm_matched: list[str]) -> list[str]:
    optional_lower = {s.lower(): s for s in optional_skills}
    matched: list[str] = []
    for skill in llm_matched:
        canonical = optional_lower.get(skill.lower())
        if canonical and canonical not in matched:
            matched.append(canonical)
    return matched


def _required_match_percent(matched: list[str], required: list[str]) -> float:
    if not required:
        return 100.0
    return (len(matched) / len(required)) * 100


def _experience_sufficient(
    detected: int | None, min_years: int, incomplete_data: bool
) -> bool | None:
    if incomplete_data:
        return None
    if detected is None:
        return None
    return detected >= min_years


def _apply_decision_rules(
    matched_required: list[str],
    required_skills: list[str],
    experience_years_detected: int | None,
    min_experience_years: int,
    incomplete_data: bool,
) -> Literal["pass", "reject", "review"]:
    if incomplete_data:
        return "review"

    match_percent = _required_match_percent(matched_required, required_skills)
    experience_ok = _experience_sufficient(
        experience_years_detected, min_experience_years, incomplete_data=False
    )

    if match_percent >= 80:
        if experience_ok is True:
            return "pass"
        return "review"

    if match_percent >= 50:
        return "review"

    return "reject"


def _build_hr_message(
    decision: Literal["pass", "reject", "review"],
    reason: str,
    llm_hr_message: str,
) -> str:
    if llm_hr_message.strip():
        base = llm_hr_message.strip()
    elif reason.strip():
        base = reason.strip()
    else:
        base = "Результаты автоматической проверки резюме."

    if decision == "reject":
        return (
            f"{base} Кандидат не рекомендован к следующему этапу по результатам "
            "автоматической проверки. Финальное решение принимает HR."
        )
    if decision == "review":
        return (
            f"{base} Рекомендуется ручная проверка HR. "
            "Финальное решение принимает HR."
        )
    return (
        f"{base} Кандидат соответствует основным требованиям по автоматической проверке. "
        "Финальное решение принимает HR."
    )


def _build_user_prompt(
    resume_text: str,
    vacancy_title: str,
    required_skills: list[str],
    optional_skills: list[str],
    min_experience_years: int,
) -> str:
    return f"""Проверь резюме кандидата по вакансии.

Вакансия: {vacancy_title}
Обязательные навыки: {", ".join(required_skills) if required_skills else "не указаны"}
Желательные навыки: {", ".join(optional_skills) if optional_skills else "не указаны"}
Минимальный опыт (лет): {min_experience_years}

Резюме:
---
{resume_text}
---

Верни только JSON в указанном формате."""


class ScreeningService:
    def __init__(self, settings: Settings, llm_client: OllamaClient) -> None:
        self._settings = settings
        self._llm = llm_client

    async def screen_resume(
        self,
        resume_text: str,
        filename: str,
        file_type: Literal["pdf", "docx"],
        vacancy_title: str,
        required_skills_raw: str,
        optional_skills_raw: str,
        min_experience_years: int,
        candidate_full_name: str | None = None,
        candidate_email: str | None = None,
        candidate_phone: str | None = None,
    ) -> ScreenResumeResponse:
        required_skills = _parse_skills(required_skills_raw)
        optional_skills = _parse_skills(optional_skills_raw)

        vacancy = VacancyInfo(
            title=vacancy_title,
            required_skills=required_skills,
            optional_skills=optional_skills,
            min_experience_years=min_experience_years,
        )

        user_prompt = _build_user_prompt(
            resume_text=resume_text,
            vacancy_title=vacancy_title,
            required_skills=required_skills,
            optional_skills=optional_skills,
            min_experience_years=min_experience_years,
        )

        raw_response = await self._llm.generate(SYSTEM_PROMPT, user_prompt)
        parsed = extract_json_from_text(raw_response)

        incomplete_data = False
        if parsed is None:
            incomplete_data = True
            llm_data = LLMResponse()
            screening = ScreeningResult(
                decision="review",
                score=0,
                reason="Не удалось надёжно обработать ответ модели",
                hr_message=_build_hr_message("review", "Не удалось надёжно обработать ответ модели", ""),
            )
            candidate = CandidateInfo(
                full_name=candidate_full_name,
                email=candidate_email,
                phone=candidate_phone,
            )
        else:
            try:
                llm_data = LLMResponse.model_validate(parsed)
            except Exception:
                incomplete_data = True
                llm_data = LLMResponse()
                screening = ScreeningResult(
                    decision="review",
                    score=0,
                    reason="Не удалось надёжно обработать ответ модели",
                    hr_message=_build_hr_message("review", "Не удалось надёжно обработать ответ модели", ""),
                )
                candidate = CandidateInfo(
                    full_name=candidate_full_name,
                    email=candidate_email,
                    phone=candidate_phone,
                )
            else:
                candidate = CandidateInfo(
                    full_name=candidate_full_name or llm_data.candidate.full_name,
                    email=candidate_email or llm_data.candidate.email,
                    phone=candidate_phone or llm_data.candidate.phone,
                )

                matched_required, missing_required = _normalize_skill_lists(
                    required_skills,
                    llm_data.screening.matched_required_skills,
                    llm_data.screening.missing_required_skills,
                )
                matched_optional = _normalize_optional_skills(
                    optional_skills,
                    llm_data.screening.matched_optional_skills,
                )

                decision = _apply_decision_rules(
                    matched_required=matched_required,
                    required_skills=required_skills,
                    experience_years_detected=llm_data.screening.experience_years_detected,
                    min_experience_years=min_experience_years,
                    incomplete_data=incomplete_data,
                )

                # Override LLM decision with rule-based decision for consistency
                match_percent = _required_match_percent(matched_required, required_skills)
                score = int(round(match_percent)) if required_skills else llm_data.screening.score

                reason = llm_data.screening.reason or ""
                hr_message = _build_hr_message(
                    decision, reason, llm_data.screening.hr_message
                )

                screening = ScreeningResult(
                    decision=decision,
                    score=score,
                    matched_required_skills=matched_required,
                    missing_required_skills=missing_required,
                    matched_optional_skills=matched_optional,
                    experience_years_detected=llm_data.screening.experience_years_detected,
                    reason=reason,
                    hr_message=hr_message,
                )

        meta = MetaInfo(
            filename=filename,
            file_type=file_type,
            llm_model=self._settings.ollama_model,
        )

        return ScreenResumeResponse(
            candidate=candidate,
            vacancy=vacancy,
            screening=screening,
            meta=meta,
        )
