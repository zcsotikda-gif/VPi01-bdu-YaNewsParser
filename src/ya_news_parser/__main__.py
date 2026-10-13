"""Точка сборки: источник страницы → разбор → CSV."""

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

from .csv_sink import CsvHeadlineSink
from .fetcher import RequestsPageSource
from .parsing import parse_headlines
from .ports import HeadlineSink, PageSource
from .sso import StubPageError


def run(source: PageSource, sink: HeadlineSink) -> int:
    headlines = parse_headlines(source.fetch())
    if not headlines:
        raise StubPageError("страница получена, но заголовков в ней нет — разметка изменилась?")
    sink.write(headlines, fetched_at=datetime.now(UTC))
    return len(headlines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ya-news-parser",
                                     description="Заголовки Яндекс.Новостей в CSV")
    parser.add_argument("--out", type=Path, default=Path("news.csv"),
                        help="куда записать CSV (по умолчанию news.csv)")
    parser.add_argument("--html", type=Path,
                        help="разобрать сохранённый HTML вместо загрузки из сети")
    args = parser.parse_args(argv)

    source: PageSource
    if args.html:
        source = _FileSource(args.html)
    else:
        source = RequestsPageSource()
    try:
        count = run(source, CsvHeadlineSink(args.out))
    except StubPageError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return 2
    print(f"Записано заголовков: {count} → {args.out}")
    return 0


class _FileSource:
    def __init__(self, path: Path) -> None:
        self._path = path

    def fetch(self) -> str:
        return self._path.read_text(encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
