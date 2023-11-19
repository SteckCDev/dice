from core.repositories.user import UserRepository
from core.schemas.user import UserDTO, CreateUserDTO, UpdateUserDTO, UserCache, UserCacheDTO
from infrastructure.cache import RedisInterface, RedisKeys
from infrastructure.database import Session
from infrastructure.database.models import UserModel


class PostgresRedisUserRepository(UserRepository):
    def __init__(self) -> None:
        self.__redis = RedisInterface()

    def __init_cache(self, tg_id: int) -> None:
        initial_cache = UserCache(tg_id=tg_id)

        self.__redis.set_json(
            RedisKeys.USER_CACHE.format(user_tg_id=tg_id),
            initial_cache.model_dump_json(),
            nx=True
        )

    def get_or_create(self, dto: CreateUserDTO) -> UserDTO:
        with Session() as db:
            user: UserModel | None = db.get(UserModel, dto.tg_id)

            if user:
                return UserDTO(**user.__dict__)

            db.add(UserModel(**dto.model_dump()))
            db.commit()

        return UserDTO(
            **db.get(UserModel, dto.tg_id).__dict__
        )

    def get_by_tg_id(self, tg_id: int) -> UserDTO:
        with Session() as db:
            user: UserModel = db.get(UserModel, tg_id)

        return UserDTO(**user.__dict__)

    def update(self, dto: UpdateUserDTO) -> None:
        with Session() as db:
            db.query(UserModel).filter(UserModel.tg_id == dto.tg_id).update(dto.model_dump())
            db.commit()

    def get_cache_by_tg_id(self, tg_id: int) -> UserCacheDTO:
        self.__init_cache(tg_id)

        return UserCacheDTO(
            **self.__redis.get_json(
                RedisKeys.USER_CACHE.format(user_tg_id=tg_id)
            )
        )

    def update_cache(self, dto: UserCacheDTO) -> None:
        self.__redis.set_json(
            RedisKeys.USER_CACHE.format(user_tg_id=dto.tg_id),
            dto.model_dump_json()
        )

    def get_cached_users_count(self) -> int:
        return self.__redis.scan_match(pattern=RedisKeys.USER_CACHE.format(user_tg_id="*"))
