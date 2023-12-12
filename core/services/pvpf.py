from typing import Final
from random import randint, choice

from core.abstract_bot import AbstractBotAPI
from core.repositories import PVPFRepository
from core.services.config import ConfigService
from core.services.pvp import PVPService
from core.services.user import UserService
from core.schemas.pvp import CreatePVPDTO
from core.schemas.user import UserDTO


ATTEMPT_FREQUENCY_SECONDS: Final[int] = 120


class PVPFService:
    def __init__(
            self,
            repository: PVPFRepository,
            bot: AbstractBotAPI,
            user_service: UserService,
            config_service: ConfigService,
            pvp_service: PVPService
    ) -> None:
        self.__repo: PVPFRepository = repository
        self.__bot: AbstractBotAPI = bot
        self.__user_service: UserService = user_service
        self.__config_service: ConfigService = config_service
        self.__pvp_service: PVPService = pvp_service

        self.config = self.__config_service.get()

    def toggle(self) -> bool:
        return self.__repo.toggle()

    def get_status(self) -> bool:
        return self.__repo.get_status()

    def estimated_creation_frequency_seconds(self, probability: int | None = None) -> int:
        if probability is None:
            return ATTEMPT_FREQUENCY_SECONDS * self.config.pvpf_creation_probability

        return ATTEMPT_FREQUENCY_SECONDS * probability

    def auto_create_game(self) -> None:
        if not self.__repo.get_status():
            return

        skip: bool = randint(1, self.config.pvpf_creation_probability) != self.config.pvpf_creation_probability

        if skip:
            return

        fakes: list[UserDTO] | None = self.__user_service.get_fakes()

        if fakes is None:
            return

        fake: UserDTO = choice(fakes)
        bet: int = randint(self.config.pvpf_min_bet, self.config.pvpf_max_bet)

        self.__pvp_service.create(
            CreatePVPDTO(
                creator_tg_id=fake.tg_id,
                bet=bet,
                beta_mode=False
            )
        )
