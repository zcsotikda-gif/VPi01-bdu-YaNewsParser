import csv
from datetime import UTC, datetime

from ya_news_parser.csv_sink import FIELDS, CsvHeadlineSink
from ya_news_parser.models import Headline


def test_writes_rows_with_bom_and_utc_stamp(tmp_path):
    out = tmp_path / "news.csv"
    rows = [Headline("Заголовок, с запятой", "https://dzen.ru/news/story/1", None),
            Headline("Второй", "https://dzen.ru/news/story/2", "Спорт")]
    CsvHeadlineSink(out).write(rows, datetime(2026, 10, 13, 9, 0, tzinfo=UTC))

    assert out.read_bytes().startswith(b"\xef\xbb\xbf")
    with out.open(encoding="utf-8-sig", newline="") as f:
        got = list(csv.DictReader(f))
    assert list(got[0]) == FIELDS
    assert got[0]["title"] == "Заголовок, с запятой"
    assert got[0]["rubric"] == ""
    assert got[1]["rubric"] == "Спорт"
    assert got[1]["fetched_at"] == "2026-10-13T09:00:00+00:00"
