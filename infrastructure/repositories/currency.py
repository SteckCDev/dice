from contextlib import suppress
from decimal import Decimal
from typing import Final

import requests
from requests.exceptions import RequestException

from core.repositories import CurrencyRepository


API_URL: Final[str] = "https://blockchain.info/ticker"


class BlockchainInfoCurrencyRepository(CurrencyRepository):
    def __init__(self) -> None:
        pass

    def get_btc_to_rub(self) -> Decimal | None:
        with suppress(KeyError, RequestException):
            currency = requests.get(API_URL).json()["RUB"]["15m"]
            return Decimal(currency) if isinstance(currency, float) else None
