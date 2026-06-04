"""Integration tests for the Books API — service layer and auth are mocked."""
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from library_catalog.main import app
from library_catalog.api.dependencies import get_book_service, get_current_user
from library_catalog.data.models.user import UserRole
from library_catalog.domain.exceptions import BookNotFoundException
from library_catalog.api.v1.schemas.book import ShowBook


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def mock_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture(autouse=True)
def override_book_service(mock_service):
    """Replace the real BookService with a mock for every test in this module."""
    app.dependency_overrides[get_book_service] = lambda: mock_service
    yield
    app.dependency_overrides.pop(get_book_service, None)


def _make_show_book(book_id: uuid.UUID | None = None) -> ShowBook:
    return ShowBook(
        book_id=book_id or uuid.uuid4(),
        title="Clean Code",
        author="Robert Martin",
        year=2008,
        genre="Programming",
        pages=464,
        available=True,
        isbn="978-0132350884",
        description=None,
        extra=None,
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )


def _make_user(role: UserRole) -> MagicMock:
    user = MagicMock()
    user.user_id = uuid.uuid4()
    user.role = role
    user.is_active = True
    return user


# ---------------------------------------------------------------------------
# GET /books  — public
# ---------------------------------------------------------------------------

def test_get_books_is_public(client, mock_service):
    mock_service.search_books.return_value = ([_make_show_book()], 1)

    response = client.get("/api/v1/books/")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1


def test_get_books_empty(client, mock_service):
    mock_service.search_books.return_value = ([], 0)

    response = client.get("/api/v1/books/")

    assert response.status_code == 200
    assert response.json()["total"] == 0


# ---------------------------------------------------------------------------
# GET /books/{id}  — public
# ---------------------------------------------------------------------------

def test_get_book_by_id_public(client, mock_service):
    bid = uuid.uuid4()
    mock_service.get_book.return_value = _make_show_book(bid)

    response = client.get(f"/api/v1/books/{bid}")

    assert response.status_code == 200
    assert response.json()["book_id"] == str(bid)


def test_get_book_not_found_returns_404(client, mock_service):
    bid = uuid.uuid4()
    mock_service.get_book.side_effect = BookNotFoundException(bid)

    response = client.get(f"/api/v1/books/{bid}")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /books  — auth required
# ---------------------------------------------------------------------------

VALID_BOOK_PAYLOAD = {
    "title": "Clean Code",
    "author": "Robert Martin",
    "year": 2008,
    "genre": "Programming",
    "pages": 464,
}


def test_create_book_without_auth_returns_401(client):
    response = client.post("/api/v1/books/", json=VALID_BOOK_PAYLOAD)
    assert response.status_code == 401


def test_create_book_with_auth_returns_201(client, mock_service):
    app.dependency_overrides[get_current_user] = lambda: _make_user(UserRole.user)
    mock_service.create_book.return_value = _make_show_book()
    try:
        response = client.post("/api/v1/books/", json=VALID_BOOK_PAYLOAD)
        assert response.status_code == 201
    finally:
        app.dependency_overrides.pop(get_current_user, None)


# ---------------------------------------------------------------------------
# PATCH /books/{id}  — auth required
# ---------------------------------------------------------------------------

def test_update_book_without_auth_returns_401(client):
    response = client.patch(f"/api/v1/books/{uuid.uuid4()}", json={"title": "New"})
    assert response.status_code == 401


def test_update_book_with_auth_returns_200(client, mock_service):
    app.dependency_overrides[get_current_user] = lambda: _make_user(UserRole.user)
    bid = uuid.uuid4()
    mock_service.update_book.return_value = _make_show_book(bid)
    try:
        response = client.patch(f"/api/v1/books/{bid}", json={"title": "Updated"})
        assert response.status_code == 200
    finally:
        app.dependency_overrides.pop(get_current_user, None)


# ---------------------------------------------------------------------------
# DELETE /books/{id}  — admin only
# ---------------------------------------------------------------------------

def test_delete_book_without_auth_returns_401(client):
    response = client.delete(f"/api/v1/books/{uuid.uuid4()}")
    assert response.status_code == 401


def test_delete_book_as_regular_user_returns_403(client):
    """Regular user is rejected by require_role(admin)."""
    app.dependency_overrides[get_current_user] = lambda: _make_user(UserRole.user)
    try:
        response = client.delete(f"/api/v1/books/{uuid.uuid4()}")
        assert response.status_code == 403
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_delete_book_as_admin_returns_204(client, mock_service):
    app.dependency_overrides[get_current_user] = lambda: _make_user(UserRole.admin)
    mock_service.delete_book.return_value = None
    try:
        response = client.delete(f"/api/v1/books/{uuid.uuid4()}")
        assert response.status_code == 204
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_delete_nonexistent_book_returns_404(client, mock_service):
    app.dependency_overrides[get_current_user] = lambda: _make_user(UserRole.admin)
    bid = uuid.uuid4()
    mock_service.delete_book.side_effect = BookNotFoundException(bid)
    try:
        response = client.delete(f"/api/v1/books/{bid}")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.pop(get_current_user, None)
