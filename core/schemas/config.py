from pydantic import BaseModel, ValidationError, field_validator
from pydantic_core.core_schema import ValidationInfo


class Config(BaseModel):
    required_chats: list[int] | None = None
    start_balance: int = 500
    start_beta_balance: int = 10_000
    pvb_fee: int = 3
    pvp_fee: int = 3
    pvpc_fee: int = 3
    card_withdrawal_fee: int = 5
    btc_withdrawal_fee: int = 5
    min_bet: int = 10
    max_bet: int = 20_000
    pvpc_max_rounds: int = 3


class UpdateConfig(BaseModel):
    class Config:
        validate_assignment = True

    required_chats: list[int] | None
    start_balance: int
    start_beta_balance: int
    pvb_fee: int
    pvp_fee: int
    pvpc_fee: int
    card_withdrawal_fee: int
    btc_withdrawal_fee: int
    min_bet: int
    max_bet: int
    pvpc_max_rounds: int

    @field_validator("start_balance", "start_beta_balance")
    def validate_start_balance(cls, value: int) -> int:
        assert isinstance(value, int) and 0 <= value, "Стартовый баланс должен быть положительным числом или нулём"
        return value

    @field_validator("pvb_fee", "pvp_fee", "pvpc_fee", "card_withdrawal_fee", "btc_withdrawal_fee")
    def validate_fee(cls, value: int) -> int:
        assert isinstance(value, int) and (0 <= value <= 100), "Комиссия должна быть числом от 0 до 100"
        return value

    @field_validator("min_bet", "max_bet")
    def validate_bet(cls, value: int) -> int:
        assert isinstance(value, int) and 0 <= value, "Ставка должна быть положительным числом"
        return value

    @field_validator("min_bet")
    def validate_min_bet(cls, value: int, info: ValidationInfo) -> int:
        if info.data.get("max_bet"):
            assert value < info.data.get("max_bet"), "Минимальная ставка должна быть меньше максимальной"
        return value

    @field_validator("max_bet")
    def validate_max_bet(cls, value: int, info: ValidationInfo) -> int:
        assert value > info.data.get("min_bet"), "Максимальная ставка должна быть больше минимальной"
        return value

    @field_validator("min_bet", "max_bet")
    def validate_pvpc_rounds(cls, value: int) -> int:
        assert isinstance(value, int) and 1 <= value, "Максимальное количество раундов должно быть числом больше 0"
        return value

    @staticmethod
    def get_first_error_msg(error: ValidationError) -> str:
        return error.errors()[0]["msg"]


class ConfigDTO(BaseModel):
    required_chats: list[int] | None
    start_balance: int
    start_beta_balance: int
    pvb_fee: int
    pvp_fee: int
    pvpc_fee: int
    card_withdrawal_fee: int
    btc_withdrawal_fee: int
    min_bet: int
    max_bet: int
    pvpc_max_rounds: int
