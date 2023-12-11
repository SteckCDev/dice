from decimal import Decimal
from typing import Final

from core.repositories import CurrencyRepository


PRECISION: Final[int] = 8


class CurrencyService:
    def __init__(self, repository: CurrencyRepository) -> None:
        self.__repo: CurrencyRepository = repository

    def get_btc_to_rub(self) -> Decimal | None:
        return self.__repo.get_btc_to_rub()

    def rub_to_btc(self, amount: int | float, currency: Decimal | None = None) -> Decimal | None:
        if amount == 0:
            return Decimal(0)

        if currency is None:
            currency = self.__repo.get_btc_to_rub()

        return None if currency is None else round(amount / currency, PRECISION)
