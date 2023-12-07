from core.services import (
    ConfigService,
    PVBService,
    UserService,
)
from infrastructure.api_services.telebot import BaseTeleBotHandler
from infrastructure.repositories import (
    RedisConfigRepository,
    PostgresRedisPVBRepository,
    PostgresRedisUserRepository,
)
from settings import settings
from templates import Markups, Messages


class AdminHandler(BaseTeleBotHandler):
    def __init__(self) -> None:
        super().__init__()

        config_service: ConfigService = ConfigService(
            repository=RedisConfigRepository()
        )
        self.__user_service: UserService = UserService(
            repository=PostgresRedisUserRepository(),
            bot=self._bot,
            config_service=config_service
        )
        self.__pvb_service: PVBService = PVBService(
            repository=PostgresRedisPVBRepository(),
            bot=self._bot,
            config_service=config_service,
            user_service=self.__user_service
        )

    def _prepare(self) -> bool:
        return True

    def _process(self) -> None:
        self._bot.send_message(
            settings.admin_tg_id,
            Messages.admin(
                self.__user_service.get_cached_users_count()
            ),
            Markups.admin(
                self.__pvb_service.get_status(),
                False,
                False,
                False,
                False
            )
        )
