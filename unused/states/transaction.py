from enum import Enum, unique


@unique
class TransactionStatus(int, Enum):
    CREATED = 0
    SUCCEED = 20
    CANCELED_BY_ADMIN = 30


# enums doesn't allow inheritance, so potato code below
@unique
class DepositStatus(int, Enum):
    CREATED = TransactionStatus.CREATED
    APPROVED_BY_SMSR = 10
    SUCCEED = TransactionStatus.SUCCEED
    CANCELED_BY_ADMIN = TransactionStatus.CANCELED_BY_ADMIN


@unique
class WithdrawalStatus(int, Enum):
    CREATED = TransactionStatus.CREATED
    IN_QUEUE = 10
    SUCCEED = TransactionStatus.SUCCEED
    CANCELED_BY_ADMIN = TransactionStatus.CANCELED_BY_ADMIN
    CANCELED_BY_USER = 31
