from abc import ABC, abstractmethod

from core.schemas.pvp import (
    PVPDTO,
    CreatePVPDTO,
    UpdatePVPDTO,
)


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
    def get_by_id(self, _id: int) -> PVPDTO:
        ...

    @abstractmethod
    def update(self, dto: UpdatePVPDTO) -> None:
        ...

    @abstractmethod
    def get_all_for_status(self, status: int) -> list[PVPDTO] | None:
        ...
