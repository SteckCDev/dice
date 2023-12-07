import html
import math

from telebot.types import Message

from core.exceptions import (
    BalanceIsNotEnoughError,
    PVPCCancellationRejectedError,
    PVPCAlreadyStartedError,
    PVPCJoinRejectedError,
    PVPCAlreadyInGameError,
    PVPCNotFoundForUserError,
)
from core.schemas.config import (
    ConfigDTO,
)
from core.schemas.pvb import (
    PVBDTO,
)
from core.schemas.pvp import (
    PVPDTO,
)
from core.schemas.pvpc import (
    PVPCDetailsDTO
)
from core.schemas.user import (
    UserDTO,
    CreateUserDTO,
    UserCacheDTO,
)
from core.services import (
    AdminService,
    ConfigService,
    PVBService,
    PVPService,
    PVPCService,
    UserService,
)
from core.states import (
    GameMode,
    PVPStatus,
)
from infrastructure.api_services.telebot import BaseTeleBotHandler
from infrastructure.repositories import (
    ImplementedAdminRepository,
    ImplementedConfigRepository,
    ImplementedPVBRepository,
    ImplementedPVPRepository,
    ImplementedPVPCRepository,
    ImplementedUserRepository,
)
from infrastructure.queues.celery.tasks import mailing
from settings import settings
from templates import Markups, Messages


class CallbackHandler(BaseTeleBotHandler):
    def __init__(
            self,
            call_id: int,
            path: str,
            chat_id: int,
            message_id: int,
            user_id: int,
            user_name: str,
            message: Message
    ) -> None:
        super().__init__()

        self.call_id: int = call_id
        self.path: str = path
        self.path_args = path.split(":")
        self.chat_id: int = chat_id
        self.message_id: int = message_id
        self.message: Message = message

        self.edit_message_in_context = self._bot.get_edit_message_for_context(self.chat_id, self.message_id)

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
            config_service=config_service,
            user_service=self.__user_service
        )
        self.__admin_service: AdminService = AdminService(
            repository=ImplementedAdminRepository(),
            bot=self._bot,
            user_service=self.__user_service,
            config_service=config_service
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

    def __process_pvb(self) -> None:
        self.user_cache.game_mode = GameMode.PVB
        self.__user_service.update_cache(self.user_cache)

        if self.path_args[0] == "pvb":
            self.edit_message_in_context(
                Messages.pvb(
                    self.user.beta_balance if self.user_cache.beta_mode else self.user.balance,
                    self.user_cache.beta_mode
                ),
                Markups.pvb()
            )

        elif self.path_args[0] == "pvb-create":
            self.edit_message_in_context(
                Messages.pvb_create(
                    self.user_cache.pvb_bots_turn_first,
                    self.user_cache.beta_mode,
                    self.user.beta_balance if self.user_cache.beta_mode else self.user.balance,
                    self.user_cache.pvb_bet
                ),
                Markups.pvb_create(self.user_cache.pvb_bots_turn_first)
            )

        elif self.path_args[0] == "pvb-switch-turn":
            self.user_cache.pvb_bots_turn_first = not self.user_cache.pvb_bots_turn_first
            self.__user_service.update_cache(self.user_cache)

            self.edit_message_in_context(
                Messages.pvb_create(
                    self.user_cache.pvb_bots_turn_first,
                    self.user_cache.beta_mode,
                    self.user.beta_balance if self.user_cache.beta_mode else self.user.balance,
                    self.user_cache.pvb_bet
                ),
                Markups.pvb_create(self.user_cache.pvb_bots_turn_first)
            )

        elif self.path_args[0] == "pvb-start":
            try:
                self.__pvb_service.start_game(self.user_cache)
            except ValueError as exc:
                self._bot.answer_callback(
                    self.call_id,
                    str(exc)
                )

        elif self.path_args[0] == "pvb-history":
            wins_percent: float = self.__pvb_service.get_wins_percent_for_tg_id(self.user.tg_id)
            games_pvb: list[PVBDTO] | None = self.__pvb_service.get_last_5_for_tg_id(self.user.tg_id)

            self.edit_message_in_context(
                Messages.pvb_history(wins_percent),
                Markups.pvb_history(games_pvb)
            )

        elif self.path_args[0] == "pvb-instruction":
            self.edit_message_in_context(
                Messages.pvb_instruction(),
                Markups.back_to("pvb")
            )

    def __process_pvp(self) -> None:
        self.user_cache.game_mode = GameMode.PVP
        self.__user_service.update_cache(self.user_cache)

        if self.path_args[0] == "pvp":
            page = int(self.path_args[1]) if len(self.path_args) > 1 else 0

            available_pvp_games = self.__pvp_service.get_all_for_status(PVPStatus.CREATED)
            available_pvp_games_count = len(available_pvp_games) if available_pvp_games else 0
            pages_total = math.ceil(available_pvp_games_count / 5)

            self.edit_message_in_context(
                Messages.pvp(
                    available_pvp_games_count,
                    pages_total,
                    page
                ),
                Markups.pvp(
                    self.user.tg_id,
                    available_pvp_games,
                    pages_total,
                    page
                )
            )

        elif self.path_args[0] == "pvp-details":
            if len(self.path_args) != 2 or not self.path_args[1].isdigit():
                return

            _id = int(self.path_args[1])

            self.user_cache.pvp_game_id = _id
            self.__user_service.update_cache(self.user_cache)

            pvp_details = self.__pvp_service.get_details_for_id(_id)

            self.edit_message_in_context(
                Messages.pvp_details(
                    self.user,
                    pvp_details
                ),
                Markups.pvp_details(
                    self.user,
                    pvp_details
                )
            )

        elif self.path_args[0] == "pvp-cancel":
            if len(self.path_args) != 2 or not self.path_args[1].isdigit():
                return

            _id = int(self.path_args[1])

            self.__pvp_service.cancel_by_creator(_id)

            self.edit_message_in_context(
                Messages.pvp_cancel(_id),
                Markups.back_to("pvp")
            )

        elif self.path_args[0] == "pvp-create":
            self.edit_message_in_context(
                Messages.pvp_create(
                    self.user_cache,
                    self.config.min_bet,
                    self.config.max_bet
                ),
                Markups.pvp_create()
            )

        elif self.path_args[0] == "pvp-confirm":
            try:
                pvp: PVPDTO = self.__pvp_service.create_game(self.user, self.user_cache)
            except ValueError as exc:
                self._bot.answer_callback(
                    self.call_id,
                    str(exc)
                )
                return

            self.edit_message_in_context(
                Messages.pvp_confirm(
                    pvp.id,
                    self.user_cache
                ),
                Markups.back_to("pvp")
            )

        elif self.path_args[0] == "pvp-rating":
            pass

        elif self.path_args[0] == "pvp-history":
            pass

        elif self.path_args[0] == "pvp-instruction":
            self.edit_message_in_context(
                Messages.pvp_instruction(),
                Markups.back_to("pvp")
            )

    def __process_pvpc(self) -> None:
        if self.path_args[0] == "pvpc":
            self._bot.send_message(
                self.chat_id,
                Messages.pvpc(),
                Markups.pvpc()
            )

        elif self.path_args[0] == "pvpc-join":
            if len(self.path_args) != 2 or not self.path_args[1].isdigit():
                return

            _id: int = int(self.path_args[1])

            try:
                pvpc_details: PVPCDetailsDTO = self.__pvpc_service.join_game(_id, self.user)
            except PVPCNotFoundForUserError:
                self._bot.answer_callback(
                    self.call_id,
                    Messages.pvpc_not_found()
                )
            except PVPCJoinRejectedError:
                self._bot.answer_callback(
                    self.call_id,
                    Messages.pvpc_join_rejected()
                )
            except PVPCAlreadyInGameError:
                self._bot.answer_callback(
                    self.call_id,
                    Messages.pvpc_already_in_game()
                )
            except PVPCAlreadyStartedError:
                self._bot.answer_callback(
                    self.call_id,
                    Messages.pvpc_join_rejected()
                )
            except BalanceIsNotEnoughError:
                self._bot.answer_callback(
                    self.call_id,
                    Messages.balance_is_not_enough()
                )
            else:
                self._bot.reply(
                    self.message,
                    Messages.pvpc_start(pvpc_details)
                )

        elif self.path_args[0] == "pvpc-cancel":
            if len(self.path_args) != 2 or not self.path_args[1].isdigit():
                return

            _id: int = int(self.path_args[1])

            try:
                self.__pvpc_service.cancel_game(_id, self.user)
            except PVPCNotFoundForUserError:
                self._bot.answer_callback(
                    self.call_id,
                    Messages.pvpc_not_found()
                )
            except PVPCCancellationRejectedError:
                self._bot.answer_callback(
                    self.call_id,
                    Messages.pvpc_cancellation_rejected()
                )
            except PVPCAlreadyStartedError:
                self._bot.answer_callback(
                    self.call_id,
                    Messages.pvpc_already_started()
                )
            else:
                self._bot.answer_callback(
                    self.call_id,
                    Messages.pvpc_canceled()
                )

    def __process_admin_switches(self) -> None:
        if self.path == "admin-switch-pvb":
            self.__pvb_service.toggle()

        elif self.path == "admin-switch-pvp":
            self.__pvp_service.toggle()

        elif self.path == "admin-switch-pvpc":
            self.__pvpc_service.toggle()

        # elif self.path == "admin-switch-pvpf":
        #     self.__pvpf_service.toggle()
        #
        # elif self.path == "admin-switch-transactions":
        #     self.__transactions_service.toggle()

        self.edit_message_in_context(
            Messages.admin(
                self.__user_service.get_cached_users_count()
            ),
            Markups.admin(
                self.__pvb_service.get_status(),
                self.__pvp_service.get_status(),
                self.__pvpc_service.get_status(),
                False,
                False
            )
        )

    def __process_admin_mailing(self) -> None:
        if self.path_args[0] == "admin-mailing":
            self.edit_message_in_context(
                Messages.admin_mailing(),
                Markups.admin_mailing()
            )

        elif self.path_args[0] == "admin-mailing-preview":
            mail: str | None = self.__admin_service.get_mailing_text()

            if mail is None:
                mail = "Не задан текст рассылки"

            self._bot.send_message(self.user.tg_id, mail)

        elif self.path_args[0] == "admin-mailing-start":
            mailing.delay()

            self.edit_message_in_context(
                Messages.admin_mailing_started(),
                Markups.back_to("admin")
            )

    def __process_admin_misc(self) -> None:
        if self.path_args[0] == "admin":
            self.edit_message_in_context(
                Messages.admin(
                    self.__user_service.get_cached_users_count()
                ),
                Markups.admin(
                    self.__pvb_service.get_status(),
                    self.__pvp_service.get_status(),
                    self.__pvpc_service.get_status(),
                    False,
                    False
                )
            )

    def __process_misc(self) -> None:
        if self.path == "terms-accept":
            self.__user_service.agree_with_terms_and_conditions(self.user.tg_id)

            self.edit_message_in_context(
                Messages.terms_accepted()
            )

            self._bot.send_message(
                self.chat_id,
                Messages.pvb(
                    self.__user_service.get_user_selected_balance(self.user.tg_id),
                    self.user_cache.beta_mode
                ),
                Markups.pvb()
            )

        elif self.path == "terms-reject":
            self.edit_message_in_context(
                Messages.terms_rejected()
            )

        elif self.path == "switch-beta":
            self.user_cache.beta_mode = not self.user_cache.beta_mode

            self.__user_service.update_cache(self.user_cache)

            self.edit_message_in_context(
                Messages.profile(
                    self.user.tg_name,
                    self.user.balance,
                    self.user.beta_balance,
                    self.user.joined_at,
                    self.__pvb_service.get_count_for_tg_id(self.user.tg_id)
                ),
                Markups.profile(self.user_cache.beta_mode)
            )

        elif self.path == "games":
            self.edit_message_in_context(
                Messages.games(
                    self.__user_service.get_user_selected_balance(self.user.tg_id),
                    self.user_cache.beta_mode
                ),
                Markups.games()
            )

    def _prepare(self) -> bool:
        # why not
        if "admin" in self.path and self.user.tg_id != settings.admin_tg_id:
            return False

        if not self.__user_service.is_subscribed_to_chats(self.user.tg_id):
            self._bot.send_message(
                self.user.tg_id,
                Messages.force_to_subscribe()
            )
            return False

        if self.user_cache.pvb_in_process:
            self._bot.send_message(
                self.user.tg_id,
                Messages.pvb_in_process()
            )
            return False

        pvb_requested_and_disabled: bool = self.path.startswith("pvb") and not self.__pvb_service.get_status()
        pvpc_requested_and_disabled: bool = self.path.startswith("pvpc") and not self.__pvpc_service.get_status()
        pvp_requested_and_disabled: bool = self.path.startswith("pvp") and not self.__pvp_service.get_status()

        if pvb_requested_and_disabled or pvpc_requested_and_disabled or pvp_requested_and_disabled:
            self._bot.answer_callback(
                self.call_id,
                Messages.game_mode_disabled()
            )
            return False

        return True
        
    def _process(self) -> None:
        if self.path.startswith("pvb"):
            self.__process_pvb()

        elif self.path.startswith("pvpc"):
            self.__process_pvpc()

        elif self.path.startswith("pvp"):
            self.__process_pvp()

        elif self.path.startswith("admin-switch"):
            self.__process_admin_switches()

        elif self.path.startswith("admin-mailing"):
            self.__process_admin_mailing()

        elif self.path.startswith("admin"):
            self.__process_admin_misc()

        else:
            self.__process_misc()

        # stop loading animation in telegram interface if this handler did no action
        self._bot.answer_callback(self.call_id, "")
