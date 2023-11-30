from datetime import datetime

from pydantic import BaseModel

from core.states import PVPStatus


class PVPC(BaseModel):
    id: int
    chat_tg_id: int
    creator_tg_id: int
    opponent_tg_id: int | None = None
    winner_tg_id: int | None = None
    creator_dices: list[int] | None = None
    opponent_dices: list[int] | None = None
    bet: int
    rounds: int
    beta_mode: bool = False
    status: PVPStatus = PVPStatus.CREATED
    created_at: datetime = datetime.now()
    started_at: datetime | None = None
    finished_at: datetime | None = None


class PVPCDTO(BaseModel):
    id: int
    chat_tg_id: int
    creator_tg_id: int
    opponent_tg_id: int | None
    winner_tg_id: int | None
    creator_dices: list[int] | None
    opponent_dices: list[int] | None
    bet: int
    rounds: int
    status: PVPStatus
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class CreatePVPCDTO(BaseModel):
    chat_tg_id: int
    creator_tg_id: int
    bet: int
    rounds: int


class UpdatePVPCDTO(BaseModel):
    id: int
    opponent_tg_id: int | None
    winner_tg_id: int | None
    creator_dices: list[int] | None
    opponent_dices: list[int] | None
    status: PVPStatus
    started_at: datetime | None
    finished_at: datetime | None


class PVPCDetailsDTO(PVPCDTO):
    creator_scored: int
    opponent_scored: int
    creator_tg_name: str
    opponent_tg_name: str
    winner_tg_name: str | None
