from telebot.types import Message

from core.base_handler import BaseHandler
from templates import Markups, Messages


class SupportHandler(BaseHandler):
    def __init__(self, msg: Message):
        super().__init__()

        self.chat_id = msg.chat.id

    def _prepare(self) -> bool:
        return True

    def _process(self) -> None:
        self._bot.send_message(
            self.chat_id,
            Messages.support,
            Markups.support
        )
