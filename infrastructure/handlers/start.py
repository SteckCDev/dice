from core.schemas.user import CreateUserDTO
from core.services import (
    ConfigService,
    UserService,
)
from infrastructure.api_services.telebot_handler import BaseTeleBotHandler
from infrastructure.repositories import (
    MockConfigRepository,
    PostgresRedisUserRepository,
)
from templates import Markups, Messages


class StartHandler(BaseTeleBotHandler):
    def __init__(
            self,
            chat_id: int,
            user_id: int,
            user_name: str
    ) -> None:
        super().__init__()

        self.chat_id = chat_id
        self.user_id = user_id
        self.user_name = user_name

        self.__config_service = ConfigService(
            repository=MockConfigRepository()
        )
        self.__user_service = UserService(
            repository=PostgresRedisUserRepository(),
            bot=self._bot,
            config_service=self.__config_service
        )

    def _prepare(self) -> bool:
        """Because start command is the entry point for new users got to create user if it doesn't already exist"""

        config = self.__config_service.get()

        self.__user_service.get_or_create(
            CreateUserDTO(
                tg_id=self.user_id,
                tg_name=self.user_name,
                balance=config.start_balance,
                beta_balance=config.start_beta_balance
            )
        )

        return True

    def _process(self) -> None:
        self._bot.send_message(
            self.chat_id,
            Messages.start,
            Markups.navigation
        )
