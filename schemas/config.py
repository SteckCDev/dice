from pydantic import BaseModel


class ConfigDTO(BaseModel):
    start_balance: int
    start_beta_balance: int
    min_bet: int
    max_bet: int
    pvb_fee: int
