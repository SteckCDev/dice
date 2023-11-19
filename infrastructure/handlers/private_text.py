from core.schemas.config import (
    ConfigDTO,
)
from core.schemas.user import (
    UserCacheDTO,
)
from core.services import (
    ConfigService,
    UserService,
)
from core.types.game_mode import GameMode
from infrastructure.api_services.telebot_handler import BaseTeleBotHandler
from infrastructure.handlers.lottery import LotteryHandler
from infrastructure.handlers.profile import ProfileHandler
from infrastructure.handlers.support import SupportHandler
from infrastructure.repositories import (
    MockConfigRepository,
    PostgresRedisUserRepository,
)
from templates import (
    Markups,
    Menu,
    Messages,
)


class PrivateTextHandler(BaseTeleBotHandler):
    def __init__(self, text: str, user_id: int, user_name: str) -> None:
        super().__init__()

        self.text: str = text
        self.user_id: int = user_id
        self.user_name: str = user_name

        config_service: ConfigService = ConfigService(
            repository=MockConfigRepository()
        )
        self.__user_service: UserService = UserService(
            repository=PostgresRedisUserRepository(),
            bot=self._bot,
            config_service=config_service
        )

        self.config: ConfigDTO = config_service.get()
        self.user_cache: UserCacheDTO = self.__user_service.get_cache_by_tg_id(user_id)

    def __set_bet(self) -> None:
        bet: int = int(self.text)

        if bet < self.config.min_bet or bet > self.config.max_bet:
            self._bot.send_message(
                self.user_id,
                Messages.bet_out_of_limits(
                    self.config.min_bet,
                    self.config.max_bet
                )
            )
            return

        if bet > self.__user_service.get_user_selected_balance(self.user_id):
            self._bot.send_message(
                self.user_id,
                Messages.balance_is_not_enough
            )
            return

        if self.user_cache.game_mode == GameMode.PVB:
            self.user_cache.pvb_bet = bet

            self._bot.edit_message(
                self.user_id,
                self.user_cache.last_message_id,
                Messages.pvb_create(
                    self.user_cache.pvb_bots_turn_first,
                    self.user_cache.beta_mode,
                    self.__user_service.get_user_selected_balance(self.user_id),
                    self.user_cache.pvb_bet
                ),
                Markups.pvb_create(self.user_cache.pvb_bots_turn_first)
            )
        else:
            self.user_cache.pvp_bet = bet

        self.__user_service.update_cache(self.user_cache)

    def _prepare(self) -> bool:
        if not self.__user_service.is_subscribed_to_chats(self.user_id):
            self._bot.send_message(
                self.user_id,
                Messages.force_to_subscribe
            )
            return False

        if self.user_cache.pvb_in_process:
            self._bot.send_message(
                self.user_id,
                Messages.pvb_in_process
            )
            return False

        return True

    def _process(self) -> None:
        match self.text:
            case Menu.GAMES:
                self._bot.send_message(
                    self.user_id,
                    Messages.games(
                        self.__user_service.get_user_selected_balance(self.user_id),
                        self.user_cache.beta_mode
                    ),
                    Markups.games
                )
            case Menu.PROFILE:
                ProfileHandler(self.user_id, self.user_name).handle()
            case Menu.LOTTERY:
                LotteryHandler(self.user_id).handle()
            case Menu.SUPPORT:
                SupportHandler(self.user_id).handle()

        if self.text.isdigit():
            self.__set_bet()
