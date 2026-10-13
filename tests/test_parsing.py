"""Разбор зафиксированной страницы samples/news.html (снята 13.10.2026).

Числа ниже — измерения этой страницы; при замене образца их надо пересчитать.
"""

from urllib.parse import urlsplit

from ya_news_parser.parsing import parse_headlines


def test_every_story_once_with_title(news_html):
    headlines = parse_headlines(news_html)
    assert len(headlines) == 255
    assert len({h.url for h in headlines}) == len(headlines)
    assert all(h.title for h in headlines)


def test_urls_are_canonical_story_links(news_html):
    # Спортивные сюжеты живут на sportsdzen.ru — домен не проверяется, только путь.
    for h in parse_headlines(news_html):
        p = urlsplit(h.url)
        assert p.scheme == "https"
        assert p.path.startswith("/news/story/")
        assert not p.query


def test_first_headline_is_top_card(news_html):
    first = parse_headlines(news_html)[0]
    assert first.title.startswith("ВВС Украины подтвердили")
    assert first.rubric is None


def test_rubrics_come_from_block_headings(news_html):
    rubrics = {h.rubric for h in parse_headlines(news_html)}
    assert {"США", "Политика", "Спорт", "Авто"} <= rubrics


def test_non_news_page_gives_nothing(push_html):
    assert parse_headlines(push_html) == []
