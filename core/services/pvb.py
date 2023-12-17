import math
import time
from typing import Final

from core.abstract_bot import AbstractBotAPI
from core.exceptions import (
    BetOutOfLimitsError,
    BalanceIsNotEnoughError,
)
from core.repositories import PVBRepository
from core.schemas.config import (
    ConfigDTO,
)
from core.schemas.pvb import (
    PVBDTO,
    CreatePVBDTO,
)
from core.schemas.user import (
    UserDTO,
    UpdateUserDTO,
    UserCacheDTO,
)
from templates.messages import Messages
from .config import ConfigService
from .user import UserService


DICE_SPIN_ANIMATION_DURATION: Final[int] = 3


class PVBService:
    def __init__(
            self,
            repository: PVBRepository,
            bot: AbstractBotAPI,
            config_service: ConfigService,
            user_service: UserService
    ) -> None:
        self.__repo: PVBRepository = repository
        self.__bot: AbstractBotAPI = bot
        self.__config_service: ConfigService = config_service
        self.__user_service: UserService = user_service

    def toggle(self) -> bool:
        return self.__repo.toggle()

    def get_status(self) -> bool:
        return self.__repo.get_status()

    def create(self, dto: CreatePVBDTO) -> PVBDTO:
        return self.__repo.create(dto)

    def get_by_id(self, _id: int) -> PVBDTO | None:
        return self.__repo.get_by_id(_id)

    def get_bet_sum(self) -> int | None:
        return self.__repo.get_bet_sum()

    def get_bet_sum_for_result(self, player_won: bool | None) -> int | None:
        return self.__repo.get_bet_sum_for_result(player_won)

    def get_count(self) -> int:
        return self.__repo.get_count()

    def get_count_for_tg_id(self, tg_id: int) -> int:
        return self.__repo.get_count_for_tg_id(tg_id)

    def get_count_for_result(self, player_won: bool | None) -> int:
        return self.__repo.get_count_for_result(player_won)

    def get_last_5_for_tg_id(self, tg_id: int) -> list[PVBDTO] | None:
        return self.__repo.get_last_5_for_tg_id(tg_id)

    def get_result_percent_for_tg_id_or_bot(self, tg_id: int | None, result: bool | None = True) -> float:
        if tg_id is None:
            wins: int = self.__repo.get_count_for_result(False)
            defeats: int = self.__repo.get_count_for_result(True)
            draws: int = self.__repo.get_count_for_result(None)
        else:
            wins: int = self.__repo.get_count_for_tg_id_and_result(tg_id, True)
            defeats: int = self.__repo.get_count_for_tg_id_and_result(tg_id, False)
            draws: int = self.__repo.get_count_for_tg_id_and_result(tg_id, None)

        total: int = wins + defeats + draws

        if result is None:
            criterion = draws
        elif result:
            criterion = wins
        else:
            criterion = defeats

        return .0 if total == 0 else 100 / total * criterion

    def __validate_game_conditions(self, bet: int, selected_balance: int) -> None:
        config: ConfigDTO = self.__config_service.get()

        if bet < config.min_bet or bet > config.max_bet:
            raise BetOutOfLimitsError(
                Messages.bet_out_of_limits(config.min_bet, config.max_bet)
            )

        if selected_balance < bet:
            raise BalanceIsNotEnoughError(
                Messages.balance_is_not_enough()
            )

    def start_game(self, user_cache: UserCacheDTO) -> None:
        self.__validate_game_conditions(
            user_cache.pvb_bet,
            self.__user_service.get_user_selected_balance(user_cache.tg_id)
        )

        user_cache.pvb_in_process = True
        self.__user_service.update_cache(user_cache)

        if user_cache.pvb_bots_turn_first:
            self.__bot.send_message(
                user_cache.tg_id,
                Messages.pvb_bots_turn()
            )

            user_cache.pvb_bot_dice = self.__bot.send_dice(user_cache.tg_id)
            self.__user_service.update_cache(user_cache)

            time.sleep(DICE_SPIN_ANIMATION_DURATION)

        self.__bot.send_message(
            user_cache.tg_id,
            Messages.pvb_your_turn()
        )

    def finish_game(self, user: UserDTO, user_cache: UserCacheDTO, user_dice: int) -> PVBDTO | None:
        cached_pvb_bot_dice: int | None = user_cache.pvb_bot_dice

        user_cache.pvb_in_process = False
        user_cache.pvb_bot_dice = None

        self.__user_service.update_cache(user_cache)

        if user_cache.pvb_bots_turn_first and cached_pvb_bot_dice is None:
            return

        time.sleep(DICE_SPIN_ANIMATION_DURATION)

        if not user_cache.pvb_bots_turn_first:
            self.__bot.send_message(
                user_cache.tg_id,
                Messages.pvb_bots_turn()
            )

            bot_dice: int = self.__bot.send_dice(user_cache.tg_id)

            time.sleep(DICE_SPIN_ANIMATION_DURATION)
        else:
            bot_dice: int = cached_pvb_bot_dice

        player_won: bool | None = None

        if bot_dice > user_dice:
            player_won = False

            if user_cache.beta_mode:
                user.beta_balance -= user_cache.pvb_bet
            else:
                user.balance -= user_cache.pvb_bet

        elif bot_dice < user_dice:
            player_won = True

            winnings: int = math.floor(user_cache.pvb_bet / 100 * (100 - self.__config_service.get().pvb_fee))

            if user_cache.beta_mode:
                user.beta_balance += winnings
            else:
                user.balance += winnings

        game: PVBDTO = self.__repo.create(
            CreatePVBDTO(
                player_tg_id=user.tg_id,
                player_won=player_won,
                player_dice=user_dice,
                bot_dice=bot_dice,
                bet=user_cache.pvb_bet,
                beta_mode=user_cache.beta_mode
            )
        )

        self.__user_service.update(
            UpdateUserDTO(
                **user.model_dump()
            )
        )

        return game
