from typing import Type

from sqlalchemy.orm import Query

from core.repositories import PVBRepository
from core.schemas.pvb import (
    PVBDTO,
    CreatePVBDTO,
)
from infrastructure.cache.redis import RedisKey, redis_instance
from infrastructure.database import Session
from infrastructure.database.models import PVBModel


class PostgresRedisPVBRepository(PVBRepository):
    def __init__(self) -> None:
        self.__redis = redis_instance

    def toggle(self) -> bool:
        cached_state: bool | None = self.__redis.get_bool(RedisKey.PVB_ACTIVE)
        state: bool = True if cached_state is None else not cached_state

        self.__redis.set_bool(RedisKey.PVB_ACTIVE, state)

        return state

    def get_status(self) -> bool:
        state: bool | None = self.__redis.get_bool(RedisKey.PVB_ACTIVE)

        if state:
            return state

        return self.toggle()

    def create(self, dto: CreatePVBDTO) -> PVBDTO:
        with Session() as db:
            db.add(PVBModel(**dto.model_dump()))
            db.commit()

            pvb: Type[PVBModel] = db.query(PVBModel).order_by(PVBModel.id.desc()).first()

        return PVBDTO(**pvb.__dict__)

    def get_by_id(self, _id: int) -> PVBDTO | None:
        with Session() as db:
            pvb: Type[PVBModel] | None = db.get(PVBModel, _id)

        return PVBDTO(**pvb.__dict__) if pvb else None

    def get_count_for_tg_id(self, tg_id: int) -> int:
        with Session() as db:
            return db.query(PVBModel).filter(PVBModel.player_tg_id == tg_id).count()

    def get_count_for_tg_id_and_result(self, tg_id: int, player_won: bool | None) -> int:
        with Session() as db:
            return db.query(PVBModel).filter(
                PVBModel.player_tg_id == tg_id,
                PVBModel.player_won == player_won
            ).count()

    def get_last_5_for_tg_id(self, tg_id: int) -> list[PVBDTO] | None:
        with Session() as db:
            games: Query[Type[PVBModel]] = db.query(PVBModel).filter(
                PVBModel.player_tg_id == tg_id
            ).order_by(PVBModel.id.desc()).limit(5)

            if games.count() == 0:
                return

            return [
                PVBDTO(**game.__dict__) for game in games
            ]
