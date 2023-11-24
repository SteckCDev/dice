from enum import Enum


class RedisKeys(str, Enum):
    PVB_ACTIVE = "pvb_active"
    PVP_ACTIVE = "pvp_active"
    USER_CACHE = "user:{user_tg_id}"
