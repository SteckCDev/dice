from celery import Celery

from core.services import (
    ConfigService,
    PVPService,
    UserService,
)
from core.services.pvp import TTL_OF_CREATED
from infrastructure.api_services.telebot import TeleBotAPI
from infrastructure.repositories import (
    PostgresRedisPVPRepository,
    PostgresRedisUserRepository,
    MockConfigRepository,
)
from settings import settings
from .instance import celery_instance


bot: TeleBotAPI = TeleBotAPI(
    api_token=settings.api_token,
    max_threads=settings.max_threads
)
config_service: ConfigService = ConfigService(
    repository=MockConfigRepository()
)
user_service: UserService = UserService(
    repository=PostgresRedisUserRepository(),
    bot=bot,
    config_service=config_service
)
pvp_service: PVPService = PVPService(
    repository=PostgresRedisPVPRepository(),
    bot=bot,
    config_service=config_service,
    user_service=user_service
)


@celery_instance.on_after_finalize.connect
def setup_beat(sender: Celery, **_kwargs) -> None:
    sender.add_periodic_task(
        schedule=5,
        sig=pvp_finish_started.s()
    )
    sender.add_periodic_task(
        schedule=TTL_OF_CREATED.seconds,
        sig=pvp_close_expired.s()
    )


@celery_instance.task
def pvp_finish_started() -> None:
    pvp_service.auto_finish_started_games()


@celery_instance.task
def pvp_close_expired() -> None:
    pvp_service.auto_close_expired_games()
