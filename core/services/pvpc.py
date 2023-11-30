from datetime import datetime

from core.abstract_bot import AbstractBotAPI
from core.exceptions import (
    BalanceIsNotEnoughError,
    PVPCNotFoundForUserError,
    PVPCJoinRejectedError,
    PVPCAlreadyInGameError,
    PVPCAlreadyStartedError,
    PVPCCancellationRejected,
)
from core.repositories import (
    PVPCRepository,
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
from core.services.user import UserService
from core.states import PVPCStatus


class PVPCService:
    def __init__(
            self,
            repository: PVPCRepository,
            bot: AbstractBotAPI,
            user_service: UserService
    ) -> None:
        self.__repo: PVPCRepository = repository
        self.__bot: AbstractBotAPI = bot
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
            raise PVPCCancellationRejected()

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
