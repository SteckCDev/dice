from datetime import datetime, timedelta

from telebot.apihelper import ApiTelegramException

from api_services import TeleBotAPI
from settings import settings
from services.user import UserService
from core.datetime import now


TERMS_AGREEMENT_LASTS_DAYS = 14


class AccessService:
    @staticmethod
    def __user_subscribed(chat_id: int, user_tg_id: int) -> bool:
        try:
            TeleBotAPI(settings.bot_token).get_chat_member(chat_id, user_tg_id)
        except ApiTelegramException as exc:
            if exc.result_json["description"] == "Bad Request: user not found":
                return False

        return True

    @staticmethod
    def __get_required_chats_ids() -> list[int] | None:
        return

    @staticmethod
    def subscriptions(user_tg_id: int) -> bool:
        required_chats = AccessService.__get_required_chats_ids()

        if required_chats is None:
            return True

        for chat_id in required_chats:
            if not AccessService.__user_subscribed(user_tg_id, chat_id):
                return False

        return True

    @staticmethod
    def terms_and_conditions(user_tg_id: int) -> bool:
        terms_accepted_at = UserService.get(user_tg_id).terms_accepted_at

        return terms_accepted_at and terms_accepted_at + timedelta(days=TERMS_AGREEMENT_LASTS_DAYS) > datetime.now()

    @staticmethod
    def agree_with_terms_and_conditions(user_tg_id: int) -> None:
        user = UserService.get(user_tg_id)
        user.terms_accepted_at = now()

        UserService.update(user)

    @staticmethod
    def no_pvb_in_process(user_tg_id: int) -> bool:
        return not UserService.get_cache(user_tg_id).pvb_in_process
