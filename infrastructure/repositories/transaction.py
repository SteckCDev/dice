from typing import Type

from sqlalchemy.orm import Query

from core.repositories import TransactionRepository
from core.schemas.transaction import (
    TransactionDTO,
    CreateTransactionDTO,
    UpdateTransactionDTO,
)
from core.states import TransactionStatus
from infrastructure.cache.redis import RedisInterface, RedisKey, redis_instance
from infrastructure.database import Session
from infrastructure.database.models import TransactionModel


class PostgresRedisTransactionRepository(TransactionRepository):
    def __init__(self) -> None:
        self.__redis: RedisInterface = redis_instance

    def toggle(self) -> bool:
        cached_state: bool | None = self.__redis.get_bool(RedisKey.TRANSACTIONS_ACTIVE)
        state: bool = True if cached_state is None else not cached_state

        self.__redis.set_bool(RedisKey.TRANSACTIONS_ACTIVE, state)

        return state

    def get_status(self) -> bool:
        state: bool | None = self.__redis.get_bool(RedisKey.TRANSACTIONS_ACTIVE)

        if state is None:
            self.__redis.set_bool(RedisKey.TRANSACTIONS_ACTIVE, True)
            return True

        return state

    def create(self, dto: CreateTransactionDTO) -> TransactionDTO:
        with Session() as db:
            db.add(TransactionModel(**dto.model_dump()))
            db.commit()

            transaction: Type[TransactionModel] = db.query(TransactionModel).order_by(
                TransactionModel.id.desc()
            ).first()

        return TransactionDTO(**transaction.__dict__)

    def get_by_id(self, _id: int) -> TransactionDTO | None:
        with Session() as db:
            transaction: Type[TransactionModel] | None = db.get(TransactionModel, _id)

        return TransactionDTO(**transaction.__dict__) if transaction else None

    def get_all_for_status(self, status: TransactionStatus) -> list[TransactionDTO] | None:
        with Session() as db:
            transactions: Query[Type[TransactionModel]] = db.query(TransactionModel).filter(
                TransactionModel.status == status
            ).order_by(TransactionModel.id.desc())

            if transactions.count() == 0:
                return

            return [
                TransactionDTO(**transaction.__dict__) for transaction in transactions
            ]

    def update(self, dto: UpdateTransactionDTO) -> None:
        with Session() as db:
            db.query(TransactionModel).filter(TransactionModel.id == dto.id).update(dto.model_dump())
            db.commit()
