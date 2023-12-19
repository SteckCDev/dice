from abc import ABC, abstractmethod

from core.schemas.details import (
    DetailsDTO,
    CreateDetailsDTO,
    UpdateDetailsDTO,
)


class DetailsRepository(ABC):
    @abstractmethod
    def create(self, dto: CreateDetailsDTO) -> DetailsDTO:
        ...

    @abstractmethod
    def get_by_id(self, _id: int) -> DetailsDTO | None:
        ...

    @abstractmethod
    def get_all_for_tg_id_and_method(self, user_tg_id: int, method: str) -> list[DetailsDTO] | None:
        ...

    @abstractmethod
    def update(self, dto: UpdateDetailsDTO) -> None:
        ...
