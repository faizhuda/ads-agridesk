from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.utils.jwt_utils import JWTUtils

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = JWTUtils.decode_token(token)
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Token tidak valid")


def require_role(required_role: str):
    def role_checker(user=Depends(get_current_user)):
        if user["role"] != required_role:
            raise HTTPException(status_code=403, detail="Akses ditolak")
        return user
    return role_checker