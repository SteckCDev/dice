from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from core.states import TransactionStatus


class Transaction(BaseModel):
    id: int
    user_tg_id: int
    type: str
    method: str
    rub: int
    btc: Decimal | None
    fee: int
    recipient_details: str
    recipient_bank: str | None = None
    status: int = TransactionStatus.CREATED
    created_at: datetime = datetime.now()
    processed_at: datetime | None = None


class TransactionDTO(BaseModel):
    id: int
    user_tg_id: int
    type: str
    method: str
    rub: int
    btc: Decimal | None
    fee: int
    recipient_details: str
    recipient_bank: str | None
    status: int
    created_at: datetime
    processed_at: datetime | None


class CreateTransactionDTO(BaseModel):
    user_tg_id: int
    type: str
    method: str
    rub: int
    btc: Decimal | None
    fee: int
    recipient_details: str
    recipient_bank: str | None


class UpdateTransactionDTO(BaseModel):
    id: int
    status: int
    processed_at: datetime | None
