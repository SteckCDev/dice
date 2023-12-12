from enum import Enum, unique


@unique
class RedisKey(str, Enum):
    CONFIG: str = "config"
    MAILING_TEXT: str = "mailing_text"
    PVB_ACTIVE: str = "pvb_service_active"
    PVP_ACTIVE: str = "pvp_service_active"
    PVPC_ACTIVE: str = "pvpc_service_active"
    PVPF_ACTIVE: str = "pvpf_service_active"
    TRANSACTIONS_ACTIVE: str = "transaction_service_active"
    USER_CACHE_TEMPLATE: str = "user_session:{user_tg_id}"
