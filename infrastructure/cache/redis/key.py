from enum import Enum, unique


@unique
class RedisKey(str, Enum):
    PVB_ACTIVE: str = "pvb_active"
    PVP_ACTIVE: str = "pvp_active"
    USER_CACHE_TEMPLATE: str = "user:{user_tg_id}"
