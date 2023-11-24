from datetime import datetime, timedelta

from pydantic import BaseModel

from core.states.pvp_status import PVPStatus


class PVP(BaseModel):
    id: int
    creator_tg_id: int
    opponent_tg_id: int | None = None
    winner_tg_id: int | None = None
    creator_dice: int | None = None
    opponent_dice: int | None = None
    bet: int
    beta_mode: bool = False
    status: PVPStatus = PVPStatus.CREATED
    created_at: datetime = datetime.now()
    started_at: datetime | None = None
    finished_at: datetime | None = None


class PVPDTO(BaseModel):
    id: int
    creator_tg_id: int
    opponent_tg_id: int | None
    winner_tg_id: int | None
    creator_dice: int | None
    opponent_dice: int | None
    bet: int
    beta_mode: bool
    status: PVPStatus
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class CreatePVPDTO(BaseModel):
    creator_tg_id: int
    bet: int
    beta_mode: bool


class UpdatePVPDTO(BaseModel):
    winner_tg_id: int | None = None
    creator_dice: int | None = None
    opponent_dice: int | None = None
    status: PVPStatus
    started_at: datetime | None = None
    finished_at: datetime | None = None


class PVPDetailsDTO(PVPDTO):
    creator_name: str
    cancellation_unlocks_in: timedelta | None
