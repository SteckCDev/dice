from abc import ABC

from core.base_handler import BaseHandler
from settings import settings
from .api import TeleBotAPI


class BaseTeleBotHandler(BaseHandler, ABC):
    def __init__(self) -> None:
        self._bot: TeleBotAPI = TeleBotAPI(
            bot_token=settings.bot_token,
            max_threads=settings.max_threads
        )
