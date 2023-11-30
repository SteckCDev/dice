import html
import math
from datetime import datetime
from typing import Any

from telebot.types import Message

from core.schemas.config import ConfigDTO
from core.schemas.pvpc import (
    PVPCDTO,
    UpdatePVPCDTO,
    PVPCDetailsDTO,
)
from core.schemas.user import (
    UserDTO,
    CreateUserDTO,
    UpdateUserDTO,
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
    MockConfigRepository,
    PostgresRedisPVPCRepository,
    PostgresRedisUserRepository,
)
from templates import Messages


class GroupDiceHandler(BaseTeleBotHandler):
    def __init__(
            self,
            text: str,
            chat_id: int,
            user_id: int,
            user_name: str,
            forwarded_from: Any,
            user_dice: int,
            message: Message
    ) -> None:
        super().__init__()

        self.text: str = text
        self.chat_id: int = chat_id
        self.is_direct: bool = forwarded_from is None
        self.user_dice: int = user_dice
        self.message: Message = message

        config_service: ConfigService = ConfigService(
            repository=MockConfigRepository()
        )
        self.__user_service: UserService = UserService(
            repository=PostgresRedisUserRepository(),
            bot=self._bot,
            config_service=config_service
        )
        self.__pvpc_service: PVPCService = PVPCService(
            repository=PostgresRedisPVPCRepository(),
            bot=self._bot
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
        pvpc: PVPCDTO | None = self.__pvpc_service.get_for_tg_id_and_status(self.user.tg_id, PVPCStatus.STARTED)

        if pvpc is None or pvpc.chat_tg_id != self.chat_id:
            return

        if self.user.tg_id == pvpc.creator_tg_id:
            pvpc.creator_dices.append(self.user_dice)
        else:
            pvpc.opponent_dices.append(self.user_dice)

        if len(pvpc.creator_dices) == pvpc.rounds and len(pvpc.opponent_dices) == pvpc.rounds:
            creator: UserDTO = self.__user_service.get_by_tg_id(pvpc.creator_tg_id)
            opponent: UserDTO = self.__user_service.get_by_tg_id(pvpc.opponent_tg_id)

            creator_scored: int = sum(pvpc.creator_dices)
            opponent_scored: int = sum(pvpc.opponent_dices)

            bank: int = math.floor(pvpc.bet * 2 / 100 * (100 - self.config.pvpc_fee))

            winner_tg_name: str | None = None

            if creator_scored > opponent_scored:
                creator.balance += bank
                pvpc.winner_tg_id = pvpc.creator_tg_id
                winner_tg_name = opponent.tg_name
            elif creator_scored < opponent_scored:
                opponent.balance += bank
                pvpc.winner_tg_id = pvpc.opponent_tg_id
                winner_tg_name = creator.tg_name
            else:
                creator.balance += pvpc.bet
                opponent.balance += pvpc.bet

            pvpc.status = PVPCStatus.FINISHED
            pvpc.finished_at = datetime.now()

            self.__user_service.update(
                UpdateUserDTO(
                    **creator.model_dump()
                )
            )
            self.__user_service.update(
                UpdateUserDTO(
                    **opponent.model_dump()
                )
            )

            self._bot.send_message(
                self.chat_id,
                Messages.pvpc_results(
                    PVPCDetailsDTO(
                        **pvpc.model_dump(),
                        creator_scored=creator_scored,
                        opponent_scored=opponent_scored,
                        creator_tg_name=creator.tg_name,
                        opponent_tg_name=opponent.tg_name,
                        winner_tg_name=winner_tg_name
                    )
                )
            )

        self.__pvpc_service.update(
            UpdatePVPCDTO(
                **pvpc.model_dump()
            )
        )
