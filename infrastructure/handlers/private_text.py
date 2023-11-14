from infrastructure.base_handler import BaseHandler
from core.types.mode import Mode
from infrastructure.handlers.lottery import LotteryHandler
from infrastructure.handlers.profile import ProfileHandler
from infrastructure.handlers.support import SupportHandler
from services import (
    AccessService,
    ConfigService,
    UserService,
)
from templates import (
    Markups,
    Menu,
    Messages,
)


class PrivateTextHandler(BaseHandler):
    def __init__(self, user_id: int, text: str):
        super().__init__()

        self.text = text

        self.user = UserService.get(user_id)
        self.user_cache = UserService.get_cache(user_id)

        self.__config = ConfigService().get()

    def __set_bet(self) -> None:
        bet = int(self.text)

        if bet < self.__config.min_bet or bet > self.__config.max_bet:
            self._bot.send_message(
                self.user.tg_id,
                Messages.bet_out_of_limits(
                    self.__config.min_bet,
                    self.__config.max_bet
                )
            )
            return

        selected_balance = self.user.beta_balance if self.user_cache.beta_mode else self.user.balance

        if bet > selected_balance:
            self._bot.send_message(
                self.user.tg_id,
                Messages.balance_not_enough
            )
            return

        if self.user_cache.mode == Mode.PVB:
            self.user_cache.pvb_bet = bet
            UserService.update_cache(self.user.tg_id, self.user_cache)

            self._bot.edit_message(
                self.user.tg_id,
                self.user_cache.last_message_id,
                Messages.pvb_create(
                    self.user_cache.pvb_bots_turn_first,
                    self.user_cache.beta_mode,
                    self.user.beta_balance if self.user_cache.beta_mode else self.user.balance,
                    self.user_cache.pvb_bet
                ),
                Markups.pvb_create(self.user_cache.pvb_bots_turn_first)
            )
        else:
            self.user_cache.pvp_bet = bet
            UserService.update_cache(self.user.tg_id, self.user_cache)

    def _prepare(self) -> bool:
        if not AccessService.subscriptions(self.user.tg_id):
            self._bot.send_message(
                self.user.tg_id,
                Messages.force_to_subscribe
            )
            return False

        if self.user_cache.pvb_in_process:
            self._bot.send_message(
                self.user.tg_id,
                Messages.pvb_in_process
            )
            return False

        return True

    def _process(self) -> None:
        match self.text:
            case Menu.GAMES:
                self._bot.send_message(
                    self.user.tg_id,
                    Messages.games(self.user.balance),
                    Markups.games
                )
            case Menu.PROFILE:
                ProfileHandler(self.user.tg_id).handle()
            case Menu.LOTTERY:
                LotteryHandler(self.user.tg_id).handle()
            case Menu.SUPPORT:
                SupportHandler(self.user.tg_id).handle()

        if self.text.isdigit():
            self.__set_bet()
