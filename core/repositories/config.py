from abc import ABC, abstractmethod

from core.schemas.config import ConfigDTO


class ConfigRepository(ABC):
    @abstractmethod
    def get(self) -> ConfigDTO:
        ...

    @abstractmethod
    def update(self, dto: ConfigDTO) -> None:
        ...
