from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "KMG Onboarding AI Module"
    app_version: str = "0.1.0"
    environment: str = "development"

    frontend_url: str = "http://localhost:5173"

    database_url: str = (
        "postgresql://kmg_user:kmg_password@localhost:5432/kmg_onboarding"
    )

    risk_engine_interval_minutes: int = 30

    bitrix_webhook_url: str = ""
    bitrix_bot_id: int | None = None
    bitrix_hr_user_id: int | None = None

    chairman_video_url: str = "https://team.kmg.kz/onboarding/welcome-video"

    llm_enabled: bool = True
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "qwen2.5:3b"
    llm_temperature: float = 0.12
    llm_max_tokens: int = 512
    llm_timeout_seconds: float = 90.0

    # URL внешнего AI-сервиса скрининга резюме (AI-CheckResume); пусто — отключён
    resume_screening_url: str = ""

    docs_path: str = ""
    embedding_model: str = "nomic-embed-text"
    rag_min_score: float = 0.35
    rag_search_limit: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("bitrix_bot_id", "bitrix_hr_user_id", mode="before")
    @classmethod
    def empty_int_to_none(cls, value: object) -> object:
        if value == "" or value is None:
            return None
        return value


settings = Settings()
