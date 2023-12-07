import math

from core.schemas.pvp import (
    PVPDTO,
)
from core.schemas.user import (
    UserCacheDTO,
)
from core.services import (
    ConfigService,
    PVPService,
    UserService,
)
from core.states import PVPStatus
from infrastructure.api_services.telebot import BaseTeleBotHandler
from infrastructure.repositories import (
    ImplementedConfigRepository,
    ImplementedPVPRepository,
    ImplementedUserRepository,
)
from templates import Markups, Messages


class PVPHandler(BaseTeleBotHandler):
    def __init__(self, user_id: int, message_id: int) -> None:
        super().__init__()

        self.user_id: int = user_id
        self.message_id: int = message_id

        config_service: ConfigService = ConfigService(
            repository=ImplementedConfigRepository()
        )
        self.__user_service: UserService = UserService(
            repository=ImplementedUserRepository(),
            bot=self._bot,
            config_service=config_service
        )
        self.__pvp_service: PVPService = PVPService(
            repository=ImplementedPVPRepository(),
            bot=self._bot,
            config_service=config_service,
            user_service=self.__user_service
        )

        self.user_cache: UserCacheDTO = self.__user_service.get_cache_by_tg_id(user_id)

    def _prepare(self) -> bool:
        if not self.__user_service.is_subscribed_to_chats(self.user_id):
            self._bot.send_message(
                self.user_id,
                Messages.force_to_subscribe()
            )
            return False

        if self.user_cache.pvb_in_process:
            self._bot.send_message(
                self.user_id,
                Messages.pvb_in_process()
            )
            return False

        if not self.__pvp_service.get_status():
            self._bot.send_message(
                self.user_id,
                Messages.game_mode_disabled()
            )
            return False

        return True

    def _process(self) -> None:
        available_pvp_games: list[PVPDTO] | None = self.__pvp_service.get_all_for_status(PVPStatus.CREATED)
        available_pvp_games_count = len(available_pvp_games) if available_pvp_games else 0
        pages_total = math.ceil(available_pvp_games_count / 5)

        self._bot.send_message(
            self.user_id,
            Messages.pvp(
                available_pvp_games_count,
                pages_total
            ),
            Markups.pvp(
                self.user_id,
                available_pvp_games,
                pages_total
            )
        )
