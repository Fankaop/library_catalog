

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