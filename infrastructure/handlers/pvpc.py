from infrastructure.api_services.telebot_handler import BaseTeleBotHandler
from templates import Markups, Messages


class PVPCHandler(BaseTeleBotHandler):
    def __init__(self, chat_id: int) -> None:
        super().__init__()

        self.chat_id = chat_id

    def _prepare(self) -> bool:
        return True

    def _process(self) -> None:
        self._bot.send_message(
            self.chat_id,
            Messages.pvpc,
            Markups.pvpc
        )
