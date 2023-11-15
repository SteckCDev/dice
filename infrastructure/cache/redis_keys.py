from enum import Enum


class RedisKeys(str, Enum):
    PVB_ACTIVE = "pvb_active"
    USERS_SINCE_LAUNCH = "users_since_launch"
    USER_CACHE = "user:{user_tg_id}"
