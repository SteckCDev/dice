from enum import Enum, unique


@unique
class PVPCStatus(int, Enum):
    CREATED: int = 0
    STARTED: int = 10
    FINISHED: int = 20
    FINISHED_BY_BOT: int = 21
    CANCELED_BY_TTL: int = 30
    CANCELED_BY_CREATOR: int = 31
