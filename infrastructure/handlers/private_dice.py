import html
from typing import Any

from core.exceptions import (
    PVPNotFoundForUserError,
)
from core.schemas.config import (
    ConfigDTO,
)
from core.schemas.pvb import (
    PVBDTO,
)
from core.schemas.pvp import (
    PVPDetailsDTO,
)
from core.schemas.user import (
    UserDTO,
    CreateUserDTO,
    UserCacheDTO
)
from core.services import (
    ConfigService,
    PVBService,
    PVPService,
    UserService,
)
from core.states import PVPStatus
from infrastructure.api_services.telebot import BaseTeleBotHandler
from infrastructure.repositories import (
    ImplementedConfigRepository,
    ImplementedPVBRepository,
    ImplementedPVPRepository,
    ImplementedUserRepository,
)
from templates import Markups, Messages


class PrivateDiceHandler(BaseTeleBotHandler):
    def __init__(self, user_id: int, user_name: str, forwarded_from: Any, user_dice: int) -> None:
        super().__init__()

        self.is_direct: bool = forwarded_from is None
        self.user_dice: int = user_dice

        config_service: ConfigService = ConfigService(
            repository=ImplementedConfigRepository()
        )
        self.__user_service: UserService = UserService(
            repository=ImplementedUserRepository(),
            bot=self._bot,
            config_service=config_service
        )
        self.__pvb_service: PVBService = PVBService(
            repository=ImplementedPVBRepository(),
            bot=self._bot,
            config_service=config_service,
            user_service=self.__user_service
        )
        self.__pvp_service: PVPService = PVPService(
            repository=ImplementedPVPRepository(),
            bot=self._bot,
            config_service=config_service,
            user_service=self.__user_service
        )

        self.config: ConfigDTO = config_service.get()

        self.user: UserDTO = self.__user_service.get_or_create(
            CreateUserDTO(
                tg_id=user_id,
                tg_name=html.escape(user_name),
                balance=self.config.start_balance,
                beta_balance=self.config.start_beta_balance
            )
        )
        self.user_cache: UserCacheDTO = self.__user_service.get_cache_by_tg_id(user_id)

        self.__pvp_in_process: bool = self.__pvp_service.get_last_for_tg_id_and_status(
            self.user.tg_id, PVPStatus.STARTED
        ) is not None

    def __send_games_menu(self) -> None:
        self._bot.send_message(
            self.user.tg_id,
            Messages.games(
                self.__user_service.get_user_selected_balance(self.user.tg_id),
                self.user_cache.beta_mode
            ),
            Markups.games()
        )

    def __pvb(self) -> None:
        game: PVBDTO = self.__pvb_service.finish_game(self.user, self.user_cache, self.user_dice)

        selected_balance: int = self.__user_service.get_user_selected_balance(self.user.tg_id)

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
                self.user_cache.pvb_bet,
                self.config.min_bet,
                self.config.max_bet
            ),
            Markups.pvb_create(self.user_cache.pvb_bots_turn_first)
        )

    def __pvp(self) -> None:
        try:
            self.__pvp_service.finish_game(self.user, self.user_dice)
        except PVPNotFoundForUserError:
            pass
        except ValueError as exc:
            self._bot.send_message(
                self.user.tg_id,
                str(exc)
            )
            return
        else:
            return

        if self.user_cache.pvp_game_id is None:
            self.__send_games_menu()
            return

        try:
            pvp_details: PVPDetailsDTO = self.__pvp_service.join_game(self.user, self.user_cache, self.user_dice)
        except ValueError as exc:
            self._bot.send_message(
                self.user.tg_id,
                str(exc)
            )
            return
        else:
            self._bot.send_message(
                self.user.tg_id,
                Messages.pvp_join(
                    pvp_details.id,
                    pvp_details.beta_mode
                )
            )

            self._bot.send_message(
                pvp_details.creator_tg_id,
                Messages.pvp_started(
                    pvp_details.id,
                    pvp_details.beta_mode,
                    pvp_details.bet,
                    self.user.tg_name
                )
            )

    def _prepare(self) -> bool:
        if not self.is_direct:
            self._bot.send_message(
                self.user.tg_id,
                Messages.dice_not_direct()
            )
            return False

        return True

    def _process(self) -> None:
        if self.user_cache.pvb_in_process:
            self.__pvb()
        elif self.__pvp_in_process or self.user_cache.pvp_game_id:
            self.__pvp()
        else:
            self.__send_games_menu()
