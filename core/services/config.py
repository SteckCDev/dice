from core.repositories.config import ConfigRepository
from core.schemas.config import ConfigDTO


class ConfigService:
    def __init__(self, repository: ConfigRepository) -> None:
        self.__repo: ConfigRepository = repository

    def get(self) -> ConfigDTO:
        return self.__repo.get()
