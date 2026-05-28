from pathlib import Path
import secrets

from pydantic import Field
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DATABASE_URL: str  # Required — set via .env or environment variable
    SECRET_KEY: str = None  # Wajib set di .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    UPLOAD_DIR: str = "uploads"

    # Public URL for generating QR codes that are scannable from mobile.
    # Override in .env or docker-compose for production.
    BASE_URL: str = "http://localhost:8000"

    # CORS allowed origins. In production, set this to your actual frontend URL(s).
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost",
        "http://127.0.0.1",
    ]

    # Storage — defaults to local filesystem (False = no S3/MinIO)
    USE_S3: bool = False

    model_config = {"env_file": str(BASE_DIR / ".env"), "extra": "ignore"}


try:
    settings = Settings()
    if not settings.SECRET_KEY or settings.SECRET_KEY.strip() == "" or settings.SECRET_KEY == "change-this-secret-key-in-production":
        raise ValueError("SECRET_KEY must be set to a secure value in your environment or .env file.")
except Exception as e:
    import sys
    print("\n" + "=" * 80, file=sys.stderr)
    print("CRITICAL CONFIGURATION ERROR — startup aborted.", file=sys.stderr)
    print("One or more required settings are missing or invalid:", file=sys.stderr)
    print("  • DATABASE_URL  — PostgreSQL connection string (required, no default)", file=sys.stderr)
    print("  • SECRET_KEY    — secure random string for JWT signing", file=sys.stderr)
    print("", file=sys.stderr)
    print("Set these in backend/.env:", file=sys.stderr)
    print("  DATABASE_URL=postgresql://user:password@host:5432/dbname", file=sys.stderr)
    print("  SECRET_KEY=" + secrets.token_urlsafe(32), file=sys.stderr)
    print("=" * 80 + "\n", file=sys.stderr)
    raise RuntimeError("Application startup aborted due to missing required configuration.") from e

