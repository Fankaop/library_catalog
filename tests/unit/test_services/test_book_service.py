"""Unit tests for BookService — all DB and external calls are mocked."""
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from library_catalog.api.v1.schemas.book import BookCreate, BookUpdate, ShowBook
from library_catalog.domain.exceptions import (
    BookAlreadyExistsException,
    BookNotFoundException,
    InvalidPagesException,
    InvalidYearException,
    OpenLibraryException,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_book_create(**overrides) -> BookCreate:
    defaults = dict(
        title="Clean Code",
        author="Robert Martin",
        year=2008,
        genre="Programming",
        pages=464,
    )
    defaults.update(overrides)
    return BookCreate(**defaults)


# ---------------------------------------------------------------------------
# create_book
# ---------------------------------------------------------------------------

async def test_create_book_success(book_service, mock_book_repo, mock_ol_client, sample_book):
    mock_book_repo.find_by_isbn.return_value = None
    mock_book_repo.create.return_value = sample_book
    mock_ol_client.enrich.return_value = {"cover_url": "http://covers.openlibrary.org/1.jpg"}

    result = await book_service.create_book(_make_book_create(isbn="978-0132350884"))

    assert isinstance(result, ShowBook)
    assert result.title == "Clean Code"
    mock_book_repo.create.assert_called_once()


async def test_create_book_invalid_year_raises(book_service):
    with pytest.raises(InvalidYearException):
        await book_service.create_book(_make_book_create(year=2100))


def test_validate_year_too_old_raises(book_service):
    # year=999 is blocked by Pydantic schema (ge=1000), test service guard directly
    with pytest.raises(InvalidYearException):
        book_service._validate_year(999)


def test_validate_pages_zero_raises(book_service):
    with pytest.raises(InvalidPagesException):
        book_service._validate_pages(0)


def test_validate_pages_negative_raises(book_service):
    with pytest.raises(InvalidPagesException):
        book_service._validate_pages(-5)


async def test_create_book_duplicate_isbn_raises(book_service, mock_book_repo, sample_book):
    mock_book_repo.find_by_isbn.return_value = sample_book

    with pytest.raises(BookAlreadyExistsException):
        await book_service.create_book(_make_book_create(isbn="978-0132350884"))


async def test_create_book_ol_failure_ignored(book_service, mock_book_repo, mock_ol_client, sample_book):
    """Open Library failure must not prevent book creation."""
    mock_book_repo.find_by_isbn.return_value = None
    mock_book_repo.create.return_value = sample_book
    mock_ol_client.enrich.side_effect = OpenLibraryException("timeout")

    result = await book_service.create_book(_make_book_create())

    assert isinstance(result, ShowBook)
    called_kwargs = mock_book_repo.create.call_args.kwargs
    assert called_kwargs.get("extra") is None


# ---------------------------------------------------------------------------
# get_book
# ---------------------------------------------------------------------------

async def test_get_book_success(book_service, mock_book_repo, sample_book):
    mock_book_repo.get_by_id.return_value = sample_book

    result = await book_service.get_book(sample_book.book_id)

    assert isinstance(result, ShowBook)
    assert result.title == "Clean Code"


async def test_get_book_not_found_raises(book_service, mock_book_repo):
    mock_book_repo.get_by_id.return_value = None

    with pytest.raises(BookNotFoundException):
        await book_service.get_book(uuid.uuid4())


# ---------------------------------------------------------------------------
# delete_book
# ---------------------------------------------------------------------------

async def test_delete_book_success(book_service, mock_book_repo):
    mock_book_repo.delete.return_value = True
    await book_service.delete_book(uuid.uuid4())  # must not raise


async def test_delete_book_not_found_raises(book_service, mock_book_repo):
    mock_book_repo.delete.return_value = False

    with pytest.raises(BookNotFoundException):
        await book_service.delete_book(uuid.uuid4())


# ---------------------------------------------------------------------------
# update_book
# ---------------------------------------------------------------------------

async def test_update_book_not_found_raises(book_service, mock_book_repo):
    mock_book_repo.get_by_id.return_value = None

    with pytest.raises(BookNotFoundException):
        await book_service.update_book(uuid.uuid4(), BookUpdate(title="New Title"))


async def test_update_book_success(book_service, mock_book_repo, sample_book):
    mock_book_repo.get_by_id.return_value = sample_book
    updated = MagicMock()
    updated.book_id = sample_book.book_id
    updated.title = "New Title"
    updated.author = sample_book.author
    updated.year = sample_book.year
    updated.genre = sample_book.genre
    updated.pages = sample_book.pages
    updated.available = sample_book.available
    updated.isbn = sample_book.isbn
    updated.description = sample_book.description
    updated.extra = sample_book.extra
    updated.created_at = sample_book.created_at
    updated.updated_at = sample_book.updated_at
    mock_book_repo.update.return_value = updated

    result = await book_service.update_book(sample_book.book_id, BookUpdate(title="New Title"))

    assert isinstance(result, ShowBook)


# ---------------------------------------------------------------------------
# search_books
# ---------------------------------------------------------------------------

async def test_search_books_returns_paginated(book_service, mock_book_repo, sample_book):
    mock_book_repo.find_by_filters.return_value = [sample_book]
    mock_book_repo.count_by_filters.return_value = 1

    books, total = await book_service.search_books(title="Clean", limit=20, offset=0)

    assert total == 1
    assert len(books) == 1
    assert isinstance(books[0], ShowBook)


async def test_search_books_empty_result(book_service, mock_book_repo):
    mock_book_repo.find_by_filters.return_value = []
    mock_book_repo.count_by_filters.return_value = 0

    books, total = await book_service.search_books()

    assert total == 0
    assert books == []
