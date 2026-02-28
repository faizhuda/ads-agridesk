from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.repositories.user_repository import InMemoryUserRepository
from app.services.auth_service import AuthService
from app.schemas.auth_schema import RegisterRequest

router = APIRouter()

repo = InMemoryUserRepository()
service = AuthService(repo)


@router.post("/register")
def register(request: RegisterRequest):
    user = service.register(
        request.name,
        request.email,
        request.password,
        request.role
    )
    return {"email": user.email, "role": user.role.value}


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return service.login(form_data.username, form_data.password)