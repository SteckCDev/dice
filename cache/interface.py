from typing import Any
from json import JSONDecoder

from redis import Redis
from redis.commands.json.path import Path

from settings import settings


class RedisInterface:
    def __init__(self):
        self.__client: Redis = Redis(
            host=settings.redis_host,
            port=settings.redis_port
        )
        self.__json_decoder = JSONDecoder()

    def set_bool(self, key: str, value: bool) -> None:
        self.__client.set(key, int(value))

    def get_bool(self, key: str) -> bool:
        return bool(int(self.__client.get(key)))

    def add_one_to_set(self, key: str, value: Any) -> None:
        self.__client.sadd(key, value)

    def get_len_of_set(self, key: str) -> int:
        return self.__client.scard(key)

    def set_json(self, key: str, value: str, nx: bool = False) -> None:
        self.__client.json().set(key, Path.root_path(), value, nx=nx)

    def get_json(self, key: str) -> Any:
        json_encoded = self.__client.json().get(key)
        return self.__json_decoder.decode(json_encoded)
