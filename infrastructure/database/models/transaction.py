from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from core.states import TransactionStatus
from infrastructure.database import Base


class TransactionModel(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_tg_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.tg_id"))
    type: Mapped[str]
    method: Mapped[str]
    rub: Mapped[int]
    btc: Mapped[Decimal] = mapped_column(nullable=True)
    fee: Mapped[int]
    recipient_details: Mapped[str] = mapped_column(nullable=True)
    recipient_bank: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[int] = mapped_column(default=TransactionStatus.CREATED)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    processed_at: Mapped[datetime] = mapped_column(nullable=True)
