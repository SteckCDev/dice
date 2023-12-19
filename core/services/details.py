from core.schemas.details import (
    DetailsDTO,
    CreateDetailsDTO,
    UpdateDetailsDTO,
)
from core.repositories import DetailsRepository


class DetailsService:
    def __init__(self, repository: DetailsRepository):
        self.__repo: DetailsRepository = repository

    def create(self, dto: CreateDetailsDTO) -> DetailsDTO:
        return self.__repo.create(dto)

    def get_by_id(self, _id) -> DetailsDTO | None:
        return self.__repo.get_by_id(_id)

    def get_all_for_tg_id_and_method(self, user_tg_id: int, method: str) -> list[DetailsDTO] | None:
        return self.__repo.get_all_for_tg_id_and_method(user_tg_id, method)

    def update(self, dto: UpdateDetailsDTO) -> None:
        self.__repo.update(dto)
