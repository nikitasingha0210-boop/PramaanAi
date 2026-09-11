"""
PramaanAI configuration.

Reads from environment variables / .env. Defaults are safe for local
development only — production deployments MUST override SECRET_KEY and
DATABASE_URL.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "PramaanAI"
    ENV: str = "development"

    # In production this should point at Postgres, e.g.
    # postgresql+psycopg2://pramaanai:password@db:5432/pramaanai
    # For zero-setup local/demo use we default to SQLite.
    DATABASE_URL: str = "sqlite:///./pramaanai.db"

    SECRET_KEY: str = "CHANGE_ME_dev_only_insecure_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 hour shift-length sessions

    # Uploaded document constraints
    MAX_UPLOAD_MB: int = 15
    ALLOWED_UPLOAD_EXTENSIONS: tuple = (".pdf", ".jpg", ".jpeg", ".png")

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:4173"]


settings = Settings()
