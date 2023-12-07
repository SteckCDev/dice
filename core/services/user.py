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
