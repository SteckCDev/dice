from telebot.types import Message

from core.base_handler import BaseHandler
from services import (
    UserService,
)
from templates import Messages


class BalanceHandler(BaseHandler):
    def __init__(self, msg: Message):
        super().__init__()

        self.chat_id = msg.chat.id

        self.user = UserService.get(msg.from_user.id)

    def _prepare(self) -> bool:
        return True

    def _process(self) -> None:
        self._bot.send_message(
            self.chat_id,
            Messages.balance(self.user.balance, self.user.beta_balance)
        )
