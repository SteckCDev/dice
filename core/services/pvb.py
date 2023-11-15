import math
import time

from core.base_bot import BaseBotAPI
from core.exceptions.pvb import (
    BetOutOfLimitsError,
    BalanceIsNotEnoughError,
)
from core.repositories.pvb import PVBRepository
from core.schemas.pvb import (
    PVBDTO,
    CreatePVBDTO,
)
from core.schemas.user import (
    UserDTO,
    UpdateUserDTO,
    UserCacheDTO,
)
from core.services.config import ConfigService
from core.services.user import UserService
from templates.messages import Messages


DICE_SPIN_ANIMATION_DURATION = 3


class PVBService:
    def __init__(
            self,
            repository: PVBRepository,
            bot: BaseBotAPI,
            config_service: ConfigService,
            user_service: UserService
    ) -> None:
        self.__repo = repository
        self.__bot = bot
        self.__config_service = config_service
        self.__user_service = user_service

    def toggle(self) -> bool:
        return self.__repo.toggle()

    def get_status(self) -> bool:
        return self.__repo.get_status()

    def create(self, dto: CreatePVBDTO) -> None:
        self.__repo.create(dto)

    def get_by_id(self, _id: int) -> PVBDTO:
        return self.__repo.get_by_id(_id)

    def __validate_game_conditions(self, bet: int, selected_balance: int) -> None:
        config = self.__config_service.get()

        if bet < config.min_bet or bet > config.max_bet:
            raise BetOutOfLimitsError(
                Messages.bet_out_of_limits(config.min_bet, config.max_bet)
            )

        if selected_balance < bet:
            raise BalanceIsNotEnoughError(Messages.balance_is_not_enough)

    def start_game(self, user_cache: UserCacheDTO) -> None:
        self.__validate_game_conditions(
            user_cache.pvb_bet,
            self.__user_service.get_user_selected_balance(user_cache.tg_id)
        )

        user_cache.pvb_in_process = True

        if user_cache.pvb_bots_turn_first:
            self.__bot.send_message(
                user_cache.tg_id,
                Messages.pvb_bots_turn
            )

            user_cache.pvb_bot_dice = self.__bot.send_dice(user_cache.tg_id)

            time.sleep(DICE_SPIN_ANIMATION_DURATION)

        self.__user_service.update_cache(user_cache)

        self.__bot.send_message(
            user_cache.tg_id,
            Messages.pvb_your_turn
        )

    def finish_game(self, user: UserDTO, user_cache: UserCacheDTO, user_dice: int) -> PVBDTO:
        time.sleep(DICE_SPIN_ANIMATION_DURATION)

        if not user_cache.pvb_bots_turn_first:
            self.__bot.send_message(
                user_cache.tg_id,
                Messages.pvb_bots_turn
            )

            user_cache.pvb_bot_dice = self.__bot.send_dice(user_cache.tg_id)

        if user_cache.pvb_bot_dice > user_dice:
            player_won = False

            if user_cache.beta_mode:
                user.beta_balance -= user_cache.pvb_bet
            else:
                user.balance -= user_cache.pvb_bet

        elif user_cache.pvb_bot_dice < user_dice:
            player_won = True

            winnings = math.floor(user_cache.pvb_bet / 100 * (100 - self.__config_service.get().pvb_fee))

            if user_cache.beta_mode:
                user.beta_balance += winnings
            else:
                user.balance += winnings

        else:
            player_won = None

        game = self.__repo.create(
            CreatePVBDTO(
                player_tg_id=user.tg_id,
                player_won=player_won,
                player_dice=user_dice,
                bot_dice=user_cache.pvb_bot_dice,
                bet=user_cache.pvb_bet,
                beta_mode=user_cache.beta_mode
            )
        )

        user_cache.pvb_bot_dice = None
        user_cache.pvb_in_process = False

        self.__user_service.update(
            UpdateUserDTO(**user.model_dump())
        )
        self.__user_service.update_cache(user_cache)

        return game
