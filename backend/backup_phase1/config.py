from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite+aiosqlite:///./verilex.db"
    secret_key: str = "local-secret-change-me"
    jwt_secret_key: str = "local-jwt-change-me"
    access_token_expire_minutes: int = 30
    cors_origins: str = "http://localhost:3000"
    upload_dir: str = "./private_uploads"
    max_upload_mb: int = 20
    bootstrap_admin_email: str = ""
    bootstrap_admin_password: str = ""
    enable_sentence_transformers: bool = True
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    @property
    def allowed_origins(self):
        return [v.strip() for v in self.cors_origins.split(",") if v.strip()]

@lru_cache
def get_settings():
    return Settings()
settings = get_settings()
