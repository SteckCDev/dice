from enum import Enum, unique


@unique
class TransactionStateDirection(int, Enum):
    SELF: int = 0
    DEPOSIT_CARD: int = 1
    DEPOSIT_BTC: int = 2
    WITHDRAW_CARD: int = 3
    WITHDRAW_BTC: int = 4
