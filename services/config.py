from schemas import ConfigDTO


class ConfigService:
    @staticmethod
    def get() -> ConfigDTO:
        return ConfigDTO(
            start_balance=1_000,
            start_beta_balance=20_000,
            min_bet=50,
            max_bet=10_000,
            pvb_fee=3,
        )
