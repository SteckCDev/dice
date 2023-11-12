from contextlib import suppress

import requests
from requests.exceptions import RequestException


API = "https://blockchain.info/ticker"
PRECISION = 8


class CurrencyService:
    @staticmethod
    def get_currency() -> float | None:
        with suppress(KeyError, RequestException):
            currency = requests.get(API).json()["RUB"]["15m"]
            return currency if isinstance(currency, float) else None

    @staticmethod
    def rub_to_btc(amount: int | float, currency: float | None = get_currency()) -> float | None:
        if currency is None:
            return

        return round(amount / currency, PRECISION)
