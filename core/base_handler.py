from abc import ABC, abstractmethod


class BaseHandler(ABC):
    @abstractmethod
    def _prepare(self) -> bool:
        ...

    @abstractmethod
    def _process(self) -> None:
        ...

    def handle(self) -> None:
        if self._prepare():
            self._process()
