from datetime import datetime

from sqlalchemy.dialects.postgresql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database import Base


class DetailsModel(Base):
    __tablename__ = "details"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_tg_id: Mapped[int] = mapped_column(BIGINT)
    method: Mapped[str]
    withdraw_details: Mapped[str]
    withdraw_bank: Mapped[str] = mapped_column(nullable=True)
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
