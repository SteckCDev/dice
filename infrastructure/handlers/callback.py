from core.schemas.config import (
    ConfigDTO,
)
from core.schemas.pvb import (
    PVBDTO,
)
from core.schemas.pvp import (
    PVPDTO,
)
from core.schemas.user import (
    UserDTO,
    CreateUserDTO,
    UserCacheDTO,
)
from core.services import (
    ConfigService,
    PVBService,
    PVPService,
    UserService,
)
from core.states.pvp_status import PVPStatus
from core.states.game_mode import GameMode
from infrastructure.api_services.telebot_handler import BaseTeleBotHandler
from infrastructure.repositories import (
    MockConfigRepository,
    PostgresRedisPVBRepository,
    PostgresRedisPVPRepository,
    PostgresRedisUserRepository,
)
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
            user_name: str
    ) -> None:
        super().__init__()

        self.call_id: int = call_id
        self.path: str = path
        self.path_args = path.split(":")
        self.chat_id: int = chat_id
        self.message_id: int = message_id

        self.edit_message_in_context = self._bot.get_edit_message_for_context(self.chat_id, self.message_id)

        config_service: ConfigService = ConfigService(
            repository=MockConfigRepository()
        )
        self.__user_service: UserService = UserService(
            repository=PostgresRedisUserRepository(),
            bot=self._bot,
            config_service=config_service
        )
        self.__pvb_service: PVBService = PVBService(
            repository=PostgresRedisPVBRepository(),
            bot=self._bot,
            config_service=config_service,
            user_service=self.__user_service
        )
        self.__pvp_service: PVPService = PVPService(
            repository=PostgresRedisPVPRepository(),
            bot=self._bot,
            config_service=config_service,
            user_service=self.__user_service
        )

        self.config: ConfigDTO = config_service.get()
        self.user: UserDTO = self.__user_service.get_or_create(
            CreateUserDTO(
                tg_id=user_id,
                tg_name=user_name,
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

            self.user_cache.last_message_id = self.message_id
            self.__user_service.update_cache(self.user_cache)

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
            wins_percent = self.__pvb_service.get_wins_percent_for_tg_id(self.user.tg_id)
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

            self.edit_message_in_context(
                Messages.pvp(
                    0 if available_pvp_games is None else len(available_pvp_games),
                    page
                ),
                Markups.pvp(
                    self.user.tg_id,
                    available_pvp_games,
                    page
                )
            )

        elif self.path_args[0] == "pvp-details":
            _id = int(self.path_args[1])

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
        if self.path == "pvpc":
            self._bot.send_message(
                self.chat_id,
                Messages.pvpc(),
                Markups.pvpc()
            )

    def __process_admin_switches(self) -> None:
        if self.path == "admin-switch-pvb":
            self.__pvb_service.toggle()

        elif self.path == "admin-switch-pvp":
            self.__pvp_service.toggle()

        # elif self.path == "admin-switch-pvpc":
        #     self.__pvpc_service.toggle()
        #
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
                False,
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
        if not self.__user_service.is_subscribed_to_chats(self.user.tg_id):
            self._bot.send_message(
                self.chat_id,
                Messages.force_to_subscribe()
            )
            return False

        if self.user_cache.pvb_in_process:
            self._bot.send_message(
                self.chat_id,
                Messages.pvb_in_process()
            )
            return False

        if "admin" in self.path and self.user.tg_id != settings.admin_tg_id:
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
        else:
            self.__process_misc()

        # stop loading animation in telegram interface if this handler did no action
        self._bot.answer_callback(self.call_id, "")
