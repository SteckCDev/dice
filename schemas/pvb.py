from datetime import datetime

from pydantic import BaseModel

from core.datetime import now


class PVBCreate(BaseModel):
    player_tg_id: int
    player_won: bool | None
    player_dice: int
    bot_dice: int
    bet: int
    beta_mode: bool = False
    status: int = 0
    created_at: datetime = now()


class PVBDTO(PVBCreate):
    id: int
