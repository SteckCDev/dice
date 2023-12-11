import re
from typing import Any, Final

from templates.regexes import RegEx


CLEAN_PATTERN: Final[re.Pattern] = re.compile(RegEx.HTML_TAG)


def remove_tags(marked_up: str) -> str:
    return re.sub(CLEAN_PATTERN, "", marked_up)


def bold(inner: Any) -> str:
    return f"<b>{inner}</b>"


def cursive(inner: Any) -> str:
    return f"<i>{inner}</i>"


def link(inner: Any, url: str) -> str:
    return f"<a href='{url}'>{inner}</a>"


def code(inner: Any) -> str:
    return f"<code>{inner}</code>"
