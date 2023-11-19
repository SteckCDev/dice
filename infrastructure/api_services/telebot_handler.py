from abc import ABC

from core.base_handler import BaseHandler
from infrastructure.api_services import TeleBotAPI
from settings import settings


class BaseTeleBotHandler(BaseHandler, ABC):
    def __init__(self) -> None:
        self._bot: TeleBotAPI = TeleBotAPI(settings.bot_token)
