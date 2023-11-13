from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup

from core.base_bot import BaseBotAPI


class TeleBotAPI(BaseBotAPI):
    def __init__(self, bot_token: str):
        self.__bot = TeleBot(
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

    def send_dice(
            self,
            chat_id: int
    ) -> int | None:
        message: Message = self.__bot.send_dice(chat_id)

        return message.dice.value

    def get_chat_member(self, chat_id: int, user_tg_id: int) -> None:
        self.__bot.get_chat_member(chat_id, user_tg_id)
