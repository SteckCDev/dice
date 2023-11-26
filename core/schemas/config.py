from pydantic import BaseModel


class Config(BaseModel):
    required_chats: list[int] | None = None
    start_balance: int = 500
    start_beta_balance: int = 10_000
    min_bet: int = 10
    max_bet: int = 20_000
    pvb_fee: int = 3
    pvp_fee: int = 3


class ConfigDTO(BaseModel):
    required_chats: list[int] | None
    start_balance: int
    start_beta_balance: int
    min_bet: int
    max_bet: int
    pvb_fee: int
    pvp_fee: int
