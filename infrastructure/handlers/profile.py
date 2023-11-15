from core.services import (
    ConfigService,
    PVBService,
    UserService,
)
from infrastructure.api_services.telebot_handler import BaseTeleBotHandler
from infrastructure.repositories import (
    MockConfigRepository,
    PostgresRedisPVBRepository,
    PostgresRedisUserRepository,
)
from templates import Markups, Messages


class ProfileHandler(BaseTeleBotHandler):
    def __init__(self, chat_id: int) -> None:
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
        self.__pvb_service = PVBService(
            repository=PostgresRedisPVBRepository(),
            bot=self._bot,
            config_service=config_service,
            user_service=self.__user_service
        )

        self.user = self.__user_service.get_by_tg_id(chat_id)
        self.user_cache = self.__user_service.get_cache_by_tg_id(chat_id)

    def _prepare(self) -> bool:
        if self.user_cache.pvb_in_process:
            self._bot.send_message(
                self.chat_id,
                Messages.pvb_in_process
            )
            return False

        return True

    def _process(self) -> None:
        self._bot.send_message(
            self.chat_id,
            Messages.profile(
                self.user.tg_name,
                self.user.balance,
                self.user.beta_balance,
                self.user.joined_at,
                self.__pvb_service.get_count_for_tg_id(self.user.tg_id)
            ),
            Markups.profile(
                self.user_cache.beta_mode
            )
        )
