from enum import Enum, unique


@unique
class PVBStatus(Enum):
    CREATED = 0
    FINISHED = 10
