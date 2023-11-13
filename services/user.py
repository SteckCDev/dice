from cache import RedisInterface
from core.datetime import now
from core.redis_keys import RedisKeys
from database import Session
from database.models import UserModel
from schemas import (
    ConfigDTO,
    UserDTO,
    UserProfile,
    UserCache
)
from services.config import ConfigService


class UserService:
    @staticmethod
    def __set_cache_initial(user_tg_id: int) -> None:
        RedisInterface().set_json(
            RedisKeys.USER_CACHE.format(user_tg_id=user_tg_id),
            UserCache().model_dump_json(),
            nx=True
        )

    @staticmethod
    def __count_user(user_tg_id: int) -> None:
        RedisInterface().add_one_to_set(RedisKeys.USERS_SINCE_LAUNCH, user_tg_id)

    @staticmethod
    def __create(user: UserDTO) -> UserDTO:
        with Session() as db:
            db.add(UserModel(**user.model_dump()))
            db.commit()

        return user

    @staticmethod
    def get_cache(user_tg_id: int) -> UserCache:
        cache_json = RedisInterface().get_json(
            RedisKeys.USER_CACHE.format(user_tg_id=user_tg_id)
        )

        return UserCache(**cache_json)

    @staticmethod
    def update_cache(user_tg_id: int, user_cache: UserCache) -> UserCache:
        RedisInterface().set_json(
            RedisKeys.USER_CACHE.format(user_tg_id=user_tg_id),
            user_cache.model_dump_json()
        )

        return user_cache

    @staticmethod
    def users_since_launch() -> int:
        return RedisInterface().get_len_of_set(RedisKeys.USERS_SINCE_LAUNCH)

    @staticmethod
    def get_or_create(user_tg_id: int, user_tg_name: str) -> UserDTO:
        UserService.__set_cache_initial(user_tg_id)
        UserService.__count_user(user_tg_id)

        with Session() as db:
            user: UserModel | None = db.get(UserModel, user_tg_id)

        if user:
            return UserDTO(**user.__dict__)

        config: ConfigDTO = ConfigService.get()

        new_user = UserDTO(
            tg_id=user_tg_id,
            tg_name=user_tg_name,
            balance=config.start_balance,
            beta_balance=config.start_beta_balance,
            beta_balance_updated_at=now(),
            joined_at=now()
        )

        return UserService.__create(new_user)

    @staticmethod
    def get(user_tg_id: int) -> UserDTO:
        UserService.__set_cache_initial(user_tg_id)
        UserService.__count_user(user_tg_id)

        with Session() as db:
            user: UserModel = db.get(UserModel, user_tg_id)

        return UserDTO(**user.__dict__)

    @staticmethod
    def get_profile(user_tg_id: int) -> UserProfile:
        UserService.__set_cache_initial(user_tg_id)
        UserService.__count_user(user_tg_id)

        with Session() as db:
            user: UserModel = db.get(UserModel, user_tg_id)

        return UserProfile(**user.__dict__, games_count=0)

    @staticmethod
    def update(user: UserDTO) -> UserDTO:
        UserService.__set_cache_initial(user.tg_id)
        UserService.__count_user(user.tg_id)

        with Session() as db:
            db.query(UserModel).filter(
                UserModel.tg_id == user.tg_id
            ).update(user.model_dump())
            db.commit()

        return user
