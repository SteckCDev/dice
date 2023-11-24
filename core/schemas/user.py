from datetime import datetime

from pydantic import BaseModel

from core.states.game_mode import GameMode


class User(BaseModel):
    tg_id: int
    tg_name: str
    balance: int
    beta_balance: int
    beta_balance_updated_at: datetime = datetime.now()
    card_details: str | None = None
    btc_wallet_address: str | None = None
    terms_accepted_at: datetime | None = None
    joined_at: datetime = datetime.now()


class UserDTO(BaseModel):
    tg_id: int
    tg_name: str
    balance: int
    beta_balance: int
    beta_balance_updated_at: datetime
    card_details: str | None
    btc_wallet_address: str | None
    terms_accepted_at: datetime | None
    joined_at: datetime


class CreateUserDTO(BaseModel):
    tg_id: int
    tg_name: str
    balance: int
    beta_balance: int


class UpdateUserDTO(BaseModel):
    tg_id: int
    tg_name: str
    balance: int
    beta_balance: int
    beta_balance_updated_at: datetime
    card_details: str | None
    btc_wallet_address: str | None
    terms_accepted_at: datetime | None


class UserCache(BaseModel):
    tg_id: int
    game_mode: GameMode = GameMode.PVB
    beta_mode: bool = False
    pvb_bet: int = 0
    pvb_bot_dice: int | None = None
    pvb_bots_turn_first: bool = False
    pvb_in_process: bool = False
    pvp_bet: int = 0
    pvp_game_id: int | None = None
    pvpc_game_id: int | None = None
    deposit_amount: int = 0
    withdraw_amount: int = 0
    withdraw_bank: str | None = None
    last_message_id: int | None = None


class UserCacheDTO(BaseModel):
    tg_id: int
    game_mode: GameMode
    beta_mode: bool
    pvb_bet: int
    pvb_bot_dice: int | None
    pvb_bots_turn_first: bool
    pvb_in_process: bool
    pvp_bet: int
    pvp_game_id: int | None
    pvpc_game_id: int | None
    deposit_amount: int
    withdraw_amount: int
    withdraw_bank: str | None
    last_message_id: int | None
