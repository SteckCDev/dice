from enum import Enum


class Menu(str, Enum):
    GAMES: str = "🎲 Игры"
    PROFILE: str = "🙋‍♂️ Профиль"
    LOTTERY: str = "🎉 Розыгрыши"
    SUPPORT: str = "🤖 Поддержка"
    ADMIN: str = "🍷 Админ-панель"
