from core.base_handler import BaseHandler
from services import (
    UserService,
)
from templates import Markups, Messages


class StartHandler(BaseHandler):
    def __init__(self, chat_id: int, user_id: int, user_name: str):
        super().__init__()

        self.chat_id = chat_id
        self.user_id = user_id
        self.user_name = user_name

    def _prepare(self) -> bool:
        # Because start command is the entry point for new users got to create user if it doesn't already exist
        UserService.get_or_create(self.user_id, self.user_name)

        return True

    def _process(self) -> None:
        self._bot.send_message(
            self.chat_id,
            Messages.start,
            Markups.navigation
        )
