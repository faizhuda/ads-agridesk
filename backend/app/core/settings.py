import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:faiz123@localhost:5432/agridesk",
    )
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "SUPER_SECRET_KEY_CHANGE_ME")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    hash_secret: str = os.getenv("AGRIDESK_HASH_SECRET", "AGRIDESK_SECRET_KEY_CHANGE_ME")
    documents_dir: str = os.getenv("AGRIDESK_DOCUMENTS_DIR", "backend/storage/documents")
    rate_limit_enabled: bool = os.getenv("AGRIDESK_RATE_LIMIT_ENABLED", "true").lower() == "true"
    rate_limit_window_seconds: int = int(os.getenv("AGRIDESK_RATE_LIMIT_WINDOW_SECONDS", "60"))
    rate_limit_requests: int = int(os.getenv("AGRIDESK_RATE_LIMIT_REQUESTS", "120"))


settings = Settings()