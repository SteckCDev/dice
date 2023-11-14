from infrastructure.base_handler import BaseHandler
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
from core.types.mode import Mode


class CallbackHandler(BaseHandler):
    def __init__(self, path: str, chat_id: int, message_id: int, user_id: int):
        super().__init__()

        self.path = path
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

        if self.user_cache.pvb_in_process:
            self._bot.send_message(
                self.chat_id,
                Messages.pvb_in_process
            )
            return False

        if "admin" in self.path and self.user.tg_id != settings.admin_tg_id:
            return False

        return True
        
    def _process(self) -> None:
        if self.path.startswith("pvb"):
            self.user_cache.mode = Mode.PVB
            UserService.update_cache(self.user.tg_id, self.user_cache)
        elif self.path.startswith("pvp"):
            self.user_cache.mode = Mode.PVP
            UserService.update_cache(self.user.tg_id, self.user_cache)

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
            self._bot.edit_message(
                self.chat_id,
                self.message_id,
                Messages.pvb(
                    self.user.beta_balance if self.user_cache.beta_mode else self.user.balance,
                    self.user_cache.beta_mode
                ),
                Markups.pvb
            )

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
                Markups.pvb_create(self.user_cache.pvb_bots_turn_first)
            )

            self.user_cache.last_message_id = self.message_id
            UserService.update_cache(self.user.tg_id, self.user_cache)

        elif self.path == "pvb-switch-turn":
            self.user_cache.pvb_bots_turn_first = not self.user_cache.pvb_bots_turn_first
            UserService.update_cache(self.user.tg_id, self.user_cache)

            self._bot.edit_message(
                self.chat_id,
                self.message_id,
                Messages.pvb_create(
                    self.user_cache.pvb_bots_turn_first,
                    self.user_cache.beta_mode,
                    self.user.beta_balance if self.user_cache.beta_mode else self.user.balance,
                    self.user_cache.pvb_bet
                ),
                Markups.pvb_create(self.user_cache.pvb_bots_turn_first)
            )

        elif self.path == "pvb-start":
            try:
                PVBService().start_game(self.user, self.user_cache)
            except ValueError:
                return

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
