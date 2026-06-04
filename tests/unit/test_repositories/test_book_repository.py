"""Unit tests for BookRepository — SQLAlchemy session is mocked."""
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from library_catalog.data.repositories.book_repository import BookRepository


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def repo(mock_session: AsyncMock) -> BookRepository:
    return BookRepository(mock_session)


# ---------------------------------------------------------------------------
# find_by_isbn
# ---------------------------------------------------------------------------

async def test_find_by_isbn_returns_book(repo, mock_session, sample_book):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_book
    mock_session.execute.return_value = mock_result

    result = await repo.find_by_isbn("978-0132350884")

    assert result is sample_book
    mock_session.execute.assert_called_once()


async def test_find_by_isbn_not_found(repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await repo.find_by_isbn("000-0000000000")

    assert result is None


# ---------------------------------------------------------------------------
# find_by_filters
# ---------------------------------------------------------------------------

async def test_find_by_filters_returns_list(repo, mock_session, sample_book):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [sample_book]
    mock_session.execute.return_value = mock_result

    books = await repo.find_by_filters(title="Clean")

    assert books == [sample_book]
    mock_session.execute.assert_called_once()


async def test_find_by_filters_no_results(repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    books = await repo.find_by_filters(author="Unknown")

    assert books == []


async def test_find_by_filters_applies_limit_offset(repo, mock_session, sample_book):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [sample_book]
    mock_session.execute.return_value = mock_result

    books = await repo.find_by_filters(limit=5, offset=10)

    assert books == [sample_book]


# ---------------------------------------------------------------------------
# count_by_filters
# ---------------------------------------------------------------------------

async def test_count_by_filters_returns_integer(repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = 7
    mock_session.execute.return_value = mock_result

    count = await repo.count_by_filters(genre="Programming")

    assert count == 7


async def test_count_by_filters_zero(repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = 0
    mock_session.execute.return_value = mock_result

    count = await repo.count_by_filters(year=1800)

    assert count == 0


# ---------------------------------------------------------------------------
# Base: get_by_id / delete
# ---------------------------------------------------------------------------

async def test_get_by_id_returns_book(repo, mock_session, sample_book):
    mock_session.get.return_value = sample_book

    result = await repo.get_by_id(sample_book.book_id)

    assert result is sample_book


async def test_get_by_id_not_found(repo, mock_session):
    mock_session.get.return_value = None

    result = await repo.get_by_id(uuid.uuid4())

    assert result is None


async def test_delete_returns_true_when_found(repo, mock_session, sample_book):
    mock_session.get.return_value = sample_book

    deleted = await repo.delete(sample_book.book_id)

    assert deleted is True
    mock_session.delete.assert_called_once_with(sample_book)
    mock_session.commit.assert_called_once()


async def test_delete_returns_false_when_not_found(repo, mock_session):
    mock_session.get.return_value = None

    deleted = await repo.delete(uuid.uuid4())

    assert deleted is False
    mock_session.delete.assert_not_called()
