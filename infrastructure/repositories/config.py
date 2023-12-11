from core.repositories import ConfigRepository
from core.schemas.config import Config, ConfigDTO
from infrastructure.cache.redis import RedisKey, RedisInterface, redis_instance


class RedisConfigRepository(ConfigRepository):
    def __init__(self):
        self.__redis: RedisInterface = redis_instance

    def __init_config(self) -> ConfigDTO:
        dto: ConfigDTO = ConfigDTO(
            **Config().model_dump()
        )

        self.__redis.set_json(
            RedisKey.CONFIG,
            dto.model_dump_json(),
            nx=True
        )

        return dto

    def get(self) -> ConfigDTO:
        config: dict | None = self.__redis.get_json(RedisKey.CONFIG)

        return ConfigDTO(**config) if config else self.__init_config()

    def update(self, dto: ConfigDTO) -> None:
        self.__redis.set_json(
            RedisKey.CONFIG,
            dto.model_dump_json()
        )
