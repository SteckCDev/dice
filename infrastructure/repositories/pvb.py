from core.repositories.pvb import PVBRepository
from core.schemas.pvb import PVBDTO, CreatePVBDTO
from infrastructure.cache import RedisInterface, RedisKeys
from infrastructure.database import Session
from infrastructure.database.models import PVBModel


class PostgresRedisPVBRepository(PVBRepository):
    def __init__(self) -> None:
        self.__redis = RedisInterface()

    def toggle(self) -> bool:
        state: bool | None = self.__redis.get_bool(RedisKeys.PVB_ACTIVE)

        state = True if state is None else not state

        self.__redis.set_bool(RedisKeys.PVB_ACTIVE, state)

        return state

    def get_status(self) -> bool:
        state: bool | None = self.__redis.get_bool(RedisKeys.PVB_ACTIVE)

        if state:
            return state

        return self.toggle()

    def create(self, dto: CreatePVBDTO) -> PVBDTO:
        with Session() as db:
            db.add(PVBModel(**dto.model_dump()))
            db.commit()

            pvb: PVBModel = db.query(PVBModel).order_by(PVBModel.id.desc()).first()

        return PVBDTO(**pvb.__dict__)

    def get_by_id(self, _id: int) -> PVBDTO:
        with Session() as db:
            pvb: PVBModel = db.get(PVBModel, _id)

        return PVBDTO(**pvb.__dict__)

    def get_count_for_tg_id(self, tg_id: int) -> int:
        with Session() as db:
            return db.query(PVBModel).filter(PVBModel.player_tg_id == tg_id).count()
