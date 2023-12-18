from core.repositories import (
    TransactionRepository,
)
from core.schemas.transaction import (
    TransactionDTO,
    CreateTransactionDTO,
    UpdateTransactionDTO,
)
from core.states import TransactionStateDirection, TransactionStatus


class TransactionService:
    def __init__(self, repository: TransactionRepository) -> None:
        self.__repo: TransactionRepository = repository

    def toggle(self, state_direction: TransactionStateDirection) -> bool:
        return self.__repo.toggle(state_direction)

    def get_status(self, state_direction: TransactionStateDirection) -> bool:
        return self.__repo.get_status(state_direction)

    def create(self, dto: CreateTransactionDTO) -> TransactionDTO:
        return self.__repo.create(dto)

    def get_by_id(self, _id: int) -> TransactionDTO | None:
        return self.__repo.get_by_id(_id)

    def get_all_for_status(self, status: TransactionStatus) -> list[TransactionDTO] | None:
        return self.__repo.get_all_for_status(status)

    def get_last_5_for_tg_id(self, tg_id: int) -> list[TransactionDTO] | None:
        return self.__repo.get_last_5_for_tg_id(tg_id)

    def update(self, dto: UpdateTransactionDTO) -> None:
        self.__repo.update(dto)
