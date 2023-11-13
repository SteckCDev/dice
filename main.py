from threading import Thread
from time import sleep
from typing import NoReturn

from telebot.types import Message, CallbackQuery

from api_services import TeleBotAPI
from handlers import (
    AdminHandler,
    BalanceHandler,
    CallbackHandler,
    LotteryHandler,
    PrivateDiceHandler,
    PrivateTextHandler,
    ProfileHandler,
    PVBHandler,
    PVPCHandler,
    StartHandler,
    SupportHandler,
)
from services import (
    PVBService,
    PVPService,
    PVPCService,
    PVPFService,
    TransactionsService,
)
from settings import settings


bot = TeleBotAPI(settings.bot_token)


def background() -> NoReturn:
    while True:
        sleep(5)


@bot.message_handler(commands=["admin"], chat_types=["private"])
def cmd_admin(_msg: Message):
    AdminHandler().handle()


@bot.message_handler(commands=["start"], chat_types=["private"])
def cmd_start(msg: Message):
    StartHandler(
        msg.chat.id,
        msg.from_user.id,
        msg.from_user.username
    ).handle()


@bot.message_handler(commands=["balance"], chat_types=["private"])
def cmd_balance(msg: Message):
    BalanceHandler(
        msg.chat.id,
        msg.from_user.id
    ).handle()


@bot.message_handler(commands=["profile"], chat_types=["private"])
def cmd_profile(msg: Message):
    ProfileHandler(msg.chat.id).handle()


@bot.message_handler(commands=["pvb"], chat_types=["private"])
def cmd_pvb(msg: Message):
    PVBHandler(
        msg.chat.id,
        msg.message_id,
        msg.from_user.id
    ).handle()


@bot.message_handler(commands=["pvp"], chat_types=["private"])
def cmd_pvp(msg: Message):
    ...


@bot.message_handler(commands=["pvpc"], chat_types=["private"])
def cmd_pvpc(msg: Message):
    PVPCHandler(msg.chat.id).handle()


@bot.message_handler(commands=["lottery"], chat_types=["private"])
def cmd_lottery(msg: Message):
    LotteryHandler(msg.chat.id).handle()


@bot.message_handler(commands=["support"], chat_types=["private"])
def cmd_support(msg: Message):
    SupportHandler(msg.chat.id).handle()


@bot.message_handler(chat_types=["private"])
def private_text(msg: Message):
    PrivateTextHandler(
        msg.from_user.id,
        msg.text
    ).handle()


@bot.message_handler(content_types=["dice"], chat_types=["private"])
def private_dice(msg: Message):
    PrivateDiceHandler(
        msg.from_user.id,
        msg.forward_from,
        msg.dice.value
    ).handle()


@bot.message_handler(chat_types=["group", "supergroup"])
def group_text(msg: Message):
    ...


@bot.message_handler(content_types=["dice"], chat_types=["group", "supergroup"])
def group_dice(msg: Message):
    ...


@bot.callback_handler(func=lambda call: True)
def callback(call: CallbackQuery):
    CallbackHandler(
        call.data,
        call.message.chat.id,
        call.message.message_id,
        call.from_user.id
    ).handle()


if __name__ == "__main__":
    background_thread = Thread(target=background)
    background_thread.start()

    for service in (PVBService, PVPService, PVPCService, PVPFService, TransactionsService):
        service().enable()

    print("Starting polling")

    bot.infinity_polling()
