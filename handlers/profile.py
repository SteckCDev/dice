from core.base_handler import BaseHandler
from services import (
    UserService,
)
from templates import Markups, Messages


class ProfileHandler(BaseHandler):
    def __init__(self, chat_id: int):
        super().__init__()

        self.chat_id = chat_id

        self.user_cache = UserService.get_cache(chat_id)

    def _prepare(self) -> bool:
        if self.user_cache.pvb_in_process:
            self._bot.send_message(
                self.chat_id,
                Messages.pvb_in_process
            )
            return False

        return True

    def _process(self) -> None:
        self._bot.send_message(
            self.chat_id,
            Messages.profile(
                UserService.get_profile(self.chat_id)
            ),
            Markups.profile(
                UserService.get_cache(self.chat_id).beta_mode
            )
        )
