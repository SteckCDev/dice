import html

from core.schemas.user import CreateUserDTO
from core.services import (
    ConfigService,
    UserService,
)
from infrastructure.api_services.telebot import BaseTeleBotHandler
from infrastructure.repositories import (
    RedisConfigRepository,
    PostgresRedisUserRepository,
)
from templates import Markups, Messages


class StartHandler(BaseTeleBotHandler):
    def __init__(self, chat_id: int, user_id: int, user_name: str) -> None:
        super().__init__()

        self.chat_id: int = chat_id

        self.__config_service: ConfigService = ConfigService(
            repository=RedisConfigRepository()
        )
        self.__user_service: UserService = UserService(
            repository=PostgresRedisUserRepository(),
            bot=self._bot,
            config_service=self.__config_service
        )

        config = self.__config_service.get()

        self.__user_service.get_or_create(
            CreateUserDTO(
                tg_id=user_id,
                tg_name=html.escape(user_name),
                balance=config.start_balance,
                beta_balance=config.start_beta_balance
            )
        )

    def _prepare(self) -> bool:
        return True

    def _process(self) -> None:
        self._bot.send_message(
            self.chat_id,
            Messages.start(),
            Markups.navigation()
        )
