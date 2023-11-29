from datetime import datetime

from pydantic import BaseModel


class PVB(BaseModel):
    id: int
    player_tg_id: int
    player_won: bool | None
    player_dice: int
    bot_dice: int
    bet: int
    beta_mode: bool = False
    created_at: datetime = datetime.now()


class PVBDTO(BaseModel):
    id: int
    player_tg_id: int
    player_won: bool | None
    player_dice: int
    bot_dice: int
    bet: int
    beta_mode: bool
    created_at: datetime


class CreatePVBDTO(BaseModel):
    player_tg_id: int
    player_won: bool | None
    player_dice: int
    bot_dice: int
    bet: int
    beta_mode: bool
