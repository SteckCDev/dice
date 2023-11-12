from typing import Any


def escape(string: str) -> str:
    unsafe = ("<", ">", "&", "\"", "'")

    for char in unsafe:
        string = str.replace(string, char, "")

    return string


def nl(repeat: int = 1) -> str:
    return "\n" * repeat


def bold(string: Any) -> str:
    return f"<b>{string}</b>"


def cursive(string: Any) -> str:
    return f"<i>{string}</i>"


def code(string: Any) -> str:
    return f"<code>{string}</code>"
