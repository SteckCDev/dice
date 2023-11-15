from core.services import (
    ConfigService,
    UserService,
)
from infrastructure.api_services.telebot_handler import BaseTeleBotHandler
from infrastructure.repositories import (
    MockConfigRepository,
    PostgresRedisUserRepository,
)
from templates import Messages


class BalanceHandler(BaseTeleBotHandler):
    def __init__(self, chat_id: int, user_id: int) -> None:
        super().__init__()

        self.chat_id = chat_id

        config_service = ConfigService(
            repository=MockConfigRepository()
        )
        self.__user_service = UserService(
            repository=PostgresRedisUserRepository(),
            bot=self._bot,
            config_service=config_service
        )

        self.user = self.__user_service.get_by_tg_id(user_id)

    def _prepare(self) -> bool:
        return True

    def _process(self) -> None:
        self._bot.send_message(
            self.chat_id,
            Messages.balance(self.user.balance, self.user.beta_balance)
        )
