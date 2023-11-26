from enum import Enum, unique


@unique
class PVPStatus(int, Enum):
    CREATED = 0
    STARTED = 10
    FINISHED = 20
    FINISHED_BY_BOT = 21
    CANCELED_BY_TTL = 30
    CANCELED_BY_CREATOR = 31
