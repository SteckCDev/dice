from decimal import Decimal
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from core.datetime import now
from database import Base


class TransactionModel(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    type: Mapped[str]
    method: Mapped[str]
    rub: Mapped[int]
    btc_to_rub_currency: Mapped[Decimal]
    btc: Mapped[Decimal]
    fee: Mapped[int] = mapped_column(default=0)
    withdrawal_bank_name: Mapped[str] = mapped_column(nullable=True)
    withdrawal_card_details: Mapped[str] = mapped_column(nullable=True)
    withdrawal_btc_wallet: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(default=now)
    processed_at: Mapped[datetime] = mapped_column(nullable=True)
