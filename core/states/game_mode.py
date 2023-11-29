from enum import Enum, unique


@unique
class GameMode(str, Enum):
    PVB: str = "pvb"
    PVP: str = "pvp"
