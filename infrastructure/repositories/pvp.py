from sqlalchemy.orm import Query

from core.repositories.pvp import PVPRepository
from core.schemas.pvp import (
    PVPDTO,
    CreatePVPDTO,
)
from infrastructure.cache import RedisInterface, RedisKeys
from infrastructure.database import Session
from infrastructure.database.models import PVPModel
from schemas.pvp import UpdatePVPDTO


class PostgresRedisPVPRepository(PVPRepository):
    def __init__(self) -> None:
        self.__redis = RedisInterface()

    def toggle(self) -> bool:
        cached_state: bool | None = self.__redis.get_bool(RedisKeys.PVP_ACTIVE)
        state: bool = True if cached_state is None else not cached_state

        self.__redis.set_bool(RedisKeys.PVP_ACTIVE, state)

        return state

    def get_status(self) -> bool:
        state: bool | None = self.__redis.get_bool(RedisKeys.PVP_ACTIVE)

        if state:
            return state

        return self.toggle()

    def create(self, dto: CreatePVPDTO) -> PVPDTO:
        with Session() as db:
            db.add(PVPModel(**dto.model_dump()))
            db.commit()

            pvp: PVPModel = db.query(PVPModel).order_by(PVPModel.id.desc()).first()

        return PVPDTO(**pvp.__dict__)

    def get_by_id(self, _id: int) -> PVPDTO:
        with Session() as db:
            pvp: PVPModel = db.get(PVPModel, _id)

        return PVPDTO(**pvp.__dict__)

    def update(self, dto: UpdatePVPDTO) -> None:
        with Session() as db:
            db.query(PVPModel).filter(PVPModel.id == dto.id).update(dto.model_dump())
            db.commit()

    def get_all_for_status(self, status: int) -> list[PVPDTO] | None:
        with Session() as db:
            games: Query[PVPModel] = db.query(PVPModel).filter(
                PVPModel.status == status
            ).order_by(PVPModel.id.desc())

            if games.count() == 0:
                return

            return [
                PVPDTO(**game.__dict__) for game in games
            ]
