from enum import Enum, unique


@unique
class TransactionStatus(int, Enum):
    CREATED: int = 0
    SUCCEED: int = 20
    CANCELED_BY_ADMIN: int = 30


# enums doesn't allow inheritance, so potato code below
@unique
class DepositStatus(int, Enum):
    CREATED: int = TransactionStatus.CREATED.value
    APPROVED_BY_SMSR: int = 10
    SUCCEED: int = TransactionStatus.SUCCEED.value
    CANCELED_BY_ADMIN: int = TransactionStatus.CANCELED_BY_ADMIN.value


@unique
class WithdrawStatus(int, Enum):
    CREATED: int = TransactionStatus.CREATED.value
    IN_QUEUE: int = 10
    SUCCEED: int = TransactionStatus.SUCCEED.value
    CANCELED_BY_ADMIN: int = TransactionStatus.CANCELED_BY_ADMIN.value
    CANCELED_BY_USER: int = 31
