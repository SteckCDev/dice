from infrastructure.api_services.telebot import BaseTeleBotHandler
from infrastructure.cache.redis import RedisInterface, redis_instance
from settings import settings
from templates import Messages


class ClearAllCacheHandler(BaseTeleBotHandler):
    def __init__(self, user_id: int) -> None:
        super().__init__()

        self.user_id: int = user_id

        self.__redis: RedisInterface = redis_instance

    def _prepare(self) -> bool:
        return self.user_id == settings.admin_tg_id

    def _process(self) -> None:
        self.__redis.flush_all()

        self._bot.send_message(
            settings.admin_tg_id,
            Messages.admin_all_cache_cleared()
        )
