from enum import Enum, unique


@unique
class TransactionStatus(Enum):
    CREATED = 0
    SUCCEED = 20
    CANCELED_BY_ADMIN = 30


@unique
class DepositStatus(TransactionStatus):
    APPROVED_BY_SMSR = 10


@unique
class WithdrawalStatus(TransactionStatus):
    IN_QUEUE = 10
    CANCELED_BY_USER = 31
