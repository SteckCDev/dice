from core.base_handler import BaseHandler
from services import (
    PVBService,
    PVPService,
    PVPCService,
    PVPFService,
    TransactionsService,
    UserService,
)
from settings import settings
from templates import Markups, Messages


class AdminHandler(BaseHandler):
    def __init__(self):
        super().__init__()

    def _prepare(self) -> bool:
        return True

    def _process(self) -> None:
        self._bot.send_message(
            settings.admin_tg_id,
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
