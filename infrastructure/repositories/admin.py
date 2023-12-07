from core.repositories import AdminRepository
from infrastructure.cache.redis import RedisKey, RedisInterface, redis_instance


class RedisAdminRepository(AdminRepository):
    def __init__(self):
        self.__redis: RedisInterface = redis_instance

    def set_mailing_text(self, text: str) -> None:
        self.__redis.set(RedisKey.MAILING_TEXT, text)

    def get_mailing_text(self) -> str | None:
        return self.__redis.get(RedisKey.MAILING_TEXT)
