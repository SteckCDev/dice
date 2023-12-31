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
    TRANSACTIONS_DEPOSIT_CARD_ACTIVE: str = "transaction_service_deposit_card_active"
    TRANSACTIONS_DEPOSIT_BTC_ACTIVE: str = "transaction_service_deposit_btc_active"
    TRANSACTIONS_WITHDRAW_CARD_ACTIVE: str = "transaction_service_withdraw_card_active"
    TRANSACTIONS_WITHDRAW_BTC_ACTIVE: str = "transaction_service_withdraw_btc_active"
    PVPC_CHAT_MIN_BET_TEMPLATE: str = "pvpc_min_bet:{chat_tg_id}"
    PVPC_CHAT_MAX_BET_TEMPLATE: str = "pvpc_max_bet:{chat_tg_id}"
    USER_CACHE_TEMPLATE: str = "user_session:{user_tg_id}"
