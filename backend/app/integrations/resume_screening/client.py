"""Клиент внешнего AI-сервиса скрининга резюме (AI-CheckResume).

Сервис принимает резюме + требования вакансии и возвращает решение
pass/review/reject со score, совпавшими навыками и сообщением для HR.
"""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class ResumeScreeningClient:
    def __init__(self) -> None:
        self.base_url = settings.resume_screening_url.rstrip("/")
        self.enabled = bool(self.base_url)

    def is_available(self) -> bool:
        if not self.enabled:
            return False
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except httpx.HTTPError:
            return False

    def screen(
        self,
        file_name: str,
        content: bytes,
        vacancy_title: str,
        required_skills: str,
        optional_skills: str = "",
        min_experience_years: int = 0,
        timeout_seconds: float = 300.0,
    ) -> dict | None:
        """Возвращает ответ /screen-resume или None при ошибке."""
        if not self.enabled:
            return None
        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                response = client.post(
                    f"{self.base_url}/screen-resume",
                    files={"file": (file_name, content)},
                    data={
                        "vacancy_title": vacancy_title,
                        "required_skills": required_skills,
                        "optional_skills": optional_skills,
                        "min_experience_years": str(min_experience_years),
                    },
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as error:
            logger.warning(
                "Resume screening request failed (%s): %s", vacancy_title, error
            )
            return None
