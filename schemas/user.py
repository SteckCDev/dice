from datetime import datetime

from pydantic import BaseModel

from core.states.mode import Mode


class UserDTO(BaseModel):
    tg_id: int
    tg_name: str
    balance: int
    beta_balance: int
    beta_balance_updated_at: datetime
    card_details: str | None = None
    btc_wallet_address: str | None = None
    terms_accepted_at: datetime | None = None
    joined_at: datetime


class UserCache(BaseModel):
    class Config:
        use_enum_values = True

    mode: Mode = Mode.PVB
    pvb_bet: int = 0
    pvb_bot_dice: int | None = None
    pvb_bots_turn_first: bool = False
    pvb_in_process: bool = False
    pvp_bet: int = 0
    pvp_game_id: int | None = None
    pvpc_game_id: int | None = None
    transaction_bank: str | None = None
    deposit_amount: int = 0
    withdraw_amount: int = 0
    beta_mode: bool = False
    last_message_id: int | None = None


class UserProfile(BaseModel):
    tg_name: str
    balance: int
    beta_balance: int
    joined_at: datetime
    games_count: int
