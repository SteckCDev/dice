from telebot.types import CallbackQuery

from core.base_handler import BaseHandler
from services import (
    AccessService,
    PVBService,
    PVPService,
    PVPCService,
    PVPFService,
    TransactionsService,
    UserService,
)
from settings import settings
from templates import Markups, Messages


class CallbackHandler(BaseHandler):
    def __init__(self, callback: CallbackQuery):
        super().__init__()

        self.path = callback.data
        self.chat_id = callback.message.chat.id
        self.message_id = callback.message.message_id

        self.user = UserService.get(callback.from_user.id)
        self.user_cache = UserService.get_cache(callback.from_user.id)

    def _prepare(self) -> bool:
        if not AccessService.subscriptions(self.user.tg_id):
            self._bot.send_message(
                self.chat_id,
                Messages.force_to_subscribe
            )
            return False

        if "admin" in self.path and self.user.tg_id != settings.admin_tg_id:
            return False

        return True
        
    def _process(self) -> None:
        if self.path == "terms-accept":
            AccessService.agree_with_terms_and_conditions(self.user.tg_id)

            self._bot.edit_message(
                self.chat_id,
                self.message_id,
                Messages.terms_accepted()
            )

        elif self.path == "terms-reject":
            self._bot.edit_message(
                self.chat_id,
                self.message_id,
                Messages.terms_rejected()
            )

        elif self.path == "switch-beta":
            self.user_cache.beta_mode = not self.user_cache.beta_mode

            UserService.update_cache(self.user.tg_id, self.user_cache)

            self._bot.edit_message(
                self.chat_id,
                self.message_id,
                Messages.profile(
                    UserService.get_profile(self.user.tg_id)
                ),
                Markups.profile(self.user_cache.beta_mode)
            )

        elif self.path == "pvb":
            pass  # cmd_pvb(self.callback.message)

        elif self.path == "pvb-create":
            self._bot.edit_message(
                self.chat_id,
                self.message_id,
                Messages.pvb_create(
                    self.user_cache.pvb_bots_turn_first,
                    self.user_cache.beta_mode,
                    self.user.beta_balance if self.user_cache.beta_mode else self.user.balance,
                    self.user_cache.pvb_bet
                ),
                Markups.back_to("pvb")
            )

        elif self.path == "pvb-create-confirm":
            pass
            # if user.bet >= options.min_bet:
            # if user.bet <= options.max_bet:
            # if user.selected_balance >= user.bet:

        elif self.path == "pvb-history":
            pass

        elif self.path == "pvb-instruction":
            self._bot.edit_message(
                self.chat_id,
                self.message_id,
                Messages.pvb_instruction,
                Markups.back_to("pvb")
            )

        elif self.path == "admin-switch-pvb":
            PVBService().toggle()

        elif self.path == "admin-switch-pvp":
            PVPService().toggle()

        elif self.path == "admin-switch-pvpc":
            PVPCService().toggle()

        elif self.path == "admin-switch-pvpf":
            PVPFService().toggle()

        elif self.path == "admin-switch-transactions":
            TransactionsService().toggle()

        #
        #
        #

        if self.path.startswith("admin-switch"):
            self._bot.edit_message(
                settings.admin_tg_id,
                self.message_id,
                Messages.admin(
                    UserService.users_since_launch()
                ),
                Markups.admin(
                    *[
                        service().status() for service in (
                            PVBService, PVPService, PVPCService, PVPFService, TransactionsService
                        )
                    ]
                )
            )
