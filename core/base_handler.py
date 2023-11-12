from abc import ABC, abstractmethod

from core.base_bot import TeleBotAPI
from settings import settings


class BaseHandler(ABC):
    def __init__(self):
        self._bot = TeleBotAPI(settings.bot_token)

    @abstractmethod
    def _prepare(self) -> bool:
        ...

    @abstractmethod
    def _process(self) -> None:
        ...

    def handle(self) -> None:
        if self._prepare():
            self._process()
