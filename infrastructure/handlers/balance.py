import html

from core.schemas.config import (
    ConfigDTO
)
from core.schemas.user import (
    UserDTO,
    CreateUserDTO,
)
from core.services import (
    ConfigService,
    UserService,
)
from infrastructure.api_services.telebot import BaseTeleBotHandler
from infrastructure.repositories import (
    ImplementedConfigRepository,
    ImplementedUserRepository,
)
from templates import Messages


class BalanceHandler(BaseTeleBotHandler):
    def __init__(self, chat_id: int, user_id: int, user_name: str) -> None:
        super().__init__()

        self.chat_id: int = chat_id

        config_service: ConfigService = ConfigService(
            repository=ImplementedConfigRepository()
        )
        self.__user_service: UserService = UserService(
            repository=ImplementedUserRepository(),
            bot=self._bot,
            config_service=config_service
        )

        config: ConfigDTO = config_service.get()

        self.user: UserDTO = self.__user_service.get_or_create(
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
            Messages.balance(self.user.balance, self.user.beta_balance)
        )
