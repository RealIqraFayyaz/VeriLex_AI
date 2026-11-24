
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite+aiosqlite:///./verilex.db"

    secret_key: str = Field(min_length=32)
    jwt_secret_key: str = Field(min_length=32)

    access_token_expire_minutes: int = Field(default=30, gt=0, le=1440)

    cors_origins: str = "http://localhost:3000"

    upload_dir: str = "./private_uploads"
    max_upload_mb: int = Field(default=20, gt=0, le=500)

    bootstrap_admin_email: str = ""
    bootstrap_admin_password: str = ""

    enable_sentence_transformers: bool = True
    embedding_model: str = (
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("DATABASE_URL cannot be empty")
        return value

    @property
    def allowed_origins(self):
        return [
            origin.strip().rstrip("/")
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache(maxsize=1)
def get_settings():
    return Settings()


settings = get_settings()
