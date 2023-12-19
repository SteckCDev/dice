import html
import math
import json
from contextlib import suppress
from datetime import datetime
from decimal import Decimal

from telebot.apihelper import ApiTelegramException
from telebot.types import Message, CallbackQuery

from core.exceptions import (
    BalanceIsNotEnoughError,
    PVPCCancellationRejectedError,
    PVPCAlreadyStartedError,
    PVPCJoinRejectedError,
    PVPCAlreadyInGameError,
    PVPCNotFoundForUserError,
)
from core.schemas.details import (
    DetailsDTO,
    CreateDetailsDTO,
    UpdateDetailsDTO,
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
from core.schemas.transaction import (
    TransactionDTO,
    CreateTransactionDTO,
    UpdateTransactionDTO,
)
from core.schemas.user import (
    UserDTO,
    CreateUserDTO,
    UpdateUserDTO,
    UserCacheDTO,
)
from core.services import (
    AdminService,
    ConfigService,
    CurrencyService,
    DetailsService,
    PVBService,
    PVPService,
    PVPCService,
    PVPFService,
    TransactionService,
    UserService,
)
from core.services.admin import ADJUSTABLE_COMMANDS
from core.states import (
    NumbersRelation,
    PVPStatus,
    TransactionStateDirection,
    TransactionStatus,
    WithdrawStatus,
)
from infrastructure.api_services.telebot import BaseTeleBotHandler
from infrastructure.queues.celery.tasks import mailing
from infrastructure.repositories import (
    ImplementedAdminRepository,
    ImplementedConfigRepository,
    ImplementedCurrencyRepository,
    ImplementedDetailsRepository,
    ImplementedPVBRepository,
    ImplementedPVPRepository,
    ImplementedPVPCRepository,
    ImplementedPVPFRepository,
    ImplementedTransactionRepository,
    ImplementedUserRepository,
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
            user_name: str,
            call: CallbackQuery
    ) -> None:
        super().__init__()

        self.call_id: int = call_id
        self.path: str = path
        self.path_args: list[str] = path.split(":")
        self.chat_id: int = chat_id
        self.message_id: int = message_id
        self.message: Message = call.message

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
        self.__pvpf_service: PVPFService = PVPFService(
            repository=ImplementedPVPFRepository(),
            bot=self._bot,
            user_service=self.__user_service,
            config_service=config_service,
            pvp_service=self.__pvp_service
        )
        self.__admin_service: AdminService = AdminService(
            repository=ImplementedAdminRepository(),
            bot=self._bot,
            user_service=self.__user_service,
            config_service=config_service
        )
        self.__currency_service: CurrencyService = CurrencyService(
            repository=ImplementedCurrencyRepository()
        )
        self.__transaction_service: TransactionService = TransactionService(
            repository=ImplementedTransactionRepository()
        )
        self.__details_service: DetailsService = DetailsService(
            repository=ImplementedDetailsRepository()
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

        self.user_cache.callback_json = json.dumps(call.json)
        self.__user_service.update_cache(
            self.user_cache
        )

    def __process_pvb(self) -> None:
        self.user_cache.numbers_relation = NumbersRelation.PVB_BET
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
                    self.user_cache.pvb_bet,
                    self.config.min_bet,
                    self.config.max_bet
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
                    self.user_cache.pvb_bet,
                    self.config.min_bet,
                    self.config.max_bet
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
            wins_percent: float = self.__pvb_service.get_result_percent_for_tg_id_or_bot(self.user.tg_id)
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
        self.user_cache.numbers_relation = NumbersRelation.PVP_BET
        self.__user_service.update_cache(self.user_cache)

        if self.path_args[0] == "pvp":
            page = int(self.path_args[1]) if len(self.path_args) > 1 else 1

            available_pvp_games = self.__pvp_service.get_all_for_status(PVPStatus.CREATED)
            available_pvp_games_count = len(available_pvp_games) if available_pvp_games else 0
            pages_total = math.ceil(available_pvp_games_count / 5)

            with suppress(ApiTelegramException):
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
            if len(self.path_args) not in (2, 3) or not self.path_args[1].isdigit():
                return

            _id = int(self.path_args[1])
            _page = int(self.path_args[2])

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
                    pvp_details,
                    _page
                )
            )

        elif self.path_args[0] == "pvp-cancel":
            if len(self.path_args) != 2 or not self.path_args[1].isdigit():
                return

            _id = int(self.path_args[1])

            self.__pvp_service.cancel_by_creator(_id, self.user.tg_id)

            self.edit_message_in_context(
                Messages.pvp_cancel(_id),
                Markups.back_to("pvp")
            )

        elif self.path_args[0] == "pvp-create":
            self.edit_message_in_context(
                Messages.pvp_create(
                    self.user_cache,
                    self.__user_service.get_user_selected_balance(self.user.tg_id),
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
            limit: int = 5

            finished: list[PVPDTO] | None = self.__pvp_service.get_all_for_status(PVPStatus.FINISHED)
            finished_by_bot: list[PVPDTO] | None = self.__pvp_service.get_all_for_status(PVPStatus.FINISHED_BY_BOT)

            if finished:
                if finished_by_bot:
                    finished.extend(finished_by_bot)

                all_finished: list[PVPDTO] | None = finished
            else:
                if finished_by_bot:
                    all_finished: list[PVPDTO] | None = finished_by_bot
                else:
                    all_finished: list[PVPDTO] | None = None

            if all_finished is None:
                self.edit_message_in_context(
                    Messages.pvp_rating(True),
                    Markups.pvp_rating(None)
                )
                return

            all_winners: dict[int, int] = dict()
            leaders: list[tuple[int, str]] = list()

            for pvp in all_finished:
                if pvp.winner_tg_id is None:
                    continue

                all_winners[pvp.winner_tg_id] = all_winners.get(pvp.winner_tg_id, 0) + pvp.bet

            leaders_raw: list[tuple[int, int]] = sorted(
                all_winners.items(), key=lambda user: user[1], reverse=True
            )[:limit]

            for leader_id, leader_winnings in leaders_raw:
                leaders.append(
                    (
                        leader_winnings,
                        self.__user_service.get_by_tg_id(leader_id).tg_name
                    )
                )

            self.edit_message_in_context(
                Messages.pvp_rating(leaders is None),
                Markups.pvp_rating(leaders)
            )

        elif self.path_args[0] == "pvp-history":
            wins_percent: float = self.__pvp_service.get_wins_percent_for_tg_id(self.user.tg_id)
            games_pvp: list[PVBDTO] | None = self.__pvp_service.get_last_5_for_tg_id(self.user.tg_id)

            self.edit_message_in_context(
                Messages.pvp_history(wins_percent),
                Markups.pvp_history(games_pvp, self.user.tg_id)
            )

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

    def __process_transaction(self) -> None:
        if self.path_args[0] == "transaction":
            self.edit_message_in_context(
                Messages.transaction(self.user.balance, self.config.min_deposit, self.config.min_withdraw),
                Markups.transaction()
            )

        elif self.path_args[0] == "transaction-history":
            transactions: list[TransactionDTO] | None = self.__transaction_service.get_last_5_for_tg_id(
                self.user.tg_id
            )

            self.edit_message_in_context(
                Messages.transaction_history(),
                Markups.transaction_history(transactions)
            )

        elif self.path_args[0] == "transaction-history-manage":
            transaction_id: int = int(self.path_args[1])

            transaction: TransactionDTO | None = self.__transaction_service.get_by_id(transaction_id)

            if transaction is None or transaction.user_tg_id != self.user.tg_id:
                return

            amount_with_fee: int = int((transaction.rub / 100) * (100 - transaction.fee))

            self.edit_message_in_context(
                Messages.transaction_history_manage(
                    transaction.method,
                    transaction.rub,
                    transaction.fee,
                    amount_with_fee,
                    transaction.recipient_details,
                    transaction.recipient_bank,
                    transaction.btc
                ),
                Markups.transaction_history_manage(transaction.id)
            )

        elif self.path_args[0] == "transaction-history-cancel":
            transaction_id: int = int(self.path_args[1])

            transaction: TransactionDTO | None = self.__transaction_service.get_by_id(transaction_id)

            if transaction.user_tg_id != self.user.tg_id:
                return

            if transaction is None or transaction.status != TransactionStatus.CREATED:
                self._bot.answer_callback(
                    self.call_id,
                    Messages.transaction_already_processed()
                )
                return

            transaction.status = WithdrawStatus.CANCELED_BY_USER
            self.user.balance += transaction.rub

            self.__transaction_service.update(
                UpdateTransactionDTO(
                    **transaction.model_dump()
                )
            )
            self.__user_service.update(
                UpdateUserDTO(
                    **self.user.model_dump()
                )
            )

            self._bot.send_message(
                settings.admin_tg_id,
                Messages.admin_transaction_canceled_by_user(transaction.id)
            )

            self.edit_message_in_context(
                Messages.transaction_canceled(),
                Markups.back_to("transaction-history")
            )

    def __process_deposit(self) -> None:
        self.user_cache.numbers_relation = NumbersRelation.DEPOSIT_AMOUNT
        self.__user_service.update_cache(self.user_cache)

        if self.path_args[0] == "transaction-deposit":
            self.edit_message_in_context(
                Messages.transaction_deposit(),
                Markups.transaction_deposit()
            )
            return

        # "transaction-deposit-amount:{method}",
        # "transaction-deposit-amount-confirm:{method}",
        # "transaction-deposit-confirm:{method}",
        # "transaction-deposit-create:{method}"

        method: str = self.path_args[1]

        if method not in ("card", "btc"):
            return

        btc_equivalent: Decimal | None = None if method == "card" else self.__currency_service.rub_to_btc(
            self.user_cache.deposit_amount
        )

        if method == "btc" and btc_equivalent is None:
            self.edit_message_in_context(
                Messages.on_issue(),
                Markups.support()
            )
            return

        if self.path_args[0] == "transaction-deposit-amount":
            self.edit_message_in_context(
                Messages.transaction_deposit_amount(
                    self.config.min_deposit,
                    self.user_cache.deposit_amount,
                    btc_equivalent
                ),
                Markups.transaction_deposit_amount(
                    method,
                    self.config.min_deposit,
                    self.user_cache.deposit_amount
                )
            )

        elif self.path_args[0] == "transaction-deposit-amount-confirm":
            self.edit_message_in_context(
                Messages.transaction_deposit_confirm_amount(
                    self.user_cache.deposit_amount,
                    btc_equivalent
                ),
                Markups.transaction_deposit_confirm_amount(method)
            )

        elif self.path_args[0] == "transaction-deposit-confirm":
            self.edit_message_in_context(
                Messages.transaction_deposit_confirm(
                    method,
                    self.user_cache.deposit_amount if method == "card" else btc_equivalent,
                    self.config.card_details if method == "card" else self.config.btc_details
                ),
                Markups.transaction_deposit_confirm(method)
            )

        elif self.path_args[0] == "transaction-deposit-create":
            transaction: TransactionDTO = self.__transaction_service.create(
                CreateTransactionDTO(
                    user_tg_id=self.user.tg_id,
                    type="deposit",
                    method=method,
                    rub=self.user_cache.deposit_amount,
                    btc=btc_equivalent,
                    fee=0,
                    recipient_details=self.config.card_details if method == "card" else self.config.btc_details,
                    recipient_bank=None
                )
            )

            self.edit_message_in_context(
                Messages.transaction_create(transaction.id)
            )

            self._bot.send_message(
                settings.admin_tg_id,
                Messages.admin_transaction_deposit_confirm(
                    transaction.id,
                    self.user.tg_id,
                    self.user.tg_name,
                    transaction.created_at,
                    transaction.method,
                    transaction.rub,
                    transaction.btc
                ),
                Markups.admin_transaction_confirm(transaction.id)
            )

    def __process_withdraw(self) -> None:
        self.user_cache.numbers_relation = NumbersRelation.WITHDRAW_AMOUNT
        self.__user_service.update_cache(self.user_cache)

        if self.path_args[0] == "transaction-withdraw":
            self.edit_message_in_context(
                Messages.transaction_withdraw(self.user.balance),
                Markups.transaction_withdraw(self.config.card_withdrawal_fee, self.config.btc_withdrawal_fee)
            )
            return

        # transaction-withdraw-amount
        # transaction-withdraw-details
        # transaction-withdraw-confirm

        method: str = self.path_args[1]

        if method not in ("card", "btc"):
            return

        btc_equivalent: Decimal | None = None if method == "card" else self.__currency_service.rub_to_btc(
            self.user_cache.withdraw_amount
        )

        if method == "btc" and btc_equivalent is None:
            self.edit_message_in_context(
                Messages.on_issue(),
                Markups.support()
            )
            return

        if self.path_args[0] == "transaction-withdraw-amount":
            self.edit_message_in_context(
                Messages.transaction_withdraw_amount(
                    self.config.min_withdraw,
                    self.config.card_withdrawal_fee if method == "card" else self.config.btc_withdrawal_fee,
                    self.user.balance,
                    self.user_cache.withdraw_amount,
                    btc_equivalent
                ),
                Markups.transaction_withdraw_amount(
                    method,
                    self.user_cache.withdraw_amount,
                    self.user.balance,
                    self.config.min_withdraw
                )
            )

        elif self.path_args[0] in (
                "transaction-withdraw-details",
                "transaction-withdraw-details-create",
                "transaction-withdraw-details-save"
        ):
            path_has_details_id: bool = len(self.path_args) == 3 and self.path_args[2].isdigit()

            if self.path_args[0].endswith("create"):
                self.__details_service.create(
                    CreateDetailsDTO(
                        user_tg_id=self.user.tg_id,
                        method=method,
                        withdraw_details=self.user_cache.withdraw_details,
                        withdraw_bank=self.user_cache.withdraw_bank if method == "card" else None
                    )
                )

            elif self.path_args[0].endswith("save") and path_has_details_id:
                _id: int = int(self.path_args[2])

                details_to_use: DetailsDTO | None = self.__details_service.get_by_id(_id)

                if details_to_use and details_to_use.user_tg_id == self.user.tg_id:
                    self.__details_service.update(
                        UpdateDetailsDTO(
                            id=details_to_use.id,
                            withdraw_details=self.user_cache.withdraw_details,
                            withdraw_bank=self.user_cache.withdraw_bank if method == "card" else None
                        )
                    )

            elif path_has_details_id:
                _id: int = int(self.path_args[2])

                details_to_use: DetailsDTO | None = self.__details_service.get_by_id(_id)

                if details_to_use:
                    self.user_cache.withdraw_details = details_to_use.withdraw_details

                    if method == "card":
                        self.user_cache.withdraw_bank = details_to_use.withdraw_bank

                    self.__user_service.update_cache(self.user_cache)

            saved_details: DetailsDTO | None = self.__details_service.get_all_for_tg_id_and_method(
                self.user.tg_id, method
            )

            self.edit_message_in_context(
                Messages.transaction_withdraw_details(
                    method,
                    self.user_cache.withdraw_details,
                    self.user_cache.withdraw_bank
                ),
                Markups.transaction_withdraw_details(
                    method,
                    self.user_cache.withdraw_details,
                    self.user_cache.withdraw_bank,
                    saved_details
                )
            )

        elif self.path_args[0] == "transaction-withdraw-details-add":
            self.edit_message_in_context(
                Messages.transaction_withdraw_details(
                    method,
                    self.user_cache.withdraw_details,
                    self.user_cache.withdraw_bank
                ),
                Markups.transaction_withdraw_details_add(
                    method,
                    self.user_cache.withdraw_details,
                    self.user_cache.withdraw_bank
                )
            )

        elif self.path_args[0] in (
                "transaction-withdraw-details-manage",
                "transaction-withdraw-details-edit"
        ):
            if len(self.path_args) != 3 or not self.path_args[2].isdigit():
                return

            _id = int(self.path_args[2])

            saved_details: DetailsDTO | None = self.__details_service.get_by_id(_id)

            if saved_details is None or saved_details.user_tg_id != self.user.tg_id:
                return

            if self.path_args[0].endswith("manage"):
                self.user_cache.withdraw_details = saved_details.withdraw_details

                if method == "card":
                    self.user_cache.withdraw_bank = saved_details.withdraw_bank

                self.__user_service.update_cache(self.user_cache)

            self.edit_message_in_context(
                Messages.transaction_withdraw_details(
                    method,
                    self.user_cache.withdraw_details,
                    self.user_cache.withdraw_bank
                ),
                Markups.transaction_withdraw_details_manage(
                    method,
                    saved_details.id
                )
            )

        elif self.path_args[0] == "transaction-withdraw-confirm":
            fee: int = self.config.card_withdrawal_fee if method == "card" else self.config.btc_withdrawal_fee
            amount_with_fee: int = int((self.user_cache.withdraw_amount / 100) * (100 - fee))

            self.edit_message_in_context(
                Messages.transaction_withdraw_confirm(
                    method,
                    self.user.balance,
                    self.user_cache.withdraw_amount,
                    fee,
                    amount_with_fee,
                    self.user_cache.withdraw_details,
                    self.user_cache.withdraw_bank,
                    btc_equivalent
                ),
                Markups.transaction_withdraw_confirm(method)
            )

        elif self.path_args[0] == "transaction-withdraw-create":
            fee: int = self.config.card_withdrawal_fee if method == "card" else self.config.btc_withdrawal_fee
            amount_with_fee: int = int((self.user_cache.withdraw_amount / 100) * (100 - fee))
            btc_equivalent_with_fee: Decimal | None = (btc_equivalent / 100) * (100 - fee) if btc_equivalent else None

            transaction: TransactionDTO = self.__transaction_service.create(
                CreateTransactionDTO(
                    user_tg_id=self.user.tg_id,
                    type="withdraw",
                    method=method,
                    rub=self.user_cache.withdraw_amount,
                    btc=btc_equivalent,
                    fee=fee,
                    recipient_details=self.user_cache.withdraw_details,
                    recipient_bank=self.user_cache.withdraw_bank
                )
            )

            self.user.balance -= transaction.rub

            self.__user_service.update(
                UpdateUserDTO(
                    **self.user.model_dump()
                )
            )

            self.edit_message_in_context(
                Messages.transaction_create(transaction.id)
            )

            self._bot.send_message(
                settings.admin_tg_id,
                Messages.admin_transaction_withdraw_confirm(
                    transaction.id,
                    self.user.tg_id,
                    self.user.tg_name,
                    transaction.created_at,
                    transaction.method,
                    transaction.rub,
                    transaction.fee,
                    amount_with_fee,
                    transaction.recipient_details,
                    transaction.recipient_bank,
                    transaction.btc,
                    btc_equivalent_with_fee
                ),
                Markups.admin_transaction_confirm(transaction.id)
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

        elif self.path == "profile":
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

    def __process_admin_switch(self) -> None:
        if self.path == "admin-switch-pvb":
            self.__pvb_service.toggle()

        elif self.path == "admin-switch-pvp":
            self.__pvp_service.toggle()

        elif self.path == "admin-switch-pvpc":
            self.__pvpc_service.toggle()

        elif self.path == "admin-switch-pvpf":
            self.__pvpf_service.toggle()

        elif self.path == "admin-switch-transactions":
            self.__transaction_service.toggle(TransactionStateDirection.SELF)

        elif self.path == "admin-switch-transactions-deposit-card":
            self.__transaction_service.toggle(TransactionStateDirection.DEPOSIT_CARD)

        elif self.path == "admin-switch-transactions-deposit-btc":
            self.__transaction_service.toggle(TransactionStateDirection.DEPOSIT_BTC)

        elif self.path == "admin-switch-transactions-withdraw-card":
            self.__transaction_service.toggle(TransactionStateDirection.WITHDRAW_CARD)

        elif self.path == "admin-switch-transactions-withdraw-btc":
            self.__transaction_service.toggle(TransactionStateDirection.WITHDRAW_BTC)

        self.edit_message_in_context(
            Messages.admin(
                self.__user_service.get_cached_users_count(),
                ADJUSTABLE_COMMANDS
            ),
            Markups.admin(
                self.__pvb_service.get_status(),
                self.__pvp_service.get_status(),
                self.__pvpc_service.get_status(),
                self.__pvpf_service.get_status(),
                self.__transaction_service.get_status(TransactionStateDirection.SELF),
                self.__transaction_service.get_status(TransactionStateDirection.DEPOSIT_CARD),
                self.__transaction_service.get_status(TransactionStateDirection.DEPOSIT_BTC),
                self.__transaction_service.get_status(TransactionStateDirection.WITHDRAW_CARD),
                self.__transaction_service.get_status(TransactionStateDirection.WITHDRAW_BTC),
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
                    self.__user_service.get_cached_users_count(),
                    ADJUSTABLE_COMMANDS
                ),
                Markups.admin(
                    self.__pvb_service.get_status(),
                    self.__pvp_service.get_status(),
                    self.__pvpc_service.get_status(),
                    self.__pvpf_service.get_status(),
                    self.__transaction_service.get_status(TransactionStateDirection.SELF),
                    self.__transaction_service.get_status(TransactionStateDirection.DEPOSIT_CARD),
                    self.__transaction_service.get_status(TransactionStateDirection.DEPOSIT_BTC),
                    self.__transaction_service.get_status(TransactionStateDirection.WITHDRAW_CARD),
                    self.__transaction_service.get_status(TransactionStateDirection.WITHDRAW_BTC)
                )
            )

        elif self.path_args[0] == "admin-stats":
            self.edit_message_in_context(
                Messages.admin_stats(
                    users_count=self.__user_service.get_count(),
                    pvb_fees_income=0,
                    pvp_fees_income=0,
                    pvpc_fees_income=0,
                    withdraws_final_outcome=0,
                    pvb_count=self.__pvb_service.get_count(),
                    pvp_count=self.__pvp_service.get_count(),
                    pvpc_count=self.__pvpc_service.get_count(),
                    pvb_total_bank=self.__pvb_service.get_bet_sum(),
                    pvp_total_bank=self.__pvp_service.get_bet_sum(),
                    pvpc_total_bank=self.__pvpc_service.get_bet_sum(),
                    pvb_bot_income=self.__pvb_service.get_bet_sum_for_result(False),
                    pvb_bot_wins_percent=self.__pvb_service.get_result_percent_for_tg_id_or_bot(None),
                    pvb_bot_defeats_percent=self.__pvb_service.get_result_percent_for_tg_id_or_bot(None, False),
                    pvb_draws_percent=self.__pvb_service.get_result_percent_for_tg_id_or_bot(None, None),
                ),
                Markups.back_to("admin")
            )

        elif self.path_args[0] == "admin-transactions":
            pending_transactions: list[TransactionDTO] | None = self.__transaction_service.get_all_for_status(
                TransactionStatus.CREATED
            )

            self.edit_message_in_context(
                Messages.admin_transactions(),
                Markups.admin_transactions(pending_transactions)
            )

        elif self.path_args[0] == "admin-transactions-manage":
            transaction_id: int = int(self.path_args[1])

            transaction: TransactionDTO | None = self.__transaction_service.get_by_id(transaction_id)

            if transaction is None or transaction.status != TransactionStatus.CREATED:
                self._bot.answer_callback(
                    self.call_id,
                    Messages.admin_transaction_already_processed()
                )
                return

            if transaction.type == "deposit":
                self._bot.send_message(
                    settings.admin_tg_id,
                    Messages.admin_transaction_deposit_confirm(
                        transaction.id,
                        self.user.tg_id,
                        self.user.tg_name,
                        transaction.created_at,
                        transaction.method,
                        transaction.rub,
                        transaction.btc
                    ),
                    Markups.admin_transaction_confirm(transaction.id)
                )
            else:
                amount_with_fee: int = int((transaction.rub / 100) * (100 - transaction.fee))
                btc_equivalent_with_fee: Decimal | None = (
                        transaction.btc / 100
                    ) * (100 - transaction.fee) if transaction.btc else None

                self._bot.send_message(
                    settings.admin_tg_id,
                    Messages.admin_transaction_withdraw_confirm(
                        transaction.id,
                        self.user.tg_id,
                        self.user.tg_name,
                        transaction.created_at,
                        transaction.method,
                        transaction.rub,
                        transaction.fee,
                        amount_with_fee,
                        transaction.recipient_details,
                        transaction.recipient_bank,
                        transaction.btc,
                        btc_equivalent_with_fee
                    ),
                    Markups.admin_transaction_confirm(transaction.id)
                )

        elif self.path_args[0] in (
                "admin-transaction-approve",
                "admin-transaction-reject"
        ):
            transaction_id: int = int(self.path_args[1])

            transaction: TransactionDTO = self.__transaction_service.get_by_id(transaction_id)

            if transaction is None or transaction.status != TransactionStatus.CREATED:
                self._bot.answer_callback(
                    self.call_id,
                    Messages.admin_transaction_not_found()
                )
                return

            user: UserDTO = self.__user_service.get_by_tg_id(transaction.user_tg_id)
            approved: bool = self.path_args[0] == "admin-transaction-approve"

            if approved:
                transaction.status = TransactionStatus.SUCCEED

                if transaction.type == "deposit":
                    user.balance += transaction.rub
            else:
                transaction.status = TransactionStatus.CANCELED_BY_ADMIN

                if transaction.type == "withdraw":
                    user.balance += transaction.rub

            transaction.processed_at = datetime.now()

            self.__transaction_service.update(
                UpdateTransactionDTO(
                    **transaction.model_dump()
                )
            )
            self.__user_service.update(
                UpdateUserDTO(
                    **user.model_dump()
                )
            )

            self._bot.send_message(
                user.tg_id,
                Messages.transaction_processed(transaction.id, approved)
            )

            if transaction.type == "deposit":
                self.edit_message_in_context(
                    Messages.admin_transaction_deposit_confirm(
                        transaction.id,
                        user.tg_id,
                        user.tg_name,
                        transaction.created_at,
                        transaction.method,
                        transaction.rub,
                        transaction.btc,
                        done=True
                    ),
                    Markups.admin_transaction_confirm(transaction.id, done=True)
                )
            else:
                amount_with_fee: int = int((transaction.rub / 100) * (100 - transaction.fee))
                btc_equivalent_with_fee: Decimal | None = None

                if transaction.btc:
                    btc_equivalent_with_fee = (transaction.btc / 100) * (100 - transaction.fee)

                self.edit_message_in_context(
                    Messages.admin_transaction_withdraw_confirm(
                        transaction.id,
                        self.user.tg_id,
                        self.user.tg_name,
                        transaction.created_at,
                        transaction.method,
                        transaction.rub,
                        transaction.fee,
                        amount_with_fee,
                        transaction.recipient_details,
                        transaction.recipient_bank,
                        transaction.btc,
                        btc_equivalent_with_fee
                    ),
                    Markups.admin_transaction_confirm(transaction.id, done=True)
                )

    def _prepare(self) -> bool:
        # why not
        if "admin" in self.path and self.user.tg_id != settings.admin_tg_id:
            return False

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
                self.user.tg_id,
                Messages.pvb_in_process()
            )
            return False

        if self.path.startswith("pvb") and not self.__user_service.is_terms_and_conditions_agreed(self.user.tg_id):
            self._bot.send_message(
                self.chat_id,
                Messages.terms_and_conditions(),
                Markups.terms_and_conditions()
            )
            return False

        pvb_requested_and_disabled: bool = self.path.startswith("pvb") and not self.__pvb_service.get_status()
        pvpc_requested_and_disabled: bool = self.path.startswith("pvpc") and not self.__pvpc_service.get_status()
        pvp_requested_and_disabled: bool = self.path.startswith("pvp") and \
            not self.path.startswith("pvpc") and not self.__pvp_service.get_status()

        if pvb_requested_and_disabled or pvpc_requested_and_disabled or pvp_requested_and_disabled:
            self._bot.answer_callback(
                self.call_id,
                Messages.game_mode_disabled()
            )
            return False

        if self.path.startswith("transaction") and not self.__transaction_service.get_status(
                TransactionStateDirection.SELF
        ):
            self._bot.answer_callback(
                self.call_id,
                Messages.transactions_disabled()
            )
            return False

        if self.path.startswith(
                ("transaction-deposit", "transaction-withdraw")
        ):
            if self.path.startswith("transaction-deposit"):
                card_state_for_type: TransactionStateDirection = TransactionStateDirection.DEPOSIT_CARD
                btc_state_for_type: TransactionStateDirection = TransactionStateDirection.DEPOSIT_BTC
            else:
                card_state_for_type: TransactionStateDirection = TransactionStateDirection.WITHDRAW_CARD
                btc_state_for_type: TransactionStateDirection = TransactionStateDirection.WITHDRAW_BTC

            card_state: bool = self.__transaction_service.get_status(card_state_for_type)
            btc_state: bool = self.__transaction_service.get_status(btc_state_for_type)

            if not card_state and not btc_state:
                self.edit_message_in_context(
                    Messages.transactions_direction_disabled(),
                    Markups.back_to("transaction")
                )
                return False

            elif len(self.path_args) >= 2 and (
                    (self.path_args[1] == "card" and not card_state) or (self.path_args[1] == "btc" and not btc_state)
            ):
                back_to: str = "transaction-deposit" if self.path.startswith(
                    "transaction-deposit"
                ) else "transaction-withdraw"

                self.edit_message_in_context(
                    Messages.transactions_direction_disabled(),
                    Markups.back_to(back_to)
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

        elif self.path.startswith("transaction-deposit"):
            self.__process_deposit()

        elif self.path.startswith("transaction-withdraw"):
            self.__process_withdraw()

        elif self.path.startswith("transaction"):
            self.__process_transaction()

        elif self.path.startswith("admin-switch"):
            self.__process_admin_switch()

        elif self.path.startswith("admin-mailing"):
            self.__process_admin_mailing()

        elif self.path.startswith("admin"):
            self.__process_admin_misc()

        else:
            self.__process_misc()

        # stop loading animation in telegram interface if this handler did no action
        self._bot.answer_callback(self.call_id, "")
