from typing import Type

from sqlalchemy.orm import Query

from core.schemas.details import (
    DetailsDTO,
    CreateDetailsDTO,
    UpdateDetailsDTO,
)
from core.repositories import DetailsRepository
from infrastructure.database import Session
from infrastructure.database.models import DetailsModel


class PostgresDetailsRepository(DetailsRepository):
    def create(self, dto: CreateDetailsDTO) -> DetailsDTO:
        with Session() as db:
            db.add(
                DetailsModel(
                    **dto.model_dump()
                )
            )
            db.commit()

            details: Type[DetailsModel] = db.query(DetailsModel).order_by(DetailsModel.id.desc()).first()

        return DetailsDTO(**details.__dict__)

    def get_by_id(self, _id: int) -> DetailsDTO | None:
        with Session() as db:
            details: Type[DetailsModel] | None = db.get(DetailsModel, _id)

        return DetailsDTO(**details.__dict__) if details else None

    def get_all_for_tg_id_and_method(self, user_tg_id: int, method: str) -> list[DetailsDTO] | None:
        with Session() as db:
            details: Query[Type[DetailsModel]] = db.query(DetailsModel).filter(
                DetailsModel.user_tg_id == user_tg_id,
                DetailsModel.method == method
            ).order_by(DetailsModel.id.desc())

            if details.count() == 0:
                return

            return [
                DetailsDTO(**single_details.__dict__) for single_details in details
            ]

    def update(self, dto: UpdateDetailsDTO) -> None:
        with Session() as db:
            db.query(DetailsModel).filter(DetailsModel.id == dto.id).update(dto.model_dump())
            db.commit()
