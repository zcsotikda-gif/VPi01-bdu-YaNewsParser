"""Извлечение заголовков из HTML страницы dzen.ru/news — чистая функция.

Якоря — атрибуты data-testid и адрес сюжета, а не CSS-классы: классы на
странице хешированные (`news-site--card-news__cardNewsWrapper-2Z`) и меняются
при каждой сборке фронтенда.

- заголовок — текст ссылки на /news/story/<id>; у большой карточки есть ещё
  ссылка-картинка без текста, она пропускается;
- один сюжет встречается в нескольких рубриках, иногда с другой формулировкой —
  берётся первое появление сверху вниз;
- рубрика — <h2> внутри ближайшего предка data-testid="rubricN".
"""

import re
from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup

from .models import Headline

_RUBRIC = re.compile(r"^rubric\d+$")
_STORY_PATH = "/news/story/"


def _canonical(href: str) -> str:
    """Без query: lang и persistent_id не меняют сюжет."""
    p = urlsplit(href)
    return urlunsplit((p.scheme, p.netloc, p.path, "", ""))


def parse_headlines(html: str) -> list[Headline]:
    soup = BeautifulSoup(html, "html.parser")
    result: dict[str, Headline] = {}
    for a in soup.select(f'a[href*="{_STORY_PATH}"]'):
        title = a.get_text(" ", strip=True)
        if not title:
            continue
        url = _canonical(a["href"])
        if url in result:
            continue
        box = a.find_parent(attrs={"data-testid": _RUBRIC})
        h2 = box.find("h2") if box else None
        rubric = h2.get_text(" ", strip=True) if h2 else None
        result[url] = Headline(title=title, url=url, rubric=rubric)
    return list(result.values())
