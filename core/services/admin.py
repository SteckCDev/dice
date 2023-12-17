from time import sleep
from typing import Any, Final

from pydantic import ValidationError

from core.abstract_bot import AbstractBotAPI
from core.repositories import AdminRepository
from core.schemas.config import UpdateConfig, ConfigDTO
from core.schemas.user import UserDTO
from core.services.config import ConfigService
from core.services.user import UserService


ADJUST_COMMANDS: Final[dict[str, tuple[str, ...]]] = {
    "реквизиты": (
        "карта",
        "биткоин"
    ),
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
    "игроки": (
        "отмена",
        "завершение"
    ),
    "чат": (
        "раунды",
        "отмена",
        "завершение"
    ),
    "транзакция": (
        "пополнение",
        "вывод"
    ),
    "фейк": (
        "периодичность",
        "минимальная",
        "максимальная"
    ),
    "подписки": (
        "добавить",
        "удалить"
    )
}


class AdminService:
    def __init__(
            self,
            repository: AdminRepository,
            bot: AbstractBotAPI,
            user_service: UserService,
            config_service: ConfigService
    ) -> None:
        self.__repo: AdminRepository = repository
        self.__bot: AbstractBotAPI = bot
        self.__user_service: UserService = user_service
        self.__config_service: ConfigService = config_service

        self.__config: UpdateConfig = UpdateConfig(
            **self.__config_service.get().model_dump()
        )

    def __find_and_adjust_field(self, request_params: list[str]) -> bool:
        _request_params: list[str] = [arg.lower() for arg in request_params]

        if _request_params[0] == "реквизиты":
            syntax: str = "Синтаксис команды: [реквизиты] [карта / биткоин] [строка]\n"
            current: str = "Текущие значения: карта({card_details}), биткоин({btc_details})"
            tip: str = syntax + current

            tip = tip.format(
                card_details=self.__config.card_details,
                btc_details=self.__config.btc_details
            )

            if not len(_request_params) >= 3:
                raise ValueError(tip)

            if _request_params[1] == "карта":
                self.__config.card_details = " ".join(_request_params[2:])

            elif _request_params[1] == "биткоин":
                # using original params with raw case, because segwit bitcoin addresses are case-sensetive
                self.__config.btc_details = " ".join(request_params[2:])

            else:
                raise ValueError(tip)

        elif _request_params[0] == "баланс":
            syntax: str = "Синтаксис команды: [баланс] [обычный / бета] [число]\n"
            current: str = "Текущие значения: обычный({start_balance}), бета({start_beta_balance})"
            tip: str = syntax + current
            
            tip = tip.format(
                start_balance=self.__config.start_balance,
                start_beta_balance=self.__config.start_beta_balance
            )
            
            if not len(_request_params) == 3:
                raise ValueError(tip)

            if _request_params[1] == "обычный":
                self.__config.start_balance = _request_params[2]

            elif _request_params[1] == "бета":
                self.__config.start_beta_balance = _request_params[2]
                
            else:
                raise ValueError(tip)

        elif _request_params[0] == "комиссия":
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
            
            if not len(_request_params) == 3:
                raise ValueError(tip)
            
            if _request_params[1] == "pvb":
                self.__config.pvb_fee = _request_params[2]

            elif _request_params[1] == "pvp":
                self.__config.pvp_fee = _request_params[2]

            elif _request_params[1] == "pvpc":
                self.__config.pvpc_fee = _request_params[2]

            elif _request_params[1] == "card":
                self.__config.card_withdrawal_fee = _request_params[2]

            elif _request_params[1] == "wallet":
                self.__config.btc_withdrawal_fee = _request_params[2]
                
            else:
                raise ValueError(tip)
                
        elif _request_params[0] == "ставка":
            syntax: str = "Синтаксис команды: [ставка] [минимальная / максимальная] [число]\n"
            current: str = "Текущие значения: минимальная({min_bet}), максимальная({max_bet})"
            tip: str = syntax + current
            
            tip = tip.format(
                min_bet=self.__config.min_bet,
                max_bet=self.__config.max_bet
            )
            
            if not len(_request_params) == 3:
                raise ValueError(tip)
            
            if _request_params[1] == "минимальная":
                self.__config.min_bet = _request_params[2]
                
            elif _request_params[1] == "максимальная":
                self.__config.max_bet = _request_params[2]
                
            else:
                raise ValueError(tip)

        elif _request_params[0] == "игроки":
            syntax: str = "Синтаксис команды: [игроки] [отмена / завершение] [минуты]\n"
            current: str = "Текущие значения: отмена ({pvp_ttl_after_creation}), завершение ({pvp_ttl_after_start})"
            tip: str = syntax + current

            tip = tip.format(
                pvp_ttl_after_creation=self.__config.pvp_ttl_after_creation,
                pvp_ttl_after_start=self.__config.pvp_ttl_after_start
            )

            if not len(_request_params) == 3:
                raise ValueError(tip)

            if _request_params[1] == "отмена":
                self.__config.pvp_ttl_after_creation = _request_params[2]

            elif _request_params[1] == "завершение":
                self.__config.pvp_ttl_after_start = _request_params[2]

            else:
                raise ValueError(tip)

        elif _request_params[0] == "чат":
            syntax: str = "Синтаксис команды: [чат] [раунды / отмена / завершение] [число / минуты]\n"
            current: str = "Текущие значения: раунды({pvpc_max_rounds}), отмена ({pvpc_ttl_after_creation}), " \
                           "завершение ({pvpc_ttl_after_start})"
            tip: str = syntax + current
            
            tip = tip.format(
                pvpc_max_rounds=self.__config.pvpc_max_rounds,
                pvpc_ttl_after_creation=self.__config.pvpc_ttl_after_creation,
                pvpc_ttl_after_start=self.__config.pvpc_ttl_after_start
            )
            
            if not len(_request_params) == 3:
                raise ValueError(tip)
            
            if _request_params[1] == "раунды":
                self.__config.pvpc_max_rounds = _request_params[2]

            elif _request_params[1] == "отмена":
                self.__config.pvpc_ttl_after_creation = _request_params[2]

            elif _request_params[1] == "завершение":
                self.__config.pvpc_ttl_after_start = _request_params[2]

            else:
                raise ValueError(tip)

        elif _request_params[0] == "транзакция":
            syntax: str = "Синтаксис команды: [транзакция] [пополнение / вывод] [число]\n"
            current: str = "Текущие значения: пополнение({min_deposit}), вывод({min_withdraw})"
            tip: str = syntax + current

            tip = tip.format(
                min_deposit=self.__config.min_deposit,
                min_withdraw=self.__config.min_withdraw
            )

            if not len(_request_params) == 3:
                raise ValueError(tip)

            if _request_params[1] == "пополнение":
                self.__config.min_bet = _request_params[2]

            elif _request_params[1] == "вывод":
                self.__config.max_bet = _request_params[2]

            else:
                raise ValueError(tip)

        elif _request_params[0] == "фейк":
            syntax: str = "Синтаксис команды: [фейк] [периодичность / минимальная / максимальная] [минуты / число]\n"
            current: str = "Текущие значения: периодичность({pvpf_creation_periodicity}), " \
                           "минимальная({pvpf_min_bet}), максимальная({pvpf_max_bet})"
            tip: str = syntax + current

            tip = tip.format(
                pvpf_creation_periodicity=self.__config.pvpf_creation_periodicity,
                pvpf_min_bet=self.__config.pvpf_min_bet,
                pvpf_max_bet=self.__config.pvpf_max_bet
            )

            if not len(_request_params) == 3:
                raise ValueError(tip)

            if _request_params[1] == "периодичность":
                self.__config.pvpf_creation_periodicity = _request_params[2]

            elif _request_params[1] == "минимальная":
                self.__config.min_bet = _request_params[2]

            elif _request_params[1] == "максимальная":
                self.__config.max_bet = _request_params[2]

            else:
                raise ValueError(tip)

        elif _request_params[0] == "подписки":
            syntax: str = "Синтаксис команды: [подписки] [добавить / удалить] [число]\n"
            current: str = "Текущие значения: {chat_list}"
            tip: str = syntax + current

            chat_list: str = "не заданы"

            if self.__config.required_chats:
                chat_list = "\n"
                for i, chat in enumerate(self.__config.required_chats, 1):
                    chat_list += f"  {i}: {chat}\n"

            tip = tip.format(
                chat_list=chat_list
            )

            if not len(_request_params) == 3:
                raise ValueError(tip)

            if _request_params[1] == "добавить":
                if not _request_params[2][1:].isdigit():
                    raise ValueError(tip)

                if self.__config.required_chats:
                    self.__config.required_chats.append(
                        int(_request_params[2])
                    )
                else:
                    self.__config.required_chats = [int(_request_params[2])]

            elif _request_params[1] == "удалить":
                if not _request_params[2].isdigit():
                    raise ValueError(tip)

                try:
                    self.__config.required_chats.pop(
                        int(_request_params[2]) - 1
                    )
                except IndexError:
                    raise ValueError(tip)

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

    def set_mailing_text(self, text: str) -> None:
        self.__repo.set_mailing_text(text)

    def get_mailing_text(self) -> str | None:
        return self.__repo.get_mailing_text()

    def mailing(self, admin_tg_id: int, to_except: tuple[Exception | Any]) -> None:
        users: list[UserDTO] | None = self.__user_service.get_all()
        mail: str | None = self.__repo.get_mailing_text()

        if users is None:
            return

        if mail is None:
            self.__bot.send_message(admin_tg_id, "Не задан текст рассылки")
            return

        succeed: int = 0
        failed: int = 0

        for i, user in enumerate(users):
            try:
                self.__bot.send_message(user.tg_id, mail)
                succeed += 1
            except to_except:
                failed += 1
                sleep(3)

            if not i % 20:
                sleep(1)

        self.__bot.send_message(admin_tg_id, f"Успешно отправлено: {succeed}\nНе удалось: {failed}")
