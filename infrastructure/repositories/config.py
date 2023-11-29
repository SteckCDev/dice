from core.repositories import ConfigRepository
from core.schemas.config import Config, ConfigDTO


class MockConfigRepository(ConfigRepository):
    def __init__(self) -> None:
        pass

    def get(self) -> ConfigDTO:
        return ConfigDTO(
            **Config().model_dump()
        )
