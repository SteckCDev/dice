from typing import Final

from pydantic import ValidationError

from core.services.config import ConfigService
from core.schemas.config import UpdateConfig, ConfigDTO


ADJUST_COMMANDS: Final[dict[str, tuple[str, ...]]] = {
    "баланс": (
        "обычный",
        "бета"
    ),
    "комиссия": (
        "pvb",
        "pvp",
        "pvpc",
        "card",
        "wallet"
    ),
    "ставка": (
        "минимальная",
        "максимальная"
    ),
    "чат": (
        "раунды",
    )
}


class AdminService:
    def __init__(self, config_service: ConfigService) -> None:
        self.__config_service: ConfigService = config_service

        self.__config: UpdateConfig = UpdateConfig(
            **self.__config_service.get().model_dump()
        )

    def __find_and_adjust_field(self, request_params: list[str]) -> bool:
        request_params: list[str] = [arg.lower() for arg in request_params]

        if request_params[0] == "баланс":
            syntax: str = "Синтаксис команды: [баланс] [обычный / бета] [число]\n"
            current: str = "Текущие значения: обычный({start_balance}), бета({start_beta_balance})"
            tip: str = syntax + current
            
            tip = tip.format(
                start_balance=self.__config.start_balance,
                start_beta_balance=self.__config.start_beta_balance
            )
            
            if not len(request_params) == 3:
                raise ValueError(tip)

            if request_params[1] == "обычный":
                self.__config.start_balance = request_params[2]

            elif request_params[1] == "бета":
                self.__config.start_beta_balance = request_params[2]
                
            else:
                raise ValueError(tip)

        elif request_params[0] == "комиссия":
            syntax: str = "Синтаксис команды: [комиссия] [pvb / pvp / pvpc / card / wallet] [число]\n"
            current: str = "Текущие значения: pvb({pvb_fee}), pvp({pvp_fee}), pvpc({pvpc_fee}), " \
                           "card({card_withdrawal_fee}), wallet({btc_withdrawal_fee})"
            tip: str = syntax + current
            
            tip = tip.format(
                pvb_fee=self.__config.pvb_fee,
                pvp_fee=self.__config.pvp_fee,
                pvpc_fee=self.__config.pvpc_fee,
                card_withdrawal_fee=self.__config.card_withdrawal_fee,
                btc_withdrawal_fee=self.__config.btc_withdrawal_fee
            )
            
            if not len(request_params) == 3:
                raise ValueError(tip)
            
            if request_params[1] == "pvb":
                self.__config.pvb_fee = request_params[2]

            elif request_params[1] == "pvp":
                self.__config.pvp_fee = request_params[2]

            elif request_params[1] == "pvpc":
                self.__config.pvpc_fee = request_params[2]

            elif request_params[1] == "card":
                self.__config.card_withdrawal_fee = request_params[2]

            elif request_params[1] == "wallet":
                self.__config.btc_withdrawal_fee = request_params[2]
                
            else:
                raise ValueError(tip)
                
        elif request_params[0] == "ставка":
            syntax: str = "Синтаксис команды: [ставка] [минимальная / максимальная] [число]\n"
            current: str = "Текущие значения: минимальная({min_bet}), максимальная({max_bet})"
            tip: str = syntax + current
            
            tip = tip.format(
                min_bet=self.__config.min_bet,
                max_bet=self.__config.max_bet
            )
            
            if not len(request_params) == 3:
                raise ValueError(tip)
            
            if request_params[1] == "минимальная":
                self.__config.min_bet = request_params[2]
                
            elif request_params[1] == "максимальная":
                self.__config.max_bet = request_params[2]
                
            else:
                raise ValueError(tip)
            
        elif request_params[0] == "чат":
            syntax: str = "Синтаксис команды: [чат] [раунды] [число]\n"
            current: str = "Текущие значения: раунды({pvpc_max_rounds})"
            tip: str = syntax + current
            
            tip = tip.format(
                pvpc_max_rounds=self.__config.pvpc_max_rounds
            )
            
            if not len(request_params) == 3:
                raise ValueError(tip)
            
            if request_params[1] == "раунды":
                self.__config.pvpc_max_rounds = request_params[2]
            else:
                raise ValueError(tip)
            
        else:
            return False
                
        self.__config_service.update(
            ConfigDTO(
                **self.__config.model_dump()
            )
        )
        
        return True

    def try_to_adjust_config_field(self, request_params: list[str]) -> bool | str:
        """
        Returns custom string representation of error if there is one,
        True if field adjusted,
        False if section not found
        """

        try:
            return self.__find_and_adjust_field(request_params)
        except ValidationError as err:
            return UpdateConfig.get_first_error_msg(err)
        except ValueError as err:
            return str(err)
