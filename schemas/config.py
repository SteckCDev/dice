from pydantic import BaseModel


class ConfigDTO(BaseModel):
    start_balance: int
    start_beta_balance: int
