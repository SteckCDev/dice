import time
from typing import Callable, Final, NoReturn

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
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


WEBHOOK_PATH: Final[str] = f"/{settings.api_token}/"

fastapi_app: FastAPI = FastAPI(
    docs_url=None,
    redoc_url=None
)

#
# while using webhooks, 'threaded' set to False makes sense on some free ...aaS
# else case processing down unable
# https://www.pythonanywhere.com/forums/topic/9562/
#
bot: TeleBotAPI = TeleBotAPI(
    api_token=settings.api_token,
    max_threads=settings.max_threads,
    threaded=settings.threaded
)


@fastapi_app.post("/{API_TOKEN}/")
def process_webhook(raw_update: dict) -> JSONResponse:
    if raw_update:
        update: Update = Update.de_json(raw_update)
        bot.process_new_updates([update])

    return JSONResponse(
        content={"status": "OK"},
        status_code=200
    )


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
    def request_with_retrial(to_request: Callable, *args, **kwargs) -> bool:
        retries_left: int = 5

        while retries_left > 0:
            try:
                to_request(*args, **kwargs)
                return True
            except ApiTelegramException as exc:
                print(f"Attempt {retries_left} ({to_request}): {exc}")
                retries_left -= 1
                time.sleep(1)

        return False

    def webhook() -> NoReturn:
        webhook_removed: bool = request_with_retrial(
            bot.remove_webhook
        )
        webhook_set: bool = request_with_retrial(
            bot.set_webhook,
            host=settings.webhook_host,
            port=settings.webhook_port,
            path=WEBHOOK_PATH
        )

        if not webhook_removed or not webhook_set:
            exit(-1)

        uvicorn.run(
            app=fastapi_app,
            host=settings.webhook_listen,
            port=settings.webhook_port
        )

    def polling() -> NoReturn:
        try:
            bot.infinity_polling()
        except ApiTelegramException as exc:
            print(f"Polling start failed ({bot.infinity_polling}): {exc}")
            exit(-1)

    if settings.local_environment:
        polling()
    else:
        webhook()


if __name__ == "__main__":
    main()
