from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.types import Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from common.datetime import now
from infrastructure.database import Base


class PVPCModel(Base):
    __tablename__ = "games_pvpc"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_tg_id: Mapped[int]
    creator_tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    opponent_tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    winner_tg_id: Mapped[int] = mapped_column(nullable=True)
    creator_dices: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=True)
    opponent_dices: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=True)
    bet: Mapped[int]
    rounds: Mapped[int]
    status: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=now)
    started_at: Mapped[datetime] = mapped_column(nullable=True)
    finished_at: Mapped[datetime] = mapped_column(nullable=True)
