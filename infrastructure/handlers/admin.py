from core.services import (
    ConfigService,
    PVBService,
    PVPService,
    PVPCService,
    PVPFService,
    TransactionService,
    UserService,
)
from infrastructure.api_services.telebot import BaseTeleBotHandler
from infrastructure.repositories import (
    ImplementedConfigRepository,
    ImplementedPVBRepository,
    ImplementedPVPRepository,
    ImplementedPVPCRepository,
    ImplementedPVPFRepository,
    ImplementedTransactionRepository,
    ImplementedUserRepository,
)
from settings import settings
from templates import Markups, Messages


class AdminHandler(BaseTeleBotHandler):
    def __init__(self, user_id: int) -> None:
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
        self.__pvp_service: PVPService = PVPService(
            repository=ImplementedPVPRepository(),
            bot=self._bot,
            config_service=config_service,
            user_service=self.__user_service
        )
        self.__pvpc_service: PVPCService = PVPCService(
            repository=ImplementedPVPCRepository(),
            bot=self._bot,
            user_service=self.__user_service,
            config_service=config_service
        )
        self.__pvpf_service: PVPFService = PVPFService(
            repository=ImplementedPVPFRepository(),
            bot=self._bot,
            user_service=self.__user_service,
            config_service=config_service,
            pvp_service=self.__pvp_service
        )
        self.__transaction_service: TransactionService = TransactionService(
            repository=ImplementedTransactionRepository()
        )

    def _prepare(self) -> bool:
        return self.user_id == settings.admin_tg_id

    def _process(self) -> None:
        self._bot.send_message(
            settings.admin_tg_id,
            Messages.admin(
                self.__user_service.get_cached_users_count()
            ),
            Markups.admin(
                self.__pvb_service.get_status(),
                self.__pvp_service.get_status(),
                self.__pvpc_service.get_status(),
                self.__pvpf_service.get_status(),
                self.__transaction_service.get_status()
            )
        )
