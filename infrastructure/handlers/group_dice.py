import html
from typing import Any

from telebot.types import Message

from core.schemas.config import ConfigDTO
from core.schemas.user import (
    UserDTO,
    CreateUserDTO,
    UserCacheDTO,
)
from core.services import (
    ConfigService,
    PVPCService,
    UserService,
)
from infrastructure.api_services.telebot import BaseTeleBotHandler
from infrastructure.repositories import (
    ImplementedConfigRepository,
    ImplementedPVPCRepository,
    ImplementedUserRepository,
)
from templates import Messages


class GroupDiceHandler(BaseTeleBotHandler):
    def __init__(
            self,
            chat_id: int,
            user_id: int,
            user_name: str,
            forwarded_from: Any,
            user_dice: int,
            message: Message
    ) -> None:
        super().__init__()

        self.chat_id: int = chat_id
        self.is_direct: bool = forwarded_from is None
        self.user_dice: int = user_dice
        self.message: Message = message

        config_service: ConfigService = ConfigService(
            repository=ImplementedConfigRepository()
        )
        self.__user_service: UserService = UserService(
            repository=ImplementedUserRepository(),
            bot=self._bot,
            config_service=config_service
        )
        self.__pvpc_service: PVPCService = PVPCService(
            repository=ImplementedPVPCRepository(),
            bot=self._bot,
            config_service=config_service,
            user_service=self.__user_service
        )

        self.config: ConfigDTO = config_service.get()
        self.user: UserDTO = self.__user_service.get_or_create(
            CreateUserDTO(
                tg_id=user_id,
                tg_name=html.escape(user_name),
                balance=self.config.start_balance,
                beta_balance=self.config.start_beta_balance
            )
        )
        self.user_cache: UserCacheDTO = self.__user_service.get_cache_by_tg_id(user_id)

    def _prepare(self) -> bool:
        if not self.is_direct:
            self._bot.reply(
                self.message,
                Messages.dice_not_direct(),
            )
            return False

        return True

    def _process(self) -> None:
        self.__pvpc_service.process_dice(self.user.tg_id, self.chat_id, self.user_dice)
