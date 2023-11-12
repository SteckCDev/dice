from os.path import isfile

from pydantic_settings import BaseSettings


ENV_DEVELOPMENT = ".dev.env"
ENV_PRODUCTION = ".env"


class Settings(BaseSettings):
    class Config:
        env_file = ENV_DEVELOPMENT if isfile(ENV_DEVELOPMENT) else ENV_PRODUCTION

    postgres_host: str
    postgres_port: str
    postgres_user: str
    postgres_password: str
    postgres_database: str

    redis_host: str
    redis_port: str

    bot_token: str
    admin_tg_id: int

    bot_url: str
    pvpc_url: str
    lottery_url: str
    support_url: str

    @property
    def postgres_dsn(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@" \
               f"{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"


settings = Settings()
