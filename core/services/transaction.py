from core.repositories import (
    TransactionRepository,
)
from core.schemas.transaction import (
    TransactionDTO,
    CreateTransactionDTO,
    UpdateTransactionDTO,
)


class TransactionService:
    def __init__(self, repository: TransactionRepository) -> None:
        self.__repo: TransactionRepository = repository

    def toggle(self) -> bool:
        return self.__repo.toggle()

    def get_status(self) -> bool:
        return self.__repo.get_status()

    def create(self, dto: CreateTransactionDTO) -> TransactionDTO:
        return self.__repo.create(dto)

    def get_by_id(self, _id: int) -> TransactionDTO | None:
        return self.__repo.get_by_id(_id)

    def update(self, dto: UpdateTransactionDTO) -> None:
        self.__repo.update(dto)
