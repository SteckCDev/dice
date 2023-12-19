from datetime import datetime, timedelta
from typing import Final

from core.abstract_bot import AbstractBotAPI
from core.repositories import UserRepository
from core.schemas.user import (
    UserDTO,
    CreateUserDTO,
    UpdateUserDTO,
    UserCacheDTO,
)
from core.services.config import ConfigService


TERMS_AGREEMENT_LASTS_DAYS: Final[int] = 14
MAX_BETA_BALANCE: Final[int] = 20_000
BETA_BALANCE_STEP: Final[int] = 1_750


class UserService:
    def __init__(self, repository: UserRepository, bot: AbstractBotAPI, config_service: ConfigService) -> None:
        self.__repo: UserRepository = repository
        self.__bot: AbstractBotAPI = bot
        self.__config_service: ConfigService = config_service

    def get_or_create(self, dto: CreateUserDTO) -> UserDTO:
        return self.__repo.get_or_create(dto)

    def get_all(self) -> list[UserDTO] | None:
        return self.__repo.get_all()

    def get_by_tg_id(self, tg_id: int) -> UserDTO | None:
        return self.__repo.get_by_tg_id(tg_id)

    def get_max_fake_tg_id(self) -> int:
        return self.__repo.get_max_fake_tg_id()

    def get_fakes(self) -> list[UserDTO] | None:
        return self.__repo.get_fakes()

    def get_count(self) -> int:
        return self.__repo.get_count()

    def update(self, dto: UpdateUserDTO) -> None:
        self.__repo.update(dto)

    def update_cache(self, dto: UserCacheDTO) -> None:
        self.__repo.update_cache(dto)

    def get_cache_by_tg_id(self, tg_id: int) -> UserCacheDTO:
        return self.__repo.get_cache_by_tg_id(tg_id)

    def get_cached_users_count(self) -> int:
        return self.__repo.get_cached_users_count()

    def get_user_selected_balance(self, tg_id: int) -> int:
        user: UserDTO = self.__repo.get_by_tg_id(tg_id)
        user_cache: UserCacheDTO = self.__repo.get_cache_by_tg_id(tg_id)

        return user.beta_balance if user_cache.beta_mode else user.balance

    def is_terms_and_conditions_agreed(self, tg_id: int) -> bool:
        terms_accepted_at: datetime = self.__repo.get_by_tg_id(tg_id).terms_accepted_at

        return terms_accepted_at and terms_accepted_at + timedelta(days=TERMS_AGREEMENT_LASTS_DAYS) > datetime.now()

    def agree_with_terms_and_conditions(self, tg_id: int) -> None:
        user: UserDTO = self.__repo.get_by_tg_id(tg_id)
        user.terms_accepted_at = datetime.now()

        self.__repo.update(
            UpdateUserDTO(
                **user.model_dump()
            )
        )

    def is_subscribed_to_chats(self, tg_id: int) -> bool:
        required_chats: list[int] | None = self.__config_service.get().required_chats

        if required_chats is None:
            return True

        for chat_id in required_chats:
            if not self.__bot.is_user_subscribed(chat_id, tg_id):
                return False

        return True

    def get_required_chats_title_and_invite_link(self) -> list[tuple[str, str]] | None:
        required_chats: list[int] | None = self.__config_service.get().required_chats

        if required_chats is None:
            return

        chats_info: list[tuple[str, str]] = list()

        for chat_id in required_chats:
            chat_info: tuple[str, str] | None = self.__bot.get_chat_title_and_invite_link(chat_id)

            if chat_info is None:
                continue

            chats_info.append(chat_info)

        return chats_info if chats_info else None

    def auto_update_beta_balance(self) -> None:
        """
        if self._beta_updated == 0:
            self._beta_updated = int(time())
        else:
            hours_passed = (int(time()) - self._beta_updated) // 3600

            while self._beta_balance <= 18250 and hours_passed > 0:
                self._beta_balance += 1750
                hours_passed -= 1

        base.query("UPDATE users SET beta_updated_on = ? WHERE tg_id = ?", (int(time()), self._id))
        """

        users: list[UserDTO] | None = self.__repo.get_all()

        if users is None:
            return

        for user in users:
            time_passed: timedelta = datetime.now() - user.beta_balance_updated_at
            hours_passed: int = time_passed.seconds // 3600

            if hours_passed == 0 or user.beta_balance > MAX_BETA_BALANCE - BETA_BALANCE_STEP:
                continue

            user.beta_balance += min(
                (MAX_BETA_BALANCE - user.beta_balance) // BETA_BALANCE_STEP, hours_passed
            ) * BETA_BALANCE_STEP
            user.beta_balance_updated_at = datetime.now()

            self.__repo.update(
                UpdateUserDTO(
                    **user.model_dump()
                )
            )
