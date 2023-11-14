from zoneinfo import ZoneInfo
from datetime import datetime


def now() -> datetime:
    return datetime.now(tz=ZoneInfo("Europe/Moscow"))
