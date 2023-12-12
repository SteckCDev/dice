from abc import ABC, abstractmethod

from core.schemas.transaction import (
    TransactionDTO,
    CreateTransactionDTO,
    UpdateTransactionDTO,
)
from core.states import TransactionStatus


class TransactionRepository(ABC):
    @abstractmethod
    def toggle(self) -> bool:
        ...

    @abstractmethod
    def get_status(self) -> bool:
        ...

    @abstractmethod
    def create(self, dto: CreateTransactionDTO) -> TransactionDTO:
        ...

    @abstractmethod
    def get_by_id(self, _id: int) -> TransactionDTO | None:
        ...

    @abstractmethod
    def get_all_for_status(self, status: TransactionStatus) -> list[TransactionDTO] | None:
        ...

    @abstractmethod
    def get_last_5_for_tg_id(self, tg_id: int) -> list[TransactionDTO] | None:
        ...

    @abstractmethod
    def update(self, dto: UpdateTransactionDTO) -> None:
        ...
