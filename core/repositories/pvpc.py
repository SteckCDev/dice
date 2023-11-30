from abc import ABC, abstractmethod

from core.schemas.pvpc import (
    PVPCDTO,
    CreatePVPCDTO,
    UpdatePVPCDTO,
)
from core.states import PVPCStatus


class PVPCRepository(ABC):
    @abstractmethod
    def toggle(self) -> bool:
        ...

    @abstractmethod
    def get_status(self) -> bool:
        ...

    @abstractmethod
    def create(self, dto: CreatePVPCDTO) -> PVPCDTO:
        ...

    @abstractmethod
    def get_by_id(self, _id: int) -> PVPCDTO | None:
        ...

    @abstractmethod
    def update(self, dto: UpdatePVPCDTO) -> None:
        ...

    @abstractmethod
    def get_for_tg_id_and_status(self, user_tg_id: int, status: PVPCStatus) -> PVPCDTO | None:
        ...
