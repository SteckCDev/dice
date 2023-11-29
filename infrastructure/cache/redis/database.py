from enum import Enum, unique


@unique
class RedisDatabase(int, Enum):
    APP: int = 0
    CELERY: int = 1
