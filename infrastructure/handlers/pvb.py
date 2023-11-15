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


class PVBHandler(BaseTeleBotHandler):
    def __init__(
            self,
            chat_id: int,
            message_id: int,
            user_id: int
    ) -> None:
        super().__init__()

        self.chat_id = chat_id
        self.message_id = message_id
        self.user_id = user_id

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

        self.user_cache = self.__user_service.get_cache_by_tg_id(user_id)

    def _prepare(self) -> bool:
        if not self.__user_service.is_subscribed_to_chats(self.user_id):
            self._bot.send_message(
                self.chat_id,
                Messages.force_to_subscribe
            )
            return False

        if not self.__user_service.is_terms_and_conditions_agreed(self.user_id):
            self._bot.send_message(
                self.chat_id,
                Messages.terms_and_conditions,
                Markups.terms_and_conditions
            )
            return False

        if self.user_cache.pvb_in_process:
            self._bot.send_message(
                self.chat_id,
                Messages.pvb_in_process
            )
            return False

        if not self.__pvb_service.get_status():
            self._bot.send_message(
                self.chat_id,
                Messages.game_mode_disabled
            )
            return False

        return True

    def _process(self) -> None:
        self._bot.send_message(
            self.chat_id,
            Messages.pvb(
                self.__user_service.get_user_selected_balance(self.user_id),
                self.user_cache.beta_mode
            ),
            Markups.pvb
        )
