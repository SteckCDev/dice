from enum import Enum


class Menu(str, Enum):
    GAMES = "🎲 Игры"
    PROFILE = "🙋‍♂️ Профиль"
    LOTTERY = "🎉 Розыгрыши"
    SUPPORT = "🤖 Поддержка"
