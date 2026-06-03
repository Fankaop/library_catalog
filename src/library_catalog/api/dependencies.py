import uuid
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..data.repositories.book_repository import BookRepository
from ..domain.services.book_service import BookService
from ..external.openlibrary.client import OpenLibraryClient
from ..core.config import settings

#зависимости для jwt аутентификации
from fastapi import Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from ..core.security import decode_token
from ..core.exceptions import UnauthorizedException, ForbiddenException
from ..data.models.user import UserRole, User
from ..data.repositories.user_repository import UserRepository

# ========== EXTERNAL CLIENTS (Singletons) ==========

@lru_cache
def get_openlibrary_client() -> OpenLibraryClient:
    """
    Получить singleton OpenLibraryClient.
    
    lru_cache создает клиент один раз и переиспользует.
    """
    return OpenLibraryClient(
        base_url=settings.openlibrary_base_url,
        timeout=settings.openlibrary_timeout,
    )


# ========== REPOSITORIES ==========

async def get_book_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> BookRepository:
    """
    Создать BookRepository для текущей сессии БД.
    
    Создается новый экземпляр для каждого запроса.
    """
    return BookRepository(db)


# ========== SERVICES ==========

async def get_book_service(
    book_repo: Annotated[BookRepository, Depends(get_book_repository)],
    ol_client: Annotated[OpenLibraryClient, Depends(get_openlibrary_client)],
) -> BookService:
    """
    Создать BookService с внедренными зависимостями.
    
    FastAPI автоматически разрешит все зависимости:
    1. get_db() создаст AsyncSession
    2. get_book_repository() создаст BookRepository с session
    3. get_openlibrary_client() вернет singleton клиент
    4. Все внедрится в BookService
    """
    return BookService(
        book_repository=book_repo,
        openlibrary_client=ol_client,
    )


# ========== TYPE ALIASES ДЛЯ УДОБСТВА ==========

# Можно использовать в роутерах так:
# async def my_route(service: BookServiceDep):
BookServiceDep = Annotated[BookService, Depends(get_book_service)]
BookRepoDep = Annotated[BookRepository, Depends(get_book_repository)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db)]


# ========== JWT AUTH ==========
bearer_scheme = HTTPBearer()

async def get_user_repository(db: DbSessionDep) -> UserRepository:
    return UserRepository(db)

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise UnauthorizedException("Invalid or expired token")
    
    user = await user_repo.get_by_id(uuid.UUID(payload["sub"]))
    if not user or not user.is_active:
        raise UnauthorizedException()
    return user

def require_role(*roles: UserRole):
    """Фабрика зависимостей для проверки роли."""
    async def checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in roles:
            raise ForbiddenException()
        return current_user
    return checker


# ========== TYPE ALIASES ==========
CurrentUserDep = Annotated[User, Depends(get_current_user)]
AdminDep = Annotated[User, Depends(require_role(UserRole.admin))]
