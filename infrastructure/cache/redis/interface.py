from json import JSONDecoder
from typing import Any

from redis import Redis
from redis.commands.json.path import Path

from settings import settings
from .database import RedisDatabase


class RedisInterface:
    def __init__(self, database: RedisDatabase = RedisDatabase.APP):
        # wrong type hint in redis library: Redis.from_url() returns type Redis, not None
        self.__client: Redis = Redis.from_url(settings.redis_dsn, db=database)
        self.__json_decoder = JSONDecoder()

    def set_bool(self, key: str, value: bool) -> None:
        self.__client.set(key, int(value))

    def get_bool(self, key: str) -> bool | None:
        value = self.__client.get(key)

        if value is None:
            return

        return bool(int(value))

    def add_one_to_set(self, key: str, value: Any) -> None:
        self.__client.sadd(key, value)

    def get_len_of_set(self, key: str) -> int:
        return self.__client.scard(key)

    def set_json(self, key: str, value: str, nx: bool = False) -> None:
        self.__client.json().set(key, Path.root_path(), value, nx=nx)

    def get_json(self, key: str) -> Any:
        json_encoded = self.__client.json().get(key)

        return self.__json_decoder.decode(json_encoded)

    def scan_match(self, pattern: str) -> int:
        return self.__client.scan(match=pattern)