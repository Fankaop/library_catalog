from abc import ABC, abstractmethod
import asyncio
import httpx
import logging


class BaseApiClient(ABC):

    """
    Базовый класс для HTTP клиентов внешних API.

    Включает:
    - Retry логику
    - Обработку ошибок
    - Логирование
    - Timeout management
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,  # секунды до таймаута одного запроса
        retries: int = 3,       # максимальное число попыток
        backoff: float = 0.5,   # базовая пауза между попытками (удваивается с каждой)
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self._client = httpx.AsyncClient(timeout=self.timeout)
        self.logger = logging.getLogger(self.client_name())

    @abstractmethod
    def client_name(self) -> str:
        """Имя клиента — используется как имя логгера."""
        ...

    def _build_url(self, path: str) -> str:
        """Собрать полный URL, гарантируя один слэш между base_url и path."""
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    async def _request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
        json: dict | None = None,
        headers: dict | None = None,
    ) -> dict:
        """
        Выполнить HTTP запрос с retry логикой.

        Raises:
            httpx.TimeoutException: если все попытки завершились таймаутом
            httpx.HTTPStatusError: при не-5xx ошибке или исчерпании попыток на 5xx
        """
        url = self._build_url(path)
        for attempt in range(self.retries):
            try:
                self.logger.debug(f"{method} {url} params={params}")

                response = await self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    headers=headers,
                )

                response.raise_for_status()
                return response.json()

            except httpx.TimeoutException:
                if attempt == self.retries - 1:
                    self.logger.error(f"Timeout after {self.retries} attempts")
                    raise

                wait_time = self.backoff * (2 ** attempt)
                self.logger.warning(f"Timeout, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < self.retries - 1:
                    wait_time = self.backoff * (2 ** attempt)
                    self.logger.warning(f"Server error {e.response.status_code}, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"HTTP error: {e}")
                    raise

        # Недостижимо при retries > 0, но нужно для корректного вывода типов
        raise RuntimeError(f"_request exhausted {self.retries} retries without result")

    async def _get(self, path: str, **kwargs) -> dict:
        """Выполнить GET запрос."""
        return await self._request("GET", path, **kwargs)

    async def close(self) -> None:
        """Закрыть HTTP клиент и освободить соединения."""
        await self._client.aclose()