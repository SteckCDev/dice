import json

from redis import Redis

from settings import settings
from .database import RedisDatabase


class RedisInterface:
    # noinspection PyNoneFunctionAssignment
    def __init__(self, database: RedisDatabase = RedisDatabase.APP):
        # wrong type hint in redis library: Redis.from_url() returns type Redis, not None
        # noinspection PyTypeChecker
        self.__client: Redis = Redis.from_url(settings.redis_dsn, db=database)

    def set(self, key: str, value: str) -> None:
        self.__client.set(key, value)

    def get(self, key: str) -> str | None:
        return self.__client.get(key)

    def set_bool(self, key: str, value: bool) -> None:
        self.__client.set(key, int(value))

    def get_bool(self, key: str) -> bool | None:
        value = self.__client.get(key)

        if value is None:
            return

        return bool(int(value))

    def set_json(self, key: str, value: str, nx: bool = False) -> None:
        self.__client.set(key, value, nx=nx)

    def get_json(self, key: str) -> dict | None:
        value: str | None = self.__client.get(key)

        return json.loads(value) if value else None

    def scan_match(self, pattern: str) -> int:
        return len(self.__client.scan(match=pattern)[1])
