from core.services import (
    ConfigService,
    PVBService,
    UserService,
)
from core.types.game_mode import GameMode
from infrastructure.api_services.telebot_handler import BaseTeleBotHandler
from infrastructure.repositories import (
    MockConfigRepository,
    PostgresRedisPVBRepository,
    PostgresRedisUserRepository,
)
from settings import settings
from templates import Markups, Messages


class CallbackHandler(BaseTeleBotHandler):
    def __init__(self, call_id: int, path: str, chat_id: int, message_id: int, user_id: int) -> None:
        super().__init__()

        self.call_id = call_id
        self.path = path
        self.chat_id = chat_id
        self.message_id = message_id

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

        self.config = config_service.get()
        self.user = self.__user_service.get_by_tg_id(user_id)
        self.user_cache = self.__user_service.get_cache_by_tg_id(user_id)

    def _prepare(self) -> bool:
        if not self.__user_service.is_subscribed_to_chats(self.user.tg_id):
            self._bot.send_message(
                self.chat_id,
                Messages.force_to_subscribe
            )
            return False

        if self.user_cache.pvb_in_process:
            self._bot.send_message(
                self.chat_id,
                Messages.pvb_in_process
            )
            return False

        if "admin" in self.path and self.user.tg_id != settings.admin_tg_id:
            return False

        return True
        
    def _process(self) -> None:
        if self.path.startswith("pvb"):
            self.user_cache.mode = GameMode.PVB
            self.__user_service.update_cache(self.user_cache)
        elif self.path.startswith("pvp"):
            self.user_cache.mode = GameMode.PVP
            self.__user_service.update_cache(self.user_cache)

        if self.path == "terms-accept":
            self.__user_service.agree_with_terms_and_conditions(self.user.tg_id)

            self._bot.edit_message(
                self.chat_id,
                self.message_id,
                Messages.terms_accepted()
            )

        elif self.path == "terms-reject":
            self._bot.edit_message(
                self.chat_id,
                self.message_id,
                Messages.terms_rejected()
            )

        elif self.path == "switch-beta":
            self.user_cache.beta_mode = not self.user_cache.beta_mode

            self.__user_service.update_cache(self.user_cache)

            self._bot.edit_message(
                self.chat_id,
                self.message_id,
                Messages.profile(
                    self.user.tg_name,
                    self.user.balance,
                    self.user.beta_balance,
                    self.user.joined_at,
                    0
                ),
                Markups.profile(self.user_cache.beta_mode)
            )

        elif self.path == "pvb":
            self._bot.edit_message(
                self.chat_id,
                self.message_id,
                Messages.pvb(
                    self.user.beta_balance if self.user_cache.beta_mode else self.user.balance,
                    self.user_cache.beta_mode
                ),
                Markups.pvb
            )

        elif self.path == "pvb-create":
            self._bot.edit_message(
                self.chat_id,
                self.message_id,
                Messages.pvb_create(
                    self.user_cache.pvb_bots_turn_first,
                    self.user_cache.beta_mode,
                    self.user.beta_balance if self.user_cache.beta_mode else self.user.balance,
                    self.user_cache.pvb_bet
                ),
                Markups.pvb_create(self.user_cache.pvb_bots_turn_first)
            )

            self.user_cache.last_message_id = self.message_id
            self.__user_service.update_cache(self.user_cache)

        elif self.path == "pvb-switch-turn":
            self.user_cache.pvb_bots_turn_first = not self.user_cache.pvb_bots_turn_first
            self.__user_service.update_cache(self.user_cache)

            self._bot.edit_message(
                self.chat_id,
                self.message_id,
                Messages.pvb_create(
                    self.user_cache.pvb_bots_turn_first,
                    self.user_cache.beta_mode,
                    self.user.beta_balance if self.user_cache.beta_mode else self.user.balance,
                    self.user_cache.pvb_bet
                ),
                Markups.pvb_create(self.user_cache.pvb_bots_turn_first)
            )

        elif self.path == "pvb-start":
            try:
                self.__pvb_service.start_game(self.user_cache)
            except ValueError as exc:
                self._bot.answer_callback(
                    self.call_id,
                    f"Ошибка: {exc}"
                )

        elif self.path == "pvb-history":
            pass

        elif self.path == "pvb-instruction":
            self._bot.edit_message(
                self.chat_id,
                self.message_id,
                Messages.pvb_instruction,
                Markups.back_to("pvb")
            )

        elif self.path == "admin-switch-pvb":
            self.__pvb_service.toggle()

        # elif self.path == "admin-switch-pvp":
        #     self.__pvp_service.toggle()
        #
        # elif self.path == "admin-switch-pvpc":
        #     self.__pvpc_service.toggle()
        #
        # elif self.path == "admin-switch-pvpf":
        #     self.__pvpf_service.toggle()
        #
        # elif self.path == "admin-switch-transactions":
        #     self.__transactions_service.toggle()

        if self.path.startswith("admin-switch"):
            self._bot.edit_message(
                settings.admin_tg_id,
                self.message_id,
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

        # stop loading animation in telegram interface if this handler did no action
        self._bot.answer_callback(self.call_id, "")
