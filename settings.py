from os.path import isfile
from typing import Final

from pydantic_settings import BaseSettings


ENV_DEVELOPMENT: Final[str] = ".dev.env"
ENV_PRODUCTION: Final[str] = ".env"


class Settings(BaseSettings):
    class Config:
        env_file: str = ENV_PRODUCTION if isfile(ENV_PRODUCTION) else ENV_DEVELOPMENT

    postgres_host: str
    postgres_port: str
    postgres_user: str
    postgres_password: str
    postgres_database: str

    redis_host: str
    redis_port: str
    redis_user: str | None = None
    redis_password: str | None = None

    bot_token: str
    max_threads: int
    admin_tg_id: int

    bot_url: str
    pvpc_url: str
    lottery_url: str
    support_url: str

    @property
    def postgres_dsn(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@" \
               f"{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"

    @property
    def redis_dsn(self) -> str:
        if self.redis_user and self.redis_password:
            return f"redis://{self.redis_user}:{self.redis_password}@{self.redis_host}:{self.redis_port}"
        else:
            return f"redis://{self.redis_host}:{self.redis_port}"


settings: Settings = Settings()
