from core.repositories import PVPFRepository
from infrastructure.cache.redis import RedisKey, RedisInterface, redis_instance


class RedisPVPFRepository(PVPFRepository):
    def __init__(self) -> None:
        self.__redis: RedisInterface = redis_instance

    def toggle(self) -> bool:
        cached_state: bool | None = self.__redis.get_bool(RedisKey.PVPF_ACTIVE)
        state: bool = False if cached_state is None else not cached_state

        self.__redis.set_bool(RedisKey.PVPF_ACTIVE, state)

        return state

    def get_status(self) -> bool:
        state: bool | None = self.__redis.get_bool(RedisKey.PVPF_ACTIVE)

        if state is None:
            self.__redis.set_bool(RedisKey.PVPF_ACTIVE, False)
            return False

        return state
