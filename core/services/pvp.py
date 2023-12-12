import math
from datetime import datetime, timedelta
from random import randint
from typing import Final

from core.abstract_bot import AbstractBotAPI
from core.exceptions import (
    BetOutOfLimitsError,
    BalanceIsNotEnoughError,
    PVPAlreadyStartedError,
    PVPNotFoundForUserError,
    PVPCreatorLateError,
    PVPJoinRejectedError,
)
from core.repositories import PVPRepository
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
from core.states import PVPStatus
from templates.messages import Messages


TTL_AFTER_CREATION: Final[timedelta] = timedelta(minutes=2)
TTL_AFTER_START: Final[timedelta] = timedelta(minutes=1)
TIME_UNTIL_CANCELLATION_AVAILABLE: Final[timedelta] = timedelta(minutes=10)


class PVPService:
    def __init__(
            self,
            repository: PVPRepository,
            bot: AbstractBotAPI,
            config_service: ConfigService,
            user_service: UserService
    ) -> None:
        self.__repo: PVPRepository = repository
        self.__bot: AbstractBotAPI = bot
        self.__config_service: ConfigService = config_service
        self.__user_service: UserService = user_service

    def toggle(self) -> bool:
        return self.__repo.toggle()

    def get_status(self) -> bool:
        return self.__repo.get_status()

    def create(self, dto: CreatePVPDTO) -> PVPDTO:
        return self.__repo.create(dto)

    def get_by_id(self, _id: int) -> PVPDTO | None:
        return self.__repo.get_by_id(_id)

    def get_all_for_status(self, status: int) -> list[PVPDTO] | None:
        return self.__repo.get_all_for_status(status)

    def get_last_for_tg_id_and_status(self, tg_id: int, status: int) -> PVPDTO | None:
        return self.__repo.get_last_for_tg_id_and_status(tg_id, status)

    def get_last_5_for_tg_id(self, tg_id: int) -> list[PVPDTO] | None:
        return self.__repo.get_last_5_for_tg_id(tg_id)

    def get_bet_sum(self) -> int:
        return self.__repo.get_bet_sum()

    def get_count(self) -> int:
        return self.__repo.get_count()

    def update(self, dto: UpdatePVPDTO) -> None:
        self.__repo.update(dto)

    def get_wins_percent_for_tg_id(self, tg_id: int) -> float:
        wins: int = self.__repo.get_count_for_tg_id_and_result(tg_id, True)
        defeats: int = self.__repo.get_count_for_tg_id_and_result(tg_id, False)
        draws: int = self.__repo.get_count_for_tg_id_and_result(tg_id, None)

        total: int = wins + defeats + draws

        return .0 if total == 0 else 100 / total * wins

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
            raise BalanceIsNotEnoughError(
                Messages.balance_is_not_enough()
            )

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
        pvp: PVPDTO = self.__repo.get_by_id(pvp_id)
        pvp.status = PVPStatus.CANCELED_BY_CREATOR

        self.__repo.update(
            UpdatePVPDTO(
                **pvp.model_dump()
            )
        )

        user: UserDTO = self.__user_service.get_by_tg_id(pvp.creator_tg_id)

        if pvp.beta_mode:
            user.beta_balance += pvp.bet
        else:
            user.balance += pvp.bet

        self.__user_service.update(
            UpdateUserDTO(
                **user.model_dump()
            )
        )

    def join_game(self, user: UserDTO, user_cache: UserCacheDTO, user_dice: int) -> PVPDetailsDTO:
        pvp_details: PVPDetailsDTO = self.get_details_for_id(user_cache.pvp_game_id)

        if pvp_details.creator_tg_id == user.tg_id:
            raise PVPJoinRejectedError(
                Messages.pvp_join_rejected(pvp_details.id, pvp_details.beta_mode)
            )

        required_balance: int = user.beta_balance if pvp_details.beta_mode else user.balance

        if required_balance < pvp_details.bet:
            raise BalanceIsNotEnoughError(
                Messages.balance_is_not_enough()
            )

        if pvp_details.status != PVPStatus.CREATED:
            raise PVPAlreadyStartedError(
                Messages.pvp_already_started(
                    pvp_details.id, pvp_details.beta_mode
                )
            )

        if pvp_details.beta_mode:
            user.beta_balance -= pvp_details.bet
        else:
            user.balance -= pvp_details.bet

        pvp_details.status = PVPStatus.STARTED
        pvp_details.started_at = datetime.now()
        pvp_details.opponent_tg_id = user.tg_id
        pvp_details.opponent_dice = user_dice

        self.__user_service.update(
            UpdateUserDTO(
                **user.model_dump()
            )
        )

        self.__repo.update(
            UpdatePVPDTO(
                **pvp_details.model_dump()
            )
        )

        return pvp_details

    def __end_game(self, pvp: PVPDTO, creator: UserDTO, final_status: PVPStatus) -> None:
        config: ConfigDTO = self.__config_service.get()

        opponent: UserDTO = self.__user_service.get_by_tg_id(pvp.opponent_tg_id)

        winnings: int = math.floor(pvp.bet * 2 / 100 * (100 - config.pvp_fee))

        if pvp.creator_dice > pvp.opponent_dice:
            creator_balance_correction = winnings
            opponent_balance_correction = 0
            winner_tg_id = creator.tg_id
        elif pvp.creator_dice < pvp.opponent_dice:
            creator_balance_correction = 0
            opponent_balance_correction = winnings
            winner_tg_id = opponent.tg_id
        else:
            creator_balance_correction = pvp.bet
            opponent_balance_correction = pvp.bet
            winner_tg_id = None

        if pvp.beta_mode:
            creator.beta_balance += creator_balance_correction
            opponent.beta_balance += opponent_balance_correction
        else:
            creator.balance += creator_balance_correction
            opponent.balance += opponent_balance_correction

        pvp.status = final_status
        pvp.winner_tg_id = winner_tg_id

        self.__user_service.update(
            UpdateUserDTO(
                **creator.model_dump()
            )
        )
        self.__user_service.update(
            UpdateUserDTO(
                **opponent.model_dump()
            )
        )
        self.__repo.update(
            UpdatePVPDTO(
                **pvp.model_dump()
            )
        )

        if creator.tg_id >= self.__user_service.get_max_fake_tg_id():
            self.__bot.send_message(
                creator.tg_id,
                Messages.pvp_finished(pvp, creator, opponent)
            )

        self.__bot.send_message(
            opponent.tg_id,
            Messages.pvp_finished(pvp, opponent, creator)
        )

    def finish_game(self, creator: UserDTO, creator_dice: int) -> PVPDTO:
        pvp: PVPDTO | None = self.__repo.get_last_for_creator_and_status(creator.tg_id, PVPStatus.STARTED)

        if pvp is None:
            raise PVPNotFoundForUserError()

        if pvp.status != PVPStatus.STARTED:
            raise PVPCreatorLateError(
                Messages.pvp_creator_late(pvp.id, pvp.beta_mode)
            )

        pvp.creator_dice = creator_dice

        self.__end_game(pvp, creator, PVPStatus.FINISHED)

        return pvp

    def auto_finish_started_games(self) -> None:
        games: list[PVPDTO] | None = self.__repo.get_all_for_status(PVPStatus.STARTED)

        if games is None:
            return

        for pvp in games:
            if pvp.started_at + TTL_AFTER_START > datetime.now():
                continue

            if pvp.creator_tg_id >= self.__user_service.get_max_fake_tg_id():
                pvp.creator_dice = self.__bot.send_dice(pvp.creator_tg_id)

                self.__bot.send_message(
                    pvp.creator_tg_id,
                    Messages.pvp_creator_late(pvp.id, pvp.beta_mode)
                )
            else:
                pvp.creator_dice = randint(1, 6)

            creator: UserDTO = self.__user_service.get_by_tg_id(pvp.creator_tg_id)

            self.__end_game(pvp, creator, PVPStatus.FINISHED_BY_BOT)

    def auto_close_expired_games(self) -> None:
        games: list[PVPDTO] | None = self.__repo.get_all_for_status(PVPStatus.CREATED)

        if games is None:
            return

        for pvp in games:
            if pvp.created_at + TTL_AFTER_CREATION > datetime.now():
                continue

            creator: UserDTO = self.__user_service.get_by_tg_id(pvp.creator_tg_id)

            if pvp.beta_mode:
                creator.beta_balance += pvp.bet
            else:
                creator.balance += pvp.bet

            pvp.status = PVPStatus.CANCELED_BY_TTL

            self.__user_service.update(
                UpdateUserDTO(
                    **creator.model_dump()
                )
            )
            self.__repo.update(
                UpdatePVPDTO(
                    **pvp.model_dump()
                )
            )

            self.__bot.send_message(
                creator.tg_id,
                Messages.pvp_expired(
                    pvp.id,
                    pvp.beta_mode,
                    pvp.bet,
                    TTL_AFTER_CREATION
                )
            )
