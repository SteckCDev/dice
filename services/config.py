from typing import Final

from schemas import ConfigDTO


class ConfigService:
    @staticmethod
    def get() -> ConfigDTO:
        return ConfigDTO(
            start_balance=1000,
            start_beta_balance=20000,
        )
