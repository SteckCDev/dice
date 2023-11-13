from typing import Any

from core.states.mode import Mode
from core.base_handler import BaseHandler
from services import (
    PVBService,
    UserService,
)
from templates import Markups, Messages


class PrivateDiceHandler(BaseHandler):
    def __init__(self, user_id: int, forwarded_from: Any, user_dice: int):
        super().__init__()

        self.direct = forwarded_from is None
        self.user_dice = user_dice

        self.user = UserService.get(user_id)
        self.user_cache = UserService.get_cache(user_id)

    def __pvb_send_menu(self) -> None:
        self._bot.send_message(
            self.user.tg_id,
            Messages.pvb(
                self.user.beta_balance if self.user_cache.beta_mode else self.user.balance,
                self.user_cache.beta_mode
            ),
            Markups.pvb
        )

    def __pvb(self) -> None:
        game = PVBService().finish_game(self.user, self.user_cache, self.user_dice)

        self.user = UserService.get(self.user.tg_id)
        self.user_cache = UserService.get_cache(self.user.tg_id)

        selected_balance = self.user.beta_balance if self.user_cache.beta_mode else self.user.balance

        self._bot.send_message(
            self.user.tg_id,
            Messages.pvb_result(
                game.beta_mode,
                selected_balance,
                game.player_won,
                game.id
            )
        )

        self._bot.send_message(
            self.user.tg_id,
            Messages.pvb_create(
                self.user_cache.pvb_bots_turn_first,
                self.user_cache.beta_mode,
                selected_balance,
                self.user_cache.pvb_bet
            ),
            Markups.pvb_create(self.user_cache.pvb_bots_turn_first)
        )

    def __pvp(self) -> None:
        pass

    def _prepare(self) -> bool:
        if not self.direct:
            self._bot.send_message(
                self.user.tg_id,
                Messages.pvb_non_direct
            )
            return False

        # every check below is for PVB mode, so skip now if it's PVP
        if self.user_cache.mode == Mode.PVP:
            return True

        if not self.user_cache.pvb_in_process:
            self.__pvb_send_menu()
            return False

        try:
            PVBService().game_validate(self.user, self.user_cache)
        except ValueError:
            self.__pvb_send_menu()
            return False

        return True

    def _process(self) -> None:
        match self.user_cache.mode:
            case Mode.PVB:
                self.__pvb()
            case Mode.PVP:
                self.__pvp()
            case _:
                self.__pvb_send_menu()
