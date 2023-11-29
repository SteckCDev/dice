from abc import ABC, abstractmethod
from typing import Any, Callable


class AbstractBotAPI(ABC):
    @abstractmethod
    def message_handler(self) -> Callable:
        ...

    @abstractmethod
    def callback_handler(self) -> Callable:
        ...

    @abstractmethod
    def infinity_polling(self) -> Callable:
        ...

    @abstractmethod
    def send_message(self, chat_id: int, text: str, markup: Any = None) -> int | None:
        ...

    @abstractmethod
    def edit_message(self, chat_id: int, message_id: int, text: str, markup: Any = None) -> int | None:
        ...

    @abstractmethod
    def answer_callback(self, call_id: int, text: str) -> None:
        ...

    @abstractmethod
    def send_dice(self, chat_id: int) -> int | None:
        ...

    @abstractmethod
    def is_user_subscribed(self, chat_id: int, user_tg_id: int) -> bool:
        ...
