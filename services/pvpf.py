from core.base_service import ToggleableService
from core.redis_keys import RedisKeys


class PVPFService(ToggleableService):
    def __init__(self):
        super().__init__()
        self._redis_key = RedisKeys.PVPF_ACTIVE
