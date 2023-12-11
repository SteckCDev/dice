from abc import ABC, abstractmethod

from core.schemas.pvp import (
    PVPDTO,
    CreatePVPDTO,
    UpdatePVPDTO,
)
from core.states import PVPStatus


class PVPRepository(ABC):
    @abstractmethod
    def toggle(self) -> bool:
        ...

    @abstractmethod
    def get_status(self) -> bool:
        ...

    @abstractmethod
    def create(self, dto: CreatePVPDTO) -> PVPDTO:
        ...

    @abstractmethod
    def get_by_id(self, _id: int) -> PVPDTO | None:
        ...

    @abstractmethod
    def get_all_for_status(self, status: int) -> list[PVPDTO] | None:
        ...

    @abstractmethod
    def get_last_for_tg_id_and_status(self, tg_id: int, status: int) -> PVPDTO | None:
        ...

    @abstractmethod
    def get_last_for_creator_and_status(self, tg_id: int, status: PVPStatus) -> PVPDTO:
        ...

    @abstractmethod
    def update(self, dto: UpdatePVPDTO) -> None:
        ...
