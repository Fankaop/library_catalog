from ...data.repositories.user_repository import UserRepository
from ...core.security import hash_password, verify_password, create_access_token
from ...core.exceptions import UnauthorizedException, ConflictException


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, email: str, username: str, password: str):
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ConflictException("Email already registered")
        hashed = hash_password(password)
        return await self.user_repo.create(email, username, hashed)

    async def login(self, email: str, password: str) -> str:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid credentials")
        return create_access_token(sub=str(user.user_id), role=user.role.value)