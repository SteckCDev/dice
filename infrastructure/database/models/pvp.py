from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from core.states import PVPStatus
from infrastructure.database import Base


class PVPModel(Base):
    __tablename__ = "games_pvp"

    id: Mapped[int] = mapped_column(primary_key=True)
    creator_tg_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.tg_id"))
    opponent_tg_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.tg_id"), nullable=True)
    winner_tg_id: Mapped[int] = mapped_column(BIGINT, nullable=True)
    creator_dice: Mapped[int] = mapped_column(nullable=True)
    opponent_dice: Mapped[int] = mapped_column(nullable=True)
    bet: Mapped[int]
    beta_mode: Mapped[bool] = mapped_column(default=False)
    status: Mapped[int] = mapped_column(default=PVPStatus.CREATED)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    started_at: Mapped[datetime] = mapped_column(nullable=True)
    finished_at: Mapped[datetime] = mapped_column(nullable=True)
