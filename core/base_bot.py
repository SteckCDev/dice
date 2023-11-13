from abc import ABC, abstractmethod
from typing import Any


class BaseBotAPI(ABC):
    @abstractmethod
    def __init__(self):
        self.message_handler = ...
        self.callback_handler = ...
        self.infinity_polling = ...

    @abstractmethod
    def send_message(self, chat_id: int, text: str, markup: Any = None) -> int | None:
        ...

    @abstractmethod
    def edit_message(self, chat_id: int, message_id: int, text: str, markup: Any = None) -> int | None:
        ...

    @abstractmethod
    def get_chat_member(self, chat_id: int, user_tg_id: int) -> None:
        ...
