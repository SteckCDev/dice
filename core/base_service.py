from cache.interface import RedisInterface


class ToggleableService:
    def __init__(self):
        self._redis_interface = RedisInterface()
        self._redis_key = ""

    def status(self) -> bool:
        return self._redis_interface.get_bool(self._redis_key)

    def enable(self) -> None:
        self._redis_interface.set_bool(self._redis_key, True)

    def disable(self) -> None:
        self._redis_interface.set_bool(self._redis_key, False)

    def toggle(self) -> None:
        self._redis_interface.set_bool(
            self._redis_key,
            not self._redis_interface.get_bool(self._redis_key)
        )
