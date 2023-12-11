from enum import Enum, unique


@unique
class NumbersRelation(str, Enum):
    PVB_BET: str = "pvb_bet"
    PVP_BET: str = "pvp_bet"
    DEPOSIT_AMOUNT: str = "deposit_amount"
    WITHDRAW_AMOUNT: str = "withdraw_amount"
