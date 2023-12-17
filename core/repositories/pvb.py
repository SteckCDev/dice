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
    def get_by_id(self, _id: int) -> PVBDTO | None:
        ...

    @abstractmethod
    def get_bet_sum(self) -> int | None:
        ...

    @abstractmethod
    def get_bet_sum_for_result(self, player_won: bool | None) -> int | None:
        ...

    @abstractmethod
    def get_count(self) -> int:
        ...

    @abstractmethod
    def get_count_for_tg_id(self, tg_id: int) -> int:
        ...

    @abstractmethod
    def get_count_for_result(self, player_won: bool | None) -> int:
        ...

    @abstractmethod
    def get_count_for_tg_id_and_result(self, tg_id: int, player_won: bool | None) -> int:
        ...

    @abstractmethod
    def get_last_5_for_tg_id(self, tg_id: int) -> list[PVBDTO] | None:
        ...
