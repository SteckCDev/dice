from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from core.datetime import now
from database import Base


class PVBModel(Base):
    __tablename__ = "games_pvb"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    player_won: Mapped[bool] = mapped_column(nullable=True)
    player_dice: Mapped[int] = mapped_column(nullable=True)
    bot_dice: Mapped[int] = mapped_column(nullable=True)
    bet: Mapped[int]
    beta_mode: Mapped[bool] = mapped_column(default=False)
    status: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=now)
