from uuid import UUID
from ..core.exceptions import AppException, NotFoundException

class BookNotFoundException(NotFoundException):
    """Книга с указанным UUID не найдена в базе данных. Возвращает 404."""
    def __init__(self, book_id: UUID):
        super().__init__(resource='Book', identifier=book_id)


class BookAlreadyExistsException(AppException):
    """Книга с таким ISBN уже существует. Возвращает 409 Conflict."""
    def __init__(self, isbn: str):
        super().__init__(
            message=f'Book with ISBN {isbn} already exists',
            status_code=409,
        )

class InvalidYearException(AppException):
    """Год издания вне допустимого диапазона (1000 — текущий год). Возвращает 400."""
    def __init__(self, year: int):
        from datetime import datetime
        current_year = datetime.now().year
        super().__init__(
            message=f'Year {year} is invalid (must be 1000-{current_year})',
            status_code=400,
        )

class InvalidPagesException(AppException):
    """Количество страниц не положительное число. Возвращает 400."""
    def __init__(self, pages: int):
        super().__init__(
            message=f'Pages count must be positive, got {pages}',
            status_code=400,
        )

class OpenLibraryException(AppException):
    """Внешний сервис Open Library вернул ошибку. Возвращает 503 Service Unavailable."""
    def __init__(self, message: str):
        super().__init__(
            message=f'Open Library API error: {message}',
            status_code=503,
        )

class OpenLibraryTimeoutException(AppException):
    """Внешний сервис Open Library не ответил за отведённое время. Возвращает 504 Gateway Timeout."""
    def __init__(self, timeout: float):
        super().__init__(
            message=f'Open Library API timeout after {timeout}s',
            status_code=504,
        )
