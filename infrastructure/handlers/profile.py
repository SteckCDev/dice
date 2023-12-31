import html

from core.schemas.config import (
    ConfigDTO,
)
from core.schemas.user import (
    UserDTO,
    CreateUserDTO,
    UserCacheDTO,
)
from core.services import (
    ConfigService,
    PVBService,
    UserService,
)
from infrastructure.api_services.telebot import BaseTeleBotHandler
from infrastructure.repositories import (
    ImplementedConfigRepository,
    ImplementedPVBRepository,
    ImplementedUserRepository,
)
from templates import Markups, Messages


class ProfileHandler(BaseTeleBotHandler):
    def __init__(self, user_id: int, user_name: str) -> None:
        super().__init__()

        self.user_id: int = user_id

        config_service: ConfigService = ConfigService(
            repository=ImplementedConfigRepository()
        )
        self.__user_service: UserService = UserService(
            repository=ImplementedUserRepository(),
            bot=self._bot,
            config_service=config_service
        )
        self.__pvb_service: PVBService = PVBService(
            repository=ImplementedPVBRepository(),
            bot=self._bot,
            config_service=config_service,
            user_service=self.__user_service
        )

        config: ConfigDTO = config_service.get()

        self.user: UserDTO = self.__user_service.get_or_create(
            CreateUserDTO(
                tg_id=user_id,
                tg_name=html.escape(user_name),
                balance=config.start_balance,
                beta_balance=config.start_beta_balance
            )
        )
        self.user_cache: UserCacheDTO = self.__user_service.get_cache_by_tg_id(user_id)

    def _prepare(self) -> bool:
        if not self.__user_service.is_subscribed_to_chats(self.user.tg_id):
            self._bot.send_message(
                self.user.tg_id,
                Messages.force_to_subscribe(
                    self.__user_service.get_required_chats_title_and_invite_link()
                )
            )
            return False

        if self.user_cache.pvb_in_process:
            self._bot.send_message(
                self.user_id,
                Messages.pvb_in_process()
            )
            return False

        return True

    def _process(self) -> None:
        self._bot.send_message(
            self.user_id,
            Messages.profile(
                self.user.tg_name,
                self.user.balance,
                self.user.beta_balance,
                self.user.joined_at,
                self.__pvb_service.get_count_for_tg_id(self.user.tg_id)
            ),
            Markups.profile(
                self.user_cache.beta_mode
            )
        )
