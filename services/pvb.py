from math import floor
from time import sleep

from api_services import TeleBotAPI
from core.base_service import ToggleableService
from core.redis_keys import RedisKeys
from database import Session
from database.models import PVBModel
from schemas import (
    PVBCreate,
    PVBDTO,
    UserCache,
    UserDTO,
)
from services.config import ConfigService
from services.user import UserService
from settings import settings
from templates import Messages


DICE_SPIN_DELAY = 3


class PVBService(ToggleableService):
    def __init__(self):
        super().__init__()
        self._redis_key = RedisKeys.PVB_ACTIVE

        self.__bot = TeleBotAPI(settings.bot_token)
        self.__config = ConfigService.get()

    @staticmethod
    def __create(game: PVBCreate) -> PVBDTO:
        with Session() as db:
            db.add(PVBModel(**game.model_dump()))
            db.commit()

            game_id = db.query(PVBModel).order_by(PVBModel.id.desc()).first().id

        return PVBDTO(id=game_id, **game.model_dump())

    def game_validate(self, user: UserDTO, user_cache: UserCache) -> None:
        if user_cache.pvb_bet < self.__config.min_bet or user_cache.pvb_bet > self.__config.max_bet:
            raise ValueError

        selected_balance = user.beta_balance if user_cache.beta_mode else user.balance

        if selected_balance < user_cache.pvb_bet:
            raise ValueError()

    def start_game(self, user: UserDTO, user_cache: UserCache) -> None:
        self.game_validate(user, user_cache)

        user_cache.pvb_in_process = True

        if user_cache.pvb_bots_turn_first:
            self.__bot.send_message(
                user.tg_id,
                Messages.pvb_bots_turn
            )

            user_cache.pvb_bot_dice = self.__bot.send_dice(user.tg_id)

            sleep(DICE_SPIN_DELAY)

        UserService.update_cache(user.tg_id, user_cache)

        self.__bot.send_message(
            user.tg_id,
            Messages.pvb_your_turn
        )

    def _second_throw(self, user: UserDTO, user_cache: UserCache) -> None:
        self.__bot.send_message(
            user.tg_id,
            Messages.pvb_bots_turn
        )

        user_cache.pvb_bot_dice = self.__bot.send_dice(user.tg_id)
        UserService.update_cache(user.tg_id, user_cache)

    def finish_game(self, user: UserDTO, user_cache: UserCache, user_dice: int) -> PVBDTO:
        sleep(DICE_SPIN_DELAY)

        if not user_cache.pvb_bots_turn_first:
            self._second_throw(user, user_cache)

        if user_cache.pvb_bot_dice > user_dice:
            player_won = False

            if user_cache.beta_mode:
                user.beta_balance -= user_cache.pvb_bet
            else:
                user.balance -= user_cache.pvb_bet

        elif user_cache.pvb_bot_dice < user_dice:
            player_won = True

            winnings = floor(user_cache.pvb_bet / 100 * (100 - self.__config.pvb_fee))

            if user_cache.beta_mode:
                user.beta_balance += winnings
            else:
                user.balance += winnings

        else:
            player_won = None

        game = self.__create(
            PVBCreate(
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

        UserService.update(user)
        UserService.update_cache(user.tg_id, user_cache)

        return game
