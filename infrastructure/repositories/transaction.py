from typing import Type

from sqlalchemy.orm import Query

from core.repositories import TransactionRepository
from core.schemas.transaction import (
    TransactionDTO,
    CreateTransactionDTO,
    UpdateTransactionDTO,
)
from core.states import TransactionStateDirection, TransactionStatus
from infrastructure.cache.redis import RedisInterface, RedisKey, redis_instance
from infrastructure.database import Session
from infrastructure.database.models import TransactionModel


class PostgresRedisTransactionRepository(TransactionRepository):
    def __init__(self) -> None:
        self.__redis: RedisInterface = redis_instance

    @staticmethod
    def __get_key_from_sub_service_id(state_direction: TransactionStateDirection) -> str:
        match state_direction:
            case TransactionStateDirection.SELF:
                return RedisKey.TRANSACTIONS_ACTIVE

            case TransactionStateDirection.DEPOSIT_CARD:
                return RedisKey.TRANSACTIONS_DEPOSIT_CARD_ACTIVE

            case TransactionStateDirection.DEPOSIT_BTC:
                return RedisKey.TRANSACTIONS_DEPOSIT_BTC_ACTIVE

            case TransactionStateDirection.WITHDRAW_CARD:
                return RedisKey.TRANSACTIONS_WITHDRAW_CARD_ACTIVE

            case TransactionStateDirection.WITHDRAW_BTC:
                return RedisKey.TRANSACTIONS_WITHDRAW_BTC_ACTIVE

            case _:
                raise ValueError(f"No such direction with {state_direction}")

    def toggle(self, state_direction: TransactionStateDirection) -> bool:
        key_str: str = self.__get_key_from_sub_service_id(state_direction)

        cached_state: bool | None = self.__redis.get_bool(key_str)
        state: bool = False if cached_state is None else not cached_state

        self.__redis.set_bool(key_str, state)

        return state

    def get_status(self, state_direction: TransactionStateDirection) -> bool:
        key_str: str = self.__get_key_from_sub_service_id(state_direction)

        state: bool | None = self.__redis.get_bool(key_str)

        if state is None:
            self.__redis.set_bool(key_str, False)
            return False

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

    def get_last_5_for_tg_id(self, tg_id: int) -> list[TransactionDTO] | None:
        with Session() as db:
            transactions: Query[Type[TransactionModel]] = db.query(TransactionModel).filter(
                TransactionModel.user_tg_id == tg_id
            ).order_by(TransactionModel.id.desc()).limit(5)

            if transactions.count() == 0:
                return

            return [
                TransactionDTO(**transaction.__dict__) for transaction in transactions
            ]

    def update(self, dto: UpdateTransactionDTO) -> None:
        with Session() as db:
            db.query(TransactionModel).filter(TransactionModel.id == dto.id).update(dto.model_dump())
            db.commit()
