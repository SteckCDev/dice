from abc import ABC, abstractmethod

from core.schemas.pvb import (
    PVBDTO,
    CreatePVBDTO,
)


class PVBRepository(ABC):
    @abstractmethod
    def toggle(self) -> bool:
        ...

    @abstractmethod
    def get_status(self) -> bool:
        ...

    @abstractmethod
    def create(self, dto: CreatePVBDTO) -> PVBDTO:
        ...

    @abstractmethod
    def get_by_id(self, _id: int) -> PVBDTO:
        ...
