import csv
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

from .models import Headline

FIELDS = ["title", "rubric", "url", "fetched_at"]


class CsvHeadlineSink:
    """CSV в utf-8-sig: BOM нужен, чтобы Excel открыл кириллицу без ручного импорта."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def write(self, headlines: Sequence[Headline], fetched_at: datetime) -> None:
        stamp = fetched_at.isoformat(timespec="seconds")
        with self._path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            for h in headlines:
                writer.writerow({"title": h.title, "rubric": h.rubric or "",
                                 "url": h.url, "fetched_at": stamp})
