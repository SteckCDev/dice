from typing import Type

from sqlalchemy.orm import Query

from core.repositories import PVPRepository
from core.schemas.pvp import (
    PVPDTO,
    CreatePVPDTO,
)
from core.schemas.pvp import UpdatePVPDTO
from core.states import PVPStatus
from infrastructure.cache.redis import RedisKey, redis_instance
from infrastructure.database import Session
from infrastructure.database.models import PVPModel


class PostgresRedisPVPRepository(PVPRepository):
    def __init__(self) -> None:
        self.__redis = redis_instance

    def toggle(self) -> bool:
        cached_state: bool | None = self.__redis.get_bool(RedisKey.PVP_ACTIVE)
        state: bool = True if cached_state is None else not cached_state

        self.__redis.set_bool(RedisKey.PVP_ACTIVE, state)

        return state

    def get_status(self) -> bool:
        state: bool | None = self.__redis.get_bool(RedisKey.PVP_ACTIVE)

        if state:
            return state

        return self.toggle()

    def create(self, dto: CreatePVPDTO) -> PVPDTO:
        with Session() as db:
            db.add(PVPModel(**dto.model_dump()))
            db.commit()

            pvp: Type[PVPModel] = db.query(PVPModel).order_by(PVPModel.id.desc()).first()

        return PVPDTO(**pvp.__dict__)

    def get_by_id(self, _id: int) -> PVPDTO | None:
        with Session() as db:
            pvp: Type[PVPModel] | None = db.get(PVPModel, _id)

        return PVPDTO(**pvp.__dict__) if pvp else None

    def update(self, dto: UpdatePVPDTO) -> None:
        with Session() as db:
            db.query(PVPModel).filter(PVPModel.id == dto.id).update(dto.model_dump())
            db.commit()

    def get_all_for_status(self, status: PVPStatus) -> list[PVPDTO] | None:
        with Session() as db:
            games: Query[Type[PVPModel]] = db.query(PVPModel).filter(
                PVPModel.status == status
            ).order_by(PVPModel.id.desc())

            if games.count() == 0:
                return

            return [
                PVPDTO(**game.__dict__) for game in games
            ]

    def get_last_for_creator_and_status(self, tg_id: int, status: PVPStatus) -> PVPDTO | None:
        with Session() as db:
            pvp: Type[PVPModel] = db.query(PVPModel).filter(
                PVPModel.creator_tg_id == tg_id,
                PVPModel.status == status
            ).order_by(PVPModel.id.desc()).first()

            return None if pvp is None else PVPDTO(**pvp.__dict__)
