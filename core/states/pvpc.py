from enum import Enum, unique


@unique
class PVPCStatus(Enum):
    CREATED = 0
    STARTED = 10
    FINISHED = 20
    CANCELED_BY_TTL = 30
    CANCELED_BY_USER = 31
