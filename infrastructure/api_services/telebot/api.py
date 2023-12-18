from typing import Callable, Final, Any

from telebot import TeleBot
from telebot.apihelper import ApiTelegramException
from telebot.types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup

from core.abstract_bot import AbstractBotAPI


PARSE_MODE: Final[str] = "html"


class TeleBotAPI(AbstractBotAPI):
    def __init__(self, api_token: str, max_threads: int = 2, threaded: bool = True) -> None:
        self.__bot: TeleBot = TeleBot(
            token=api_token,
            num_threads=max_threads,
            threaded=threaded,
            parse_mode=PARSE_MODE,
        )

    def set_webhook(self, host: str, port: int | str = 443, path: str = "/") -> None:
        protocol = "https" if port in (443, 8443) else "http"
        base_url = f"{protocol}://{host}:{port}"
        webhook_url = base_url + path

        self.__bot.set_webhook(
            url=webhook_url
        )

    def remove_webhook(self) -> None:
        self.__bot.remove_webhook()

    def process_new_updates(self, updates: list[Any]) -> None:
        self.__bot.process_new_updates(
            updates=updates
        )

    @property
    def message_handler(self) -> Callable:
        return self.__bot.message_handler

    @property
    def callback_handler(self) -> Callable:
        return self.__bot.callback_query_handler

    @property
    def infinity_polling(self) -> Callable:
        return self.__bot.infinity_polling

    def reply(
            self,
            message: Message,
            text: str,
            markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None
    ) -> int:
        sent_message: Message = self.__bot.reply_to(
            message=message,
            text=text,
            reply_markup=markup
        )

        return sent_message.message_id

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
            if exc.result_json.get("description") == "Bad Request: user not found":
                return False

        return True

    def is_user_admin(self, chat_id: int, user_tg_id: int) -> bool:
        return self.__bot.get_chat_member(chat_id, user_tg_id).status in ("administrator", "creator")
