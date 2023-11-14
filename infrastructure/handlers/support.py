from infrastructure.base_handler import BaseHandler
from templates import Markups, Messages


class SupportHandler(BaseHandler):
    def __init__(self, chat_id: int):
        super().__init__()

        self.chat_id = chat_id

    def _prepare(self) -> bool:
        return True

    def _process(self) -> None:
        self._bot.send_message(
            self.chat_id,
            Messages.support,
            Markups.support
        )
