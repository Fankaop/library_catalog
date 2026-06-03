from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from uuid import UUID


class AppException(Exception):
    """Базовое исключение приложения, содержащее HTTP-статус и сообщение об ошибке."""

    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class NotFoundException(AppException):
    """Выбрасывается, когда запрашиваемый ресурс не найден (HTTP 404)."""

    def __init__(self, resource: str, identifier: int | str | UUID):
        super().__init__(
            message=f'{resource} with id {identifier} not found',
            status_code=404
        )

class UnauthorizedException(AppException):
    def __init__(self, message: str = 'Not auth'):
        super().__init__(message, status_code=401)

class ForbiddenException(AppException):
    def __init__(self, message: str = 'Not enough permissions'):
        super().__init__(message, status_code=403)

def register_exception_handlers(app: FastAPI) -> None:
    """Зарегистрировать обработчики исключений."""
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )
