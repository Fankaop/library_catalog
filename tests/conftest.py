import os

# Must come before any app-module imports so that Settings() reads these values.
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/library_catalog_test",
)
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-purposes-only")

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from library_catalog.data.models.book import Book
from library_catalog.data.models.user import User, UserRole
from library_catalog.domain.services.book_service import BookService
from library_catalog.api.v1.schemas.book import ShowBook


# ---------------------------------------------------------------------------
# Shared data fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def book_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def sample_book(book_id: uuid.UUID) -> MagicMock:
    """Fake Book ORM object — no real database required."""
    book = MagicMock(spec=Book)
    book.book_id = book_id
    book.title = "Clean Code"
    book.author = "Robert Martin"
    book.year = 2008
    book.genre = "Programming"
    book.pages = 464
    book.available = True
    book.isbn = "978-0132350884"
    book.description = "A handbook of agile software craftsmanship"
    book.extra = None
    book.created_at = datetime(2024, 1, 1, 12, 0, 0)
    book.updated_at = datetime(2024, 1, 1, 12, 0, 0)
    return book


@pytest.fixture
def sample_show_book(book_id: uuid.UUID) -> ShowBook:
    return ShowBook(
        book_id=book_id,
        title="Clean Code",
        author="Robert Martin",
        year=2008,
        genre="Programming",
        pages=464,
        available=True,
        isbn="978-0132350884",
        description=None,
        extra=None,
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        updated_at=datetime(2024, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def admin_user() -> MagicMock:
    user = MagicMock(spec=User)
    user.user_id = uuid.uuid4()
    user.role = UserRole.admin
    user.is_active = True
    return user


@pytest.fixture
def regular_user() -> MagicMock:
    user = MagicMock(spec=User)
    user.user_id = uuid.uuid4()
    user.role = UserRole.user
    user.is_active = True
    return user


# ---------------------------------------------------------------------------
# Service-layer fixtures (mocked repos + clients)
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_book_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_ol_client() -> AsyncMock:
    client = AsyncMock()
    client.enrich.return_value = {}
    return client


@pytest.fixture
def book_service(mock_book_repo: AsyncMock, mock_ol_client: AsyncMock) -> BookService:
    return BookService(
        book_repository=mock_book_repo,
        openlibrary_client=mock_ol_client,
    )
