from functools import lru_cache
from typing import Literal
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = 'Library Catalog API'
    environment: Literal["development", "staging", "production"]
    database_url: PostgresDsn
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    database_pool_size: int = 20
    debug: bool = True


    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=False
    )
    @property
    def is_production(self) -> bool:
        return self.environment == 'production'

@lru_cache
def get_settings() -> Settings:# -> Any:# -> Any:# -> Any:
    return Settings() # type: ignore

settings = get_settings()
