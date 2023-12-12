from celery import Celery
from telebot.apihelper import ApiTelegramException

from core.services import (
    AdminService,
    ConfigService,
    PVPService,
    PVPCService,
    UserService,
)
from infrastructure.api_services.telebot import TeleBotAPI
from infrastructure.repositories import (
    ImplementedAdminRepository,
    ImplementedPVPRepository,
    ImplementedPVPCRepository,
    ImplementedUserRepository,
    ImplementedConfigRepository,
)
from settings import settings
from .instance import celery_instance


bot: TeleBotAPI = TeleBotAPI(
    api_token=settings.api_token,
    max_threads=settings.max_threads,
    threaded=settings.threaded
)
config_service: ConfigService = ConfigService(
    repository=ImplementedConfigRepository()
)
user_service: UserService = UserService(
    repository=ImplementedUserRepository(),
    bot=bot,
    config_service=config_service
)
pvp_service: PVPService = PVPService(
    repository=ImplementedPVPRepository(),
    bot=bot,
    config_service=config_service,
    user_service=user_service
)
pvpc_service: PVPCService = PVPCService(
    repository=ImplementedPVPCRepository(),
    bot=bot,
    config_service=config_service,
    user_service=user_service
)
admin_service: AdminService = AdminService(
    repository=ImplementedAdminRepository(),
    bot=bot,
    user_service=user_service,
    config_service=config_service
)


@celery_instance.on_after_finalize.connect
def setup_beat(sender: Celery, **_kwargs) -> None:
    sender.add_periodic_task(
        schedule=5,
        sig=pvp_finish_started.s()
    )
    sender.add_periodic_task(
        schedule=120,
        sig=pvp_close_expired.s()
    )
    sender.add_periodic_task(
        schedule=5,
        sig=pvpc_finish_started.s()
    )
    sender.add_periodic_task(
        schedule=120,
        sig=pvpc_close_expired.s()
    )


@celery_instance.task
def pvp_finish_started() -> None:
    pvp_service.auto_finish_started_games()


@celery_instance.task
def pvp_close_expired() -> None:
    pvp_service.auto_close_expired_games()


@celery_instance.task
def pvpc_finish_started() -> None:
    pvpc_service.auto_finish_started_games()


@celery_instance.task
def pvpc_close_expired() -> None:
    pvpc_service.auto_close_expired_games()


@celery_instance.task
def mailing() -> None:
    admin_service.mailing(
        settings.admin_tg_id,
        (ApiTelegramException,)
    )
