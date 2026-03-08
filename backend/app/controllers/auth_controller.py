from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.enums import UserRole
from app.schemas.user_schema import (
    LecturerSearchResponse,
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.utils.dependencies import get_current_user, require_role
from app.models.user import UserModel

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    try:
        service = AuthService(db)
        user = service.register(
            name=request.name,
            email=request.email,
            password=request.password,
            role=request.role,
            nim=request.nim,
            nip=request.nip,
        )
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    try:
        service = AuthService(db)
        result = service.login(email=request.email, password=request.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserModel = Depends(get_current_user)):
    return current_user


@router.get("/lecturers/search", response_model=List[LecturerSearchResponse])
def search_lecturers(
    q: str = Query(default="", min_length=0),
    limit: int = Query(default=10, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role(UserRole.MAHASISWA)),
):
    service = AuthService(db)
    return service.search_lecturers(q, limit=limit)
