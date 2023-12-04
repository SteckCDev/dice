from typing import Type

from sqlalchemy import or_
from sqlalchemy.orm import Query

from core.repositories import PVPCRepository
from core.schemas.pvpc import (
    PVPCDTO,
    CreatePVPCDTO,
    UpdatePVPCDTO,
)
from infrastructure.database import Session
from infrastructure.database.models import PVPCModel
from infrastructure.cache.redis import RedisKey, redis_instance
from states import PVPCStatus


class PostgresRedisPVPCRepository(PVPCRepository):
    def __init__(self) -> None:
        self.__redis = redis_instance

    def toggle(self) -> bool:
        cached_state: bool | None = self.__redis.get_bool(RedisKey.PVPC_ACTIVE)
        state: bool = True if cached_state is None else not cached_state

        self.__redis.set_bool(RedisKey.PVPC_ACTIVE, state)

        return state

    def get_status(self) -> bool:
        state: bool | None = self.__redis.get_bool(RedisKey.PVPC_ACTIVE)

        if state:
            return state

        return self.toggle()

    def create(self, dto: CreatePVPCDTO) -> PVPCDTO:
        with Session() as db:
            db.add(PVPCModel(**dto.model_dump()))
            db.commit()

            pvpc: Type[PVPCModel] = db.query(PVPCModel).order_by(PVPCModel.id.desc()).first()

        return PVPCDTO(**pvpc.__dict__)

    def get_by_id(self, _id: int) -> PVPCDTO | None:
        with Session() as db:
            pvpc: Type[PVPCModel] | None = db.get(PVPCModel, _id)

        return PVPCDTO(**pvpc.__dict__) if pvpc else None

    def get_all_for_status(self, status: PVPCStatus) -> list[PVPCDTO] | None:
        with Session() as db:
            games: Query[Type[PVPCModel]] = db.query(PVPCModel).filter(
                PVPCModel.status == status
            ).order_by(PVPCModel.id.desc())

            if games.count() == 0:
                return

            return [
                PVPCDTO(**game.__dict__) for game in games
            ]

    def update(self, dto: UpdatePVPCDTO) -> None:
        with Session() as db:
            db.query(PVPCModel).filter(PVPCModel.id == dto.id).update(dto.model_dump())
            db.commit()

    def get_for_tg_id_and_status(self, user_tg_id: int, status: PVPCStatus) -> PVPCDTO | None:
        with Session() as db:
            pvpc: Type[PVPCModel] | None = db.query(PVPCModel).filter(
                or_(PVPCModel.creator_tg_id == user_tg_id, PVPCModel.opponent_tg_id == user_tg_id),
                PVPCModel.status == status
            ).first()

            if pvpc is None:
                return

            return PVPCDTO(**pvpc.__dict__)
