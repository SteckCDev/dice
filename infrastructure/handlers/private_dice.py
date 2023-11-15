from typing import Any

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
from templates import Markups, Messages


class PrivateDiceHandler(BaseTeleBotHandler):
    def __init__(self, user_id: int, forwarded_from: Any, user_dice: int) -> None:
        super().__init__()

        self.is_direct = forwarded_from is None
        self.user_dice = user_dice

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

        self.user = self.__user_service.get_by_tg_id(user_id)
        self.user_cache = self.__user_service.get_cache_by_tg_id(user_id)

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
        game = self.__pvb_service.finish_game(self.user, self.user_cache, self.user_dice)

        selected_balance = self.__user_service.get_user_selected_balance(self.user.tg_id)

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
        if not self.is_direct:
            self._bot.send_message(
                self.user.tg_id,
                Messages.pvb_non_direct
            )
            return False

        # check below is for PVB mode, so skip now if it's PVP
        if self.user_cache.mode == GameMode.PVP:
            return True

        if not self.user_cache.pvb_in_process:
            self.__pvb_send_menu()
            return False

        return True

    def _process(self) -> None:
        match self.user_cache.mode:
            case GameMode.PVB:
                self.__pvb()
            case GameMode.PVP:
                self.__pvp()
            case _:
                self.__pvb_send_menu()
