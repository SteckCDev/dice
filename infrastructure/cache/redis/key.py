from enum import Enum, unique


@unique
class RedisKey(str, Enum):
    CONFIG: str = "config"
    MAILING_TEXT: str = "mail"
    PVB_ACTIVE: str = "pvb_active"
    PVP_ACTIVE: str = "pvp_active"
    PVPC_ACTIVE: str = "pvpc_active"
    USER_CACHE_TEMPLATE: str = "user:{user_tg_id}"
