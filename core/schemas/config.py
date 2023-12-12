from pydantic import BaseModel, ValidationError, field_validator
from pydantic_core.core_schema import ValidationInfo


class Config(BaseModel):
    required_chats: list[int] | None = None
    card_details: str = "0000 0000 0000 0000"
    btc_details: str = "1B..."
    start_balance: int = 500
    start_beta_balance: int = 10_000
    pvb_fee: int = 3
    pvp_fee: int = 3
    pvpc_fee: int = 3
    min_deposit: int = 500
    min_withdraw: int = 1000
    card_withdrawal_fee: int = 5
    btc_withdrawal_fee: int = 5
    min_bet: int = 10
    max_bet: int = 20_000
    pvpc_max_rounds: int = 3
    pvpf_min_bet: int = 20
    pvpf_max_bet: int = 200
    pvpf_creation_probability: int = 2


class UpdateConfig(BaseModel):
    class Config:
        validate_assignment = True

    required_chats: list[int] | None
    card_details: str
    btc_details: str
    start_balance: int
    start_beta_balance: int
    pvb_fee: int
    pvp_fee: int
    pvpc_fee: int
    min_deposit: int
    min_withdraw: int
    card_withdrawal_fee: int
    btc_withdrawal_fee: int
    min_bet: int
    max_bet: int
    pvpc_max_rounds: int
    pvpf_min_bet: int
    pvpf_max_bet: int
    pvpf_creation_probability: int

    @field_validator("start_balance", "start_beta_balance")
    def validate_start_balance(cls, value: int) -> int:
        if not isinstance(value, int) or value < 0:
            raise ValueError("Стартовый баланс должен быть положительным числом или нулём")

        return value

    @field_validator("pvb_fee", "pvp_fee", "pvpc_fee", "card_withdrawal_fee", "btc_withdrawal_fee")
    def validate_fee(cls, value: int) -> int:
        if not isinstance(value, int) or value < 0 or value > 100:
            raise ValueError("Комиссия должна быть числом от 0 до 100")

        return value

    @field_validator("min_deposit", "min_withdraw")
    def validate_min_transaction_amount(cls, value: int) -> int:
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Минимальная сумма должна быть больше 0")

        return value

    @field_validator("min_bet", "max_bet")
    def validate_bet(cls, value: int) -> int:
        if not isinstance(value, int) or value < 0:
            raise ValueError("Ставка должна быть положительным числом")

        return value

    @field_validator("min_bet")
    def validate_min_bet(cls, value: int, info: ValidationInfo) -> int:
        if info.data.get("max_bet"):
            if value >= info.data["max_bet"]:
                raise ValueError("Минимальная ставка должна быть меньше максимальной")

        return value

    @field_validator("max_bet")
    def validate_max_bet(cls, value: int, info: ValidationInfo) -> int:
        if value <= info.data["min_bet"]:
            raise ValueError("Максимальная ставка должна быть больше минимальной")

        return value

    @field_validator("pvpc_max_rounds")
    def validate_pvpc_rounds(cls, value: int) -> int:
        if isinstance(value, int) and value < 1:
            raise ValueError("Максимальное количество раундов должно быть числом больше 0")

        return value

    @staticmethod
    def get_first_error_msg(error: ValidationError) -> str:
        return error.errors()[0]["msg"]


class ConfigDTO(BaseModel):
    required_chats: list[int] | None
    card_details: str
    btc_details: str
    start_balance: int
    start_beta_balance: int
    pvb_fee: int
    pvp_fee: int
    pvpc_fee: int
    min_deposit: int
    min_withdraw: int
    card_withdrawal_fee: int
    btc_withdrawal_fee: int
    min_bet: int
    max_bet: int
    pvpc_max_rounds: int
    pvpf_min_bet: int
    pvpf_max_bet: int
    pvpf_creation_probability: int
