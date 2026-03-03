"""Application configuration – loaded from environment variables / .env file."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration for the Finance Manager API."""

    # ── Database ──────────────────────────────────────────────
    DATABASE_URL: str = (
        "mssql+pyodbc://finance:Fin%40nce2012712!"
        "@(localdb)\\MSSQLLocalDB/FinanceDB"
        "?driver=ODBC+Driver+17+for+SQL+Server"
    )

    # ── JWT ───────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_EXPIRE_MINUTES: int = 10080  # 7 days

    # ── LLM (SiliconFlow) ────────────────────────────────────
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.siliconflow.cn/v1"
    LLM_MODEL: str = "Qwen/Qwen3-235B-A22B-Instruct-2507"

    # ── Redis ─────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
