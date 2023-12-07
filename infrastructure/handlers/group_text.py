import html

from telebot.types import Message

from core.schemas.config import ConfigDTO
from core.schemas.pvpc import (
    PVPCDTO,
)
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
from core.states import PVPCStatus
from infrastructure.api_services.telebot import BaseTeleBotHandler
from infrastructure.repositories import (
    RedisConfigRepository,
    PostgresRedisPVPCRepository,
    PostgresRedisUserRepository,
)
from templates import Markups, Messages


class GroupTextHandler(BaseTeleBotHandler):
    def __init__(self, text: str, chat_id: int, user_id: int, user_name: str, message: Message) -> None:
        super().__init__()

        self.text: str = text
        self.chat_id: int = chat_id
        self.message: Message = message

        config_service: ConfigService = ConfigService(
            repository=RedisConfigRepository()
        )
        self.__user_service: UserService = UserService(
            repository=PostgresRedisUserRepository(),
            bot=self._bot,
            config_service=config_service
        )
        self.__pvpc_service: PVPCService = PVPCService(
            repository=PostgresRedisPVPCRepository(),
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
        if not self.text.lower().startswith(("dice", "дайс")):
            return False

        if not self.__pvpc_service.get_status():
            return False

        args: list[str] = self.text.split()

        if len(args) != 3:
            self._bot.reply(
                self.message,
                Messages.pvpc_create()
            )
            return False

        started_pvpc: PVPCDTO = self.__pvpc_service.get_for_tg_id_and_status(self.user.tg_id, PVPCStatus.STARTED)
        created_pvpc: PVPCDTO = self.__pvpc_service.get_for_tg_id_and_status(self.user.tg_id, PVPCStatus.CREATED)

        if started_pvpc or created_pvpc:
            self._bot.reply(
                self.message,
                Messages.pvpc_already_in_game()
            )
            return False

        bet: str = args[1]
        rounds: str = args[2]

        if not bet.isdigit() or not rounds.isdigit():
            self._bot.reply(
                self.message,
                Messages.pvpc_create()
            )
            return False

        bet: int = int(bet)
        rounds: int = int(rounds)

        if bet < self.config.min_bet or bet > self.config.max_bet:
            self._bot.reply(
                self.message,
                Messages.bet_out_of_limits(
                    self.config.min_bet,
                    self.config.max_bet
                )
            )
            return False

        if bet > self.user.balance:
            self._bot.reply(
                self.message,
                Messages.balance_is_not_enough()
            )
            return False

        if rounds < 1 or rounds > self.config.pvpc_max_rounds:
            self._bot.reply(
                self.message,
                Messages.pvpc_rounds_out_of_limits(
                    self.config.pvpc_max_rounds,
                )
            )
            return False

        return True

    def _process(self) -> None:
        bet, rounds = [int(arg) for arg in self.text.split()[1:]]

        pvpc: PVPCDTO = self.__pvpc_service.create_game(self.user, self.chat_id, bet, rounds)

        self._bot.reply(
            self.message,
            Messages.pvpc_join(
                pvpc.id,
                pvpc.bet,
                pvpc.rounds
            ),
            Markups.pvpc_join(pvpc.id)
        )
