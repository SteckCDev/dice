from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database import Base


class UserModel(Base):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    tg_name: Mapped[str]
    balance: Mapped[int]
    beta_balance: Mapped[int]
    beta_balance_updated_at: Mapped[datetime] = mapped_column(default=datetime.now)
    card_details: Mapped[str] = mapped_column(nullable=True)
    btc_wallet_address: Mapped[str] = mapped_column(nullable=True)
    terms_accepted_at: Mapped[datetime] = mapped_column(nullable=True)
    joined_at: Mapped[datetime] = mapped_column(default=datetime.now)
