from enum import StrEnum


class RedisKeys(StrEnum):
    CONFIG = "config"
    PVB_ACTIVE = "pvb_active"
    PVP_ACTIVE = "pvp_active"
    PVPC_ACTIVE = "pvpc_active"
    PVPF_ACTIVE = "pvpf_active"
    TRANSACTIONS_ACTIVE = "transactions_active"
    USERS_SINCE_LAUNCH = "users_since_launch"
    USER_CACHE = "user:{user_tg_id}"
