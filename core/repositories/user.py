from abc import ABC, abstractmethod

from core.schemas.user import (
    UserDTO,
    CreateUserDTO,
    UpdateUserDTO,
    UserCacheDTO
)


class UserRepository(ABC):
    @abstractmethod
    def get_or_create(self, dto: CreateUserDTO) -> UserDTO:
        ...

    @abstractmethod
    def get_all(self) -> list[UserDTO] | None:
        ...

    @abstractmethod
    def get_by_tg_id(self, tg_id: int) -> UserDTO | None:
        ...

    def get_max_fake_tg_id(self) -> int:
        ...

    @abstractmethod
    def get_fakes(self) -> list[UserDTO] | None:
        ...

    @abstractmethod
    def get_count(self) -> int:
        ...

    @abstractmethod
    def update(self, dto: UpdateUserDTO) -> None:
        ...

    @abstractmethod
    def get_cache_by_tg_id(self, tg_id: int) -> UserCacheDTO:
        ...

    @abstractmethod
    def update_cache(self, dto: UserCacheDTO) -> None:
        ...

    @abstractmethod
    def get_cached_users_count(self) -> int:
        ...
