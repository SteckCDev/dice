from infrastructure.api_services.telebot_handler import BaseTeleBotHandler
from templates import Markups, Messages


class LotteryHandler(BaseTeleBotHandler):
    def __init__(self, chat_id: int) -> None:
        super().__init__()

        self.chat_id: int = chat_id

    def _prepare(self) -> bool:
        return True

    def _process(self) -> None:
        self._bot.send_message(
            self.chat_id,
            Messages.lottery,
            Markups.lottery
        )
