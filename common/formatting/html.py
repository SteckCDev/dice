from typing import Any


def bold(inner: Any) -> str:
    return f"<b>{inner}</b>"


def cursive(inner: Any) -> str:
    return f"<i>{inner}</i>"


def code(inner: Any) -> str:
    return f"<code>{inner}</code>"
