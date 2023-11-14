from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from common.datetime import now
from infrastructure.database import Base


class PVBModel(Base):
    __tablename__ = "games_pvb"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    player_won: Mapped[bool]
    player_dice: Mapped[int]
    bot_dice: Mapped[int]
    bet: Mapped[int]
    beta_mode: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=now)
