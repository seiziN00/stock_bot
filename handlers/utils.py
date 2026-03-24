"""Shared utilities for Telegram handlers."""

import re

_MARKDOWNV2_ESCAPE = re.compile(r"([_*\[\]()~`>#+\-=|{}.!])")


def escape_md(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2."""
    return _MARKDOWNV2_ESCAPE.sub(r"\\\1", str(text))
