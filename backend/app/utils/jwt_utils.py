from jose import jwt
from datetime import datetime, timedelta, timezone
from app.core.settings import settings

SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_expire_minutes


class JWTUtils:

    @staticmethod
    def create_access_token(data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_token(token: str):
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])