from abc import ABC, abstractmethod
from decimal import Decimal


class CurrencyRepository(ABC):
    @abstractmethod
    def get_btc_to_rub(self) -> Decimal | None:
        ...
