import math
from datetime import datetime, timedelta
from typing import Final

from core.abstract_bot import AbstractBotAPI
from core.exceptions import (
    BalanceIsNotEnoughError,
    PVPCNotFoundForUserError,
    PVPCJoinRejectedError,
    PVPCAlreadyInGameError,
    PVPCAlreadyStartedError,
    PVPCCancellationRejectedError,
)
from core.repositories import (
    PVPCRepository,
)
from core.schemas.config import (
    ConfigDTO,
)
from core.schemas.pvpc import (
    PVPCDTO,
    CreatePVPCDTO,
    UpdatePVPCDTO,
    PVPCDetailsDTO,
)
from core.schemas.user import (
    UserDTO,
    UpdateUserDTO,
)
from core.services.config import ConfigService
from core.services.user import UserService
from core.states import PVPCStatus
from templates import Messages


TTL_AFTER_CREATION: Final[timedelta] = timedelta(minutes=2)
TTL_AFTER_START: Final[timedelta] = timedelta(minutes=1)


class PVPCService:
    def __init__(
            self,
            repository: PVPCRepository,
            bot: AbstractBotAPI,
            user_service: UserService,
            config_service: ConfigService
    ) -> None:
        self.__repo: PVPCRepository = repository
        self.__bot: AbstractBotAPI = bot
        self.__config_service: ConfigService = config_service
        self.__user_service: UserService = user_service

    def toggle(self) -> bool:
        return self.__repo.toggle()

    def get_status(self) -> bool:
        return self.__repo.get_status()

    def create(self, dto: CreatePVPCDTO) -> PVPCDTO:
        return self.__repo.create(dto)

    def get_by_id(self, _id: int) -> PVPCDTO | None:
        return self.__repo.get_by_id(_id)

    def update(self, dto: UpdatePVPCDTO) -> None:
        self.__repo.update(dto)

    def get_for_tg_id_and_status(self, user_tg_id: int, status: PVPCStatus) -> PVPCDTO | None:
        return self.__repo.get_for_tg_id_and_status(user_tg_id, status)

    def get_bet_sum(self) -> int | None:
        return self.__repo.get_bet_sum()

    def get_count(self) -> int:
        return self.__repo.get_count()

    def create_game(self, user: UserDTO, chat_id: int, bet: int, rounds: int) -> PVPCDTO:
        pvpc: PVPCDTO = self.__repo.create(
            CreatePVPCDTO(
                chat_tg_id=chat_id,
                creator_tg_id=user.tg_id,
                bet=bet,
                rounds=rounds
            )
        )

        user.balance -= bet

        self.__user_service.update(
            UpdateUserDTO(
                **user.model_dump()
            )
        )

        return pvpc

    def join_game(self, _id: int, user: UserDTO) -> PVPCDetailsDTO:
        pvpc: PVPCDTO | None = self.__repo.get_by_id(_id)

        if pvpc is None:
            raise PVPCNotFoundForUserError()

        if pvpc.creator_tg_id == user.tg_id:
            raise PVPCJoinRejectedError()

        created_pvpc: PVPCDTO | None = self.__repo.get_for_tg_id_and_status(user.tg_id, PVPCStatus.CREATED)
        started_pvpc: PVPCDTO | None = self.__repo.get_for_tg_id_and_status(user.tg_id, PVPCStatus.STARTED)

        if created_pvpc or started_pvpc:
            raise PVPCAlreadyInGameError()

        if pvpc.status != PVPCStatus.CREATED:
            raise PVPCAlreadyStartedError()

        if user.balance < pvpc.bet:
            raise BalanceIsNotEnoughError()

        creator: UserDTO = self.__user_service.get_by_tg_id(pvpc.creator_tg_id)

        user.balance -= pvpc.bet
        pvpc.status = PVPCStatus.STARTED
        pvpc.opponent_tg_id = user.tg_id
        pvpc.started_at = datetime.now()

        self.__user_service.update(
            UpdateUserDTO(
                **user.model_dump()
            )
        )
        self.__repo.update(
            UpdatePVPCDTO(
                **pvpc.model_dump()
            )
        )

        return PVPCDetailsDTO(
            **pvpc.model_dump(),
            creator_scored=0,
            opponent_scored=0,
            creator_tg_name=creator.tg_name,
            opponent_tg_name=user.tg_name,
            winner_tg_name=None
        )

    def cancel_game(self, _id: int, user: UserDTO) -> None:
        pvpc: PVPCDTO | None = self.__repo.get_by_id(_id)

        if pvpc is None:
            raise PVPCNotFoundForUserError()

        if user.tg_id != pvpc.creator_tg_id:
            raise PVPCCancellationRejectedError()

        if pvpc.status != PVPCStatus.CREATED:
            raise PVPCAlreadyStartedError()

        pvpc.status = PVPCStatus.CANCELED_BY_CREATOR
        user.balance += pvpc.bet

        self.__repo.update(
            UpdatePVPCDTO(
                **pvpc.model_dump()
            )
        )
        self.__user_service.update(
            UpdateUserDTO(
                **user.model_dump()
            )
        )

    def __finish_game(self, pvpc: PVPCDTO, creator: UserDTO, opponent: UserDTO, with_status: PVPCStatus) -> None:
        creator_scored: int = sum(pvpc.creator_dices)
        opponent_scored: int = sum(pvpc.opponent_dices)

        config: ConfigDTO = self.__config_service.get()

        bank: int = math.floor(pvpc.bet * 2 / 100 * (100 - config.pvpc_fee))

        winner_tg_name: str | None = None

        if creator_scored > opponent_scored:
            creator.balance += bank
            pvpc.winner_tg_id = pvpc.creator_tg_id
            winner_tg_name = creator.tg_name
        elif creator_scored < opponent_scored:
            opponent.balance += bank
            pvpc.winner_tg_id = pvpc.opponent_tg_id
            winner_tg_name = opponent.tg_name
        else:
            creator.balance += pvpc.bet
            opponent.balance += pvpc.bet

        pvpc.status = with_status
        pvpc.finished_at = datetime.now()

        self.__repo.update(
            UpdatePVPCDTO(
                **pvpc.model_dump()
            )
        )
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

        self.__bot.send_message(
            pvpc.chat_tg_id,
            Messages.pvpc_results(
                PVPCDetailsDTO(
                    **pvpc.model_dump(),
                    creator_scored=creator_scored,
                    opponent_scored=opponent_scored,
                    creator_tg_name=creator.tg_name,
                    opponent_tg_name=opponent.tg_name,
                    winner_tg_name=winner_tg_name
                )
            )
        )

    def process_dice(self, user_tg_id: int, chat_id: int, user_dice: int) -> PVPCDTO | None:
        pvpc: PVPCDTO | None = self.__repo.get_for_tg_id_and_status(user_tg_id, PVPCStatus.STARTED)

        if pvpc is None or pvpc.chat_tg_id != chat_id:
            return

        creator_has_extra_throws: bool = (len(pvpc.creator_dices) != pvpc.rounds) if pvpc.creator_dices else True
        opponent_has_extra_throws: bool = (len(pvpc.opponent_dices) != pvpc.rounds) if pvpc.opponent_dices else True

        if user_tg_id == pvpc.creator_tg_id and creator_has_extra_throws:
            if pvpc.creator_dices is None:
                pvpc.creator_dices = [user_dice]
            else:
                pvpc.creator_dices.append(user_dice)
        elif user_tg_id == pvpc.opponent_tg_id and opponent_has_extra_throws:
            if pvpc.opponent_dices is None:
                pvpc.opponent_dices = [user_dice]
            else:
                pvpc.opponent_dices.append(user_dice)

        creator_has_extra_throws = (len(pvpc.creator_dices) != pvpc.rounds) if pvpc.creator_dices else True
        opponent_has_extra_throws = (len(pvpc.opponent_dices) != pvpc.rounds) if pvpc.opponent_dices else True

        if creator_has_extra_throws or opponent_has_extra_throws:
            self.__repo.update(
                UpdatePVPCDTO(
                    **pvpc.model_dump()
                )
            )
            return pvpc

        creator: UserDTO = self.__user_service.get_by_tg_id(pvpc.creator_tg_id)
        opponent: UserDTO = self.__user_service.get_by_tg_id(pvpc.opponent_tg_id)

        self.__finish_game(pvpc, creator, opponent, PVPCStatus.FINISHED)

    def __try_throw_for_user(self, user: UserDTO, pvpc: PVPCDTO) -> None:
        is_creator: bool = pvpc.creator_tg_id == user.tg_id
        user_dices: list[int] | None = pvpc.creator_dices if is_creator else pvpc.opponent_dices

        user_throws_left: int = pvpc.rounds - (
            len(user_dices) if user_dices else 0
        )

        if not user_throws_left:
            return

        self.__bot.send_message(
            pvpc.chat_tg_id,
            Messages.pvpc_throwing_for_user(pvpc.id, user.tg_name)
        )

        for _ in range(user_throws_left):
            dice: int = self.__bot.send_dice(pvpc.chat_tg_id)

            if is_creator:
                if pvpc.creator_dices is None:
                    pvpc.creator_dices = [dice]
                else:
                    pvpc.creator_dices.append(dice)
            else:
                if pvpc.opponent_dices is None:
                    pvpc.opponent_dices = [dice]
                else:
                    pvpc.opponent_dices.append(dice)

    def auto_finish_started_games(self) -> None:
        pvpc_games: list[PVPCDTO] | None = self.__repo.get_all_for_status(PVPCStatus.STARTED)

        if pvpc_games is None:
            return

        config: ConfigDTO = self.__config_service.get()
        ttl_after_start: timedelta = timedelta(minutes=config.pvpc_ttl_after_start)

        for pvpc in pvpc_games:
            if pvpc.started_at + ttl_after_start >= datetime.now():
                return

            creator: UserDTO = self.__user_service.get_by_tg_id(pvpc.creator_tg_id)
            opponent: UserDTO = self.__user_service.get_by_tg_id(pvpc.opponent_tg_id)

            self.__try_throw_for_user(creator, pvpc)
            self.__try_throw_for_user(opponent, pvpc)

            self.__finish_game(pvpc, creator, opponent, PVPCStatus.FINISHED_BY_BOT)

    def auto_close_expired_games(self) -> None:
        pvpc_games: list[PVPCDTO] | None = self.__repo.get_all_for_status(PVPCStatus.CREATED)

        if pvpc_games is None:
            return

        config: ConfigDTO = self.__config_service.get()
        ttl_after_creation: timedelta = timedelta(minutes=config.pvpc_ttl_after_creation)

        for pvpc in pvpc_games:
            if pvpc.created_at + ttl_after_creation >= datetime.now():
                return

            pvpc.status = PVPCStatus.CANCELED_BY_TTL

            self.__repo.update(
                UpdatePVPCDTO(
                    **pvpc.model_dump()
                )
            )

            user: UserDTO = self.__user_service.get_by_tg_id(pvpc.creator_tg_id)
            user.balance += pvpc.bet

            self.__user_service.update(
                UpdateUserDTO(
                    **user.model_dump()
                )
            )
