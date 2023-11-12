from core.base_service import ToggleableService
from core.redis_keys import RedisKeys


class TransactionsService(ToggleableService):
    def __init__(self):
        super().__init__()
        self._redis_key = RedisKeys.TRANSACTIONS_ACTIVE
