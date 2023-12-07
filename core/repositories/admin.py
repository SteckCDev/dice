from abc import ABC, abstractmethod


class AdminRepository(ABC):
    @abstractmethod
    def set_mailing_text(self, text: str) -> None:
        ...

    @abstractmethod
    def get_mailing_text(self) -> str | None:
        ...
