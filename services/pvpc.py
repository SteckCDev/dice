from core.base_service import ToggleableService
from core.redis_keys import RedisKeys


class PVPCService(ToggleableService):
    def __init__(self):
        super().__init__()
        self._redis_key = RedisKeys.PVPC_ACTIVE
