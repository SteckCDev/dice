from core.base_handler import BaseHandler
from services import (
    AccessService,
    PVBService,
    UserService,
)
from templates import Markups, Messages


class PVBHandler(BaseHandler):
    def __init__(self, chat_id: int, message_id: int, user_id: int):
        super().__init__()

        self.chat_id = chat_id
        self.message_id = message_id

        self.user = UserService.get(user_id)
        self.user_cache = UserService.get_cache(user_id)

    def _prepare(self) -> bool:
        if not AccessService.subscriptions(self.user.tg_id):
            self._bot.send_message(
                self.chat_id,
                Messages.force_to_subscribe
            )
            return False

        if not AccessService.terms_and_conditions(self.user.tg_id):
            self._bot.send_message(
                self.chat_id,
                Messages.terms_and_conditions,
                Markups.terms_and_conditions
            )
            return False

        if not AccessService.no_pvb_in_process(self.user.tg_id):
            self._bot.send_message(
                self.chat_id,
                Messages.pvb_in_process
            )
            return False

        if not PVBService().status():
            self._bot.send_message(
                self.chat_id,
                Messages.game_mode_disabled
            )
            return False

        return True

    def _process(self) -> None:
        self._bot.send_message(
            self.chat_id,
            Messages.pvb(
                self.user.beta_balance if self.user_cache.beta_mode else self.user.balance,
                self.user_cache.beta_mode
            ),
            Markups.pvb
        )
