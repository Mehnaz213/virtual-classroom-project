from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "Focus Mate"
    api_v1_prefix: str = "/api"
    secret_key: str = Field("super-secret-key", env="APP_SECRET_KEY")
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"

    database_url: str = Field(
        "sqlite:///./classroom.db",
        env="DATABASE_URL",
    )
    postgres_dsn: Optional[str] = Field(None, env="POSTGRES_DSN")

    allowed_origins: List[str] = Field(default_factory=lambda: ["*"])
    environment: str = Field("development", env="ENVIRONMENT")

    media_tmp_dir: str = "./tmp_frames"
    reports_dir: str = "./reports"

    test_mode: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False

    @validator("allowed_origins", pre=True)
    def _split_origins(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()

