import json
import time
from typing import Final, NoReturn

import uvicorn
from fastapi import FastAPI
from telebot.apihelper import ApiTelegramException
from telebot.types import Message, CallbackQuery, Update

from infrastructure.api_services.telebot import TeleBotAPI
from infrastructure.handlers import (
    AdminHandler,
    BalanceHandler,
    CallbackHandler,
    LotteryHandler,
    PrivateDiceHandler,
    PrivateTextHandler,
    ProfileHandler,
    PVBHandler,
    PVPHandler,
    PVPCHandler,
    StartHandler,
    SupportHandler,
)
from settings import settings


WEBHOOK_PATH: Final[str] = f"/{settings.bot_token}/"
LAST_UPDATE: dict = {}

fastapi_app: FastAPI = FastAPI(
    docs_url=None,
    redoc_url=None
)

bot: TeleBotAPI = TeleBotAPI(
    bot_token=settings.bot_token,
    max_threads=settings.max_threads
)


@fastapi_app.get("/test")
def test_endpoint() -> dict:
    return {
        "result": "success",
        "last_update": LAST_UPDATE
    }


@fastapi_app.post("/{BOT_TOKEN}/")
def process_webhook(update: dict) -> None:
    global LAST_UPDATE

    if update:
        #
        #
        #
        LAST_UPDATE = update
        bot.send_message(
            settings.admin_tg_id,
            f"📌 Update\n\n{update}"
        )
        print(update, "\n\n\n")
        print(json.dumps(update))
        #
        #
        #

        update: Update = Update.de_json(update)
        bot.process_new_updates([update])
    else:
        return


@bot.message_handler(commands=["admin"], chat_types=["private"])
def cmd_admin(_msg: Message) -> None:
    AdminHandler().handle()


@bot.message_handler(commands=["start"], chat_types=["private"])
def cmd_start(msg: Message) -> None:
    StartHandler(
        msg.chat.id,
        msg.from_user.id,
        msg.from_user.username or msg.from_user.first_name
    ).handle()


@bot.message_handler(commands=["balance"], chat_types=["private"])
def cmd_balance(msg: Message) -> None:
    BalanceHandler(
        msg.chat.id,
        msg.from_user.id,
        msg.from_user.username or msg.from_user.first_name
    ).handle()


@bot.message_handler(commands=["profile"], chat_types=["private"])
def cmd_profile(msg: Message) -> None:
    ProfileHandler(
        msg.from_user.id,
        msg.from_user.username or msg.from_user.first_name
    ).handle()


@bot.message_handler(commands=["pvb"], chat_types=["private"])
def cmd_pvb(msg: Message) -> None:
    PVBHandler(
        msg.chat.id,
        msg.message_id,
        msg.from_user.id
    ).handle()


@bot.message_handler(commands=["pvp"], chat_types=["private"])
def cmd_pvp(msg: Message) -> None:
    PVPHandler(
        msg.from_user.id,
        msg.message_id
    ).handle()


@bot.message_handler(commands=["pvpc"], chat_types=["private"])
def cmd_pvpc(msg: Message) -> None:
    PVPCHandler(msg.chat.id).handle()


@bot.message_handler(commands=["lottery"], chat_types=["private"])
def cmd_lottery(msg: Message) -> None:
    LotteryHandler(msg.chat.id).handle()


@bot.message_handler(commands=["support"], chat_types=["private"])
def cmd_support(msg: Message) -> None:
    SupportHandler(msg.chat.id).handle()


@bot.message_handler(chat_types=["private"])
def private_text(msg: Message) -> None:
    PrivateTextHandler(
        msg.text,
        msg.from_user.id,
        msg.from_user.username or msg.from_user.first_name
    ).handle()


@bot.message_handler(content_types=["dice"], chat_types=["private"])
def private_dice(msg: Message) -> None:
    PrivateDiceHandler(
        msg.from_user.id,
        msg.from_user.username or msg.from_user.first_name,
        msg.forward_from,
        msg.dice.value
    ).handle()


@bot.message_handler(chat_types=["group", "supergroup"])
def group_text(_msg: Message) -> None:
    ...


@bot.message_handler(content_types=["dice"], chat_types=["group", "supergroup"])
def group_dice(_msg: Message) -> None:
    ...


@bot.callback_handler(func=lambda call: True)
def callback(call: CallbackQuery) -> None:
    CallbackHandler(
        call.id,
        call.data,
        call.message.chat.id,
        call.message.message_id,
        call.from_user.id,
        call.from_user.username or call.from_user.first_name
    ).handle()


def main() -> NoReturn:
    def webhook() -> NoReturn:
        removal_retries: int = 10
        setting_retries: int = 10

        while removal_retries > 0:
            try:
                bot.remove_webhook()
                break
            except ApiTelegramException as exc:
                print(f"{removal_retries}. {exc}")
                removal_retries -= 1
                time.sleep(1)

        while setting_retries > 0:
            try:
                bot.set_webhook(
                    host=settings.webhook_host,
                    port=settings.webhook_port,
                    path=WEBHOOK_PATH
                )
                break
            except ApiTelegramException as exc:
                print(f"{setting_retries}. {exc}")
                setting_retries -= 1
                time.sleep(1)

        uvicorn.run(
            app=fastapi_app,
            host=settings.webhook_listen,
            port=settings.webhook_port
        )

    def polling() -> NoReturn:
        print("Starting polling")

        bot.infinity_polling()

    if settings.local_environment:
        polling()
    else:
        webhook()


if __name__ == "__main__":
    main()
