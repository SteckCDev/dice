from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, BIGINT
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Integer

from core.states import PVPCStatus
from infrastructure.database import Base


class PVPCModel(Base):
    __tablename__ = "games_pvpc"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_tg_id: Mapped[int] = mapped_column(BIGINT)
    creator_tg_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.tg_id"))
    opponent_tg_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.tg_id"), nullable=True)
    winner_tg_id: Mapped[int] = mapped_column(BIGINT, nullable=True)
    creator_dices: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=True)
    opponent_dices: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=True)
    bet: Mapped[int]
    rounds: Mapped[int]
    status: Mapped[int] = mapped_column(default=PVPCStatus.CREATED)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    started_at: Mapped[datetime] = mapped_column(nullable=True)
    finished_at: Mapped[datetime] = mapped_column(nullable=True)
