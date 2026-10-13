"""Что ядру нужно от внешнего мира."""

from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from .models import Headline


class PageSource(Protocol):
    def fetch(self) -> str:
        """HTML страницы новостей; бросает StubPageError, если пришла заглушка."""
        ...


class HeadlineSink(Protocol):
    def write(self, headlines: Sequence[Headline], fetched_at: datetime) -> None: ...
