from enum import Enum, unique


@unique
class RegEx(str, Enum):
    AMOUNT: str = r"^[0-9]*[.,]?[0-9]+$"
    BTC_WALLET: str = r"^(?=.*[0-9])(?=.*[a-zA-Z])[\da-zA-Z]{27,50}$"
    XMR_WALLET: str = r"^4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}$"
    CARD: str = r"(\d{4}([ ]|)\d{4}([ ]|)\d{4}([ ]|)\d{4})"
    PHONE: str = r"^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$"
    HTML_TAG: str = r"<.*?>"
