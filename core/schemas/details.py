from datetime import datetime

from pydantic import BaseModel


class Details(BaseModel):
    id: int
    user_tg_id: int
    method: str
    withdraw_details: str
    withdraw_bank: str | None = None
    active: bool = True
    created_at: datetime = datetime.now()


class DetailsDTO(BaseModel):
    id: int
    user_tg_id: int
    method: str
    withdraw_details: str
    withdraw_bank: str | None
    active: bool
    created_at: datetime


class CreateDetailsDTO(BaseModel):
    user_tg_id: int
    method: str
    withdraw_details: str
    withdraw_bank: str | None


class UpdateDetailsDTO(BaseModel):
    id: int
    withdraw_details: str
    withdraw_bank: str | None
