from typing import Type

from sqlalchemy import or_
from sqlalchemy.orm import Query

from core.repositories import PVPRepository
from core.schemas.pvp import (
    PVPDTO,
    CreatePVPDTO,
)
from core.schemas.pvp import UpdatePVPDTO
from core.states import PVPStatus
from infrastructure.cache.redis import RedisKey, RedisInterface, redis_instance
from infrastructure.database import Session
from infrastructure.database.models import PVPModel


class PostgresRedisPVPRepository(PVPRepository):
    def __init__(self) -> None:
        self.__redis: RedisInterface = redis_instance

    def toggle(self) -> bool:
        cached_state: bool | None = self.__redis.get_bool(RedisKey.PVP_ACTIVE)
        state: bool = True if cached_state is None else not cached_state

        self.__redis.set_bool(RedisKey.PVP_ACTIVE, state)

        return state

    def get_status(self) -> bool:
        state: bool | None = self.__redis.get_bool(RedisKey.PVP_ACTIVE)

        if state is None:
            self.__redis.set_bool(RedisKey.PVPC_ACTIVE, True)
            return True

        return state

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

    def get_last_for_tg_id_and_status(self, tg_id: int, status: int) -> PVPDTO | None:
        with Session() as db:
            pvp: Type[PVPModel] = db.query(PVPModel).filter(
                or_(PVPModel.creator_tg_id == tg_id, PVPModel.opponent_tg_id == tg_id),
                PVPModel.status == status
            ).order_by(PVPModel.id.desc()).first()

            return None if pvp is None else PVPDTO(**pvp.__dict__)

    def get_last_for_creator_and_status(self, tg_id: int, status: PVPStatus) -> PVPDTO | None:
        with Session() as db:
            pvp: Type[PVPModel] = db.query(PVPModel).filter(
                PVPModel.creator_tg_id == tg_id,
                PVPModel.status == status
            ).order_by(PVPModel.id.desc()).first()

            return None if pvp is None else PVPDTO(**pvp.__dict__)

    def get_last_5_for_tg_id(self, tg_id: int) -> list[PVPDTO] | None:
        with Session() as db:
            games: Query[Type[PVPModel]] = db.query(PVPModel).filter(
                or_(PVPModel.creator_tg_id == tg_id, PVPModel.opponent_tg_id == tg_id)
            ).order_by(PVPModel.id.desc()).limit(5)

            if games.count() == 0:
                return

            return [
                PVPDTO(**game.__dict__) for game in games
            ]

    def get_count_for_tg_id_and_result(self, tg_id: int, user_won: bool | None) -> int:
        if user_won is None:
            # user_won equals None here. Stand in condition, instead of None itself, only to escape inspection
            # 'is' operator doesn't work here
            condition = or_(PVPModel.winner_tg_id == user_won)
        elif user_won:
            condition = or_(PVPModel.winner_tg_id == tg_id)
        else:
            condition = or_(PVPModel.winner_tg_id != tg_id)

        with Session() as db:
            return db.query(PVPModel).filter(
                or_(PVPModel.creator_tg_id == tg_id, PVPModel.opponent_tg_id == tg_id),
                condition
            ).count()

    def update(self, dto: UpdatePVPDTO) -> None:
        with Session() as db:
            db.query(PVPModel).filter(PVPModel.id == dto.id).update(dto.model_dump())
            db.commit()
