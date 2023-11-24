from typing import Callable

from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup
from telebot.apihelper import ApiTelegramException

from core.base_bot import BaseBotAPI


class TeleBotAPI(BaseBotAPI):
    def __init__(self, bot_token: str) -> None:
        self.__bot: TeleBot = TeleBot(
            token=bot_token,
            num_threads=2,
            parse_mode="html"
        )

        self.message_handler = self.__bot.message_handler
        self.callback_handler = self.__bot.callback_query_handler
        self.infinity_polling = self.__bot.infinity_polling

    def send_message(
            self,
            chat_id: int,
            text: str,
            markup: ReplyKeyboardMarkup | InlineKeyboardMarkup | None = None
    ) -> int:
        message: Message = self.__bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=markup
        )

        return message.message_id

    def edit_message(
            self,
            chat_id: int,
            message_id: int,
            text: str,
            markup: ReplyKeyboardMarkup | InlineKeyboardMarkup | None = None
    ) -> int | None:
        message: Message | bool = self.__bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=markup
        )

        return message.message_id if isinstance(message, Message) else None

    def get_edit_message_for_context(self, chat_id: int, message_id: int) -> Callable:
        def edit_message_in_context(
                text: str,
                markup: ReplyKeyboardMarkup | InlineKeyboardMarkup | None = None
        ) -> int | None:
            return self.edit_message(chat_id, message_id, text, markup)

        return edit_message_in_context

    def answer_callback(self, call_id: int, text: str) -> None:
        self.__bot.answer_callback_query(call_id, text)

    def send_dice(self, chat_id: int) -> int | None:
        return self.__bot.send_dice(chat_id).dice.value

    def is_user_subscribed(self, chat_id: int, user_tg_id: int) -> bool:
        try:
            self.__bot.get_chat_member(chat_id, user_tg_id)
        except ApiTelegramException as exc:
            if exc.result_json["description"] == "Bad Request: user not found":
                return False

        return True
