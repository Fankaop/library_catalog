from fastapi import APIRouter, status
from ....api.dependencies import DbSessionDep
from ....data.repositories.user_repository import UserRepository
from ....domain.services.auth_service import AuthService
from ..schemas.auth import LoginSchema, RegisterSchema, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: RegisterSchema, db: DbSessionDep):
    service = AuthService(UserRepository(db))
    user = await service.register(data.email, data.username, data.password)
    return {"id": user.user_id, "email": user.email}


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginSchema, db: DbSessionDep):
    service = AuthService(UserRepository(db))
    token = await service.login(data.email, data.password)
    return TokenResponse(access_token=token)
