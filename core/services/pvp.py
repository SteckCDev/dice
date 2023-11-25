from datetime import datetime, timedelta
from typing import Final

from core.base_bot import BaseBotAPI
from core.exceptions.pvb import (
    BetOutOfLimitsError,
    BalanceIsNotEnoughError,
)
from core.repositories.pvp import PVPRepository
from core.schemas.config import ConfigDTO
from core.schemas.pvp import (
    PVPDTO,
    CreatePVPDTO,
    UpdatePVPDTO,
    PVPDetailsDTO,
)
from core.schemas.user import (
    UserDTO,
    UpdateUserDTO,
    UserCacheDTO,
)
from core.services.config import ConfigService
from core.services.user import UserService
from core.states.pvp_status import PVPStatus
from templates.messages import Messages


TIME_UNTIL_CANCELLATION_AVAILABLE: Final[timedelta] = timedelta(minutes=10)


class PVPService:
    def __init__(
            self,
            repository: PVPRepository,
            bot: BaseBotAPI,
            config_service: ConfigService,
            user_service: UserService
    ) -> None:
        self.__repo: PVPRepository = repository
        self.__bot: BaseBotAPI = bot
        self.__config_service: ConfigService = config_service
        self.__user_service: UserService = user_service

    def toggle(self) -> bool:
        return self.__repo.toggle()

    def get_status(self) -> bool:
        return self.__repo.get_status()

    def create(self, dto: CreatePVPDTO) -> None:
        self.__repo.create(dto)

    def get_by_id(self, _id: int) -> PVPDTO:
        return self.__repo.get_by_id(_id)

    def update(self, dto: UpdatePVPDTO) -> None:
        self.__repo.update(dto)

    def get_all_for_status(self, status: int) -> list[PVPDTO] | None:
        return self.__repo.get_all_for_status(status)

    def get_details_for_id(self, _id: int) -> PVPDetailsDTO:
        game: PVPDTO = self.__repo.get_by_id(_id)
        creator: UserDTO = self.__user_service.get_by_tg_id(game.creator_tg_id)

        now: datetime = datetime.now()
        cancellation_available_at: datetime = game.created_at + TIME_UNTIL_CANCELLATION_AVAILABLE

        cancellation_unlocks_in: timedelta | None = None if (
                now >= cancellation_available_at
        ) else cancellation_available_at - now

        return PVPDetailsDTO(
            **game.model_dump(),
            creator_name=creator.tg_name,
            cancellation_unlocks_in=cancellation_unlocks_in
        )

    def __validate_game_conditions(self, bet: int, selected_balance: int) -> None:
        config: ConfigDTO = self.__config_service.get()

        if bet < config.min_bet or bet > config.max_bet:
            raise BetOutOfLimitsError(
                Messages.bet_out_of_limits(config.min_bet, config.max_bet)
            )

        if selected_balance < bet:
            raise BalanceIsNotEnoughError(Messages.balance_is_not_enough())

    def create_game(self, user: UserDTO, user_cache: UserCacheDTO) -> PVPDTO:
        self.__validate_game_conditions(
            user_cache.pvp_bet,
            self.__user_service.get_user_selected_balance(user_cache.tg_id)
        )

        if user_cache.beta_mode:
            user.beta_balance -= user_cache.pvp_bet
        else:
            user.balance -= user_cache.pvp_bet

        self.__user_service.update(
            UpdateUserDTO(
                **user.model_dump()
            )
        )
        self.__user_service.update_cache(user_cache)

        return self.__repo.create(
            CreatePVPDTO(
                creator_tg_id=user_cache.tg_id,
                bet=user_cache.pvp_bet,
                beta_mode=user_cache.beta_mode
            )
        )

    def cancel_by_creator(self, pvp_id: int) -> None:
        game: PVPDTO = self.__repo.get_by_id(pvp_id)
        game.status = PVPStatus.CANCELED_BY_CREATOR

        self.__repo.update(
            UpdatePVPDTO(
                **game.model_dump()
            )
        )

        user: UserDTO = self.__user_service.get_by_tg_id(game.creator_tg_id)

        if game.beta_mode:
            user.beta_balance += game.bet
        else:
            user.balance += game.bet

        self.__user_service.update(
            UpdateUserDTO(
                **user.model_dump()
            )
        )
