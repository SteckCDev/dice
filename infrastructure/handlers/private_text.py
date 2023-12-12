import re
import html

from telebot.types import CallbackQuery

from core.schemas.config import (
    ConfigDTO,
)
from core.schemas.user import (
    UserDTO,
    UserCacheDTO,
)
from core.services import (
    AdminService,
    ConfigService,
    UserService,
)
from core.states import NumbersRelation
from infrastructure.api_services.telebot import BaseTeleBotHandler
from infrastructure.repositories import (
    ImplementedAdminRepository,
    ImplementedConfigRepository,
    ImplementedUserRepository,
)
from infrastructure.handlers.callback import CallbackHandler
from settings import settings
from templates import (
    Markups,
    Menu,
    Messages,
)
from templates import RegEx
from .admin import AdminHandler
from .lottery import LotteryHandler
from .profile import ProfileHandler
from .support import SupportHandler


class PrivateTextHandler(BaseTeleBotHandler):
    def __init__(self, text: str, user_id: int, user_name: str) -> None:
        super().__init__()

        self.text: str = text
        self.user_id: int = user_id
        self.user_name: str = html.escape(user_name)

        self.is_admin = user_id == settings.admin_tg_id
        self.is_text_card = re.fullmatch(RegEx.CARD, self.text)
        self.is_text_phone = re.fullmatch(RegEx.PHONE, self.text)
        self.is_text_btc_wallet = re.fullmatch(RegEx.BTC_WALLET, self.text)

        config_service: ConfigService = ConfigService(
            repository=ImplementedConfigRepository()
        )
        self.__user_service: UserService = UserService(
            repository=ImplementedUserRepository(),
            bot=self._bot,
            config_service=config_service
        )
        self.__admin_service: AdminService = AdminService(
            repository=ImplementedAdminRepository(),
            bot=self._bot,
            user_service=self.__user_service,
            config_service=config_service
        )

        self.config: ConfigDTO = config_service.get()
        self.user: UserDTO = self.__user_service.get_by_tg_id(user_id)
        self.user_cache: UserCacheDTO = self.__user_service.get_cache_by_tg_id(user_id)

    def __callback_path_startswith(self, pattern: str) -> bool:
        call: CallbackQuery = CallbackQuery.de_json(self.user_cache.callback_json)

        return call.data.startswith(pattern)

    def __update_message(self) -> None:
        call: CallbackQuery = CallbackQuery.de_json(self.user_cache.callback_json)

        CallbackHandler(
            call_id=call.id,
            path=call.data,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            user_id=call.from_user.id,
            user_name=call.from_user.username or call.from_user.first_name,
            call=call
        ).handle()

    def __process_admin(self) -> bool:
        if self.text[0] == ">" and len(self.text) > 1:
            self.__admin_service.set_mailing_text(self.text[1:])
            return True

        adjusted_or_error: bool | str = self.__admin_service.try_to_adjust_config_field(
            self.text.split()
        )

        if adjusted_or_error:
            self._bot.send_message(
                self.user_id,
                Messages.admin_config_adjusted() if isinstance(adjusted_or_error, bool) else adjusted_or_error
            )
            return True

        return False

    def __set_withdraw_details(self) -> None:
        if not self.__callback_path_startswith("transaction-withdraw-details"):
            return

        self.user_cache.withdraw_details = self.text
        self.__user_service.update_cache(self.user_cache)

        self.__update_message()

    def __set_withdraw_bank(self) -> None:
        if len(self.text) > 32 or len(self.text) < 2:
            return

        if not self.__callback_path_startswith("transaction-withdraw-details"):
            return

        self.user_cache.withdraw_bank = self.text
        self.__user_service.update_cache(self.user_cache)

        self.__update_message()

    def __set_amount(self) -> None:
        amount: int = int(self.text)

        if self.user_cache.numbers_relation == NumbersRelation.DEPOSIT_AMOUNT and self.__callback_path_startswith(
            "transaction-deposit-amount"
        ):
            if amount < self.config.min_deposit:
                self._bot.send_message(
                    self.user_id,
                    Messages.transaction_deposit_min_limit(self.config.min_deposit)
                )
                return

            self.user_cache.deposit_amount = amount

        elif self.user_cache.numbers_relation == NumbersRelation.WITHDRAW_AMOUNT and self.__callback_path_startswith(
            "transaction-withdraw-amount"
        ):
            if amount < self.config.min_withdraw:
                self._bot.send_message(
                    self.user_id,
                    Messages.transaction_withdraw_min_limit(self.config.min_withdraw)
                )
                return

            if amount > self.user.balance:
                self._bot.send_message(
                    self.user_id,
                    Messages.balance_is_not_enough()
                )
                return

            self.user_cache.withdraw_amount = amount

        elif self.__callback_path_startswith("pvb-create") or self.__callback_path_startswith("pvp-create"):
            if amount < self.config.min_bet or amount > self.config.max_bet:
                self._bot.send_message(
                    self.user_id,
                    Messages.bet_out_of_limits(
                        self.config.min_bet,
                        self.config.max_bet
                    )
                )
                return

            if amount > self.__user_service.get_user_selected_balance(self.user_id):
                self._bot.send_message(
                    self.user_id,
                    Messages.balance_is_not_enough()
                )
                return

            if self.user_cache.numbers_relation == NumbersRelation.PVB_BET:
                self.user_cache.pvb_bet = amount
            else:
                self.user_cache.pvp_bet = amount

        else:
            return

        self.__user_service.update_cache(self.user_cache)
        self.__update_message()

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

        return True

    def _process(self) -> None:
        if self.text == Menu.GAMES:
            self._bot.send_message(
                self.user_id,
                Messages.games(
                    self.__user_service.get_user_selected_balance(self.user_id),
                    self.user_cache.beta_mode
                ),
                Markups.games()
            )

        elif self.text == Menu.PROFILE:
            ProfileHandler(self.user_id, self.user_name).handle()

        elif self.text == Menu.LOTTERY:
            LotteryHandler(self.user_id).handle()

        elif self.text == Menu.SUPPORT:
            SupportHandler(self.user_id).handle()

        elif self.text == Menu.ADMIN:
            AdminHandler(self.user_id).handle()

        elif self.is_admin and self.__process_admin():
            pass

        elif self.is_text_card or self.is_text_phone or self.is_text_btc_wallet:
            self.__set_withdraw_details()

        elif self.text.isdigit():
            self.__set_amount()

        else:
            self.__set_withdraw_bank()
