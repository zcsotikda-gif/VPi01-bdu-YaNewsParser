"""Проход SSO на подменённой сессии: сеть не нужна, ответы — сохранённые страницы."""

import pytest
from requests.cookies import RequestsCookieJar

from ya_news_parser.fetcher import RequestsPageSource
from ya_news_parser.sso import StubPageError


class FakeResponse:
    def __init__(self, text: str, url: str) -> None:
        self.text = text
        self.url = url

    def raise_for_status(self) -> None:
        pass


class FakeDzen:
    """Ведёт себя как dzen.ru: без cookie sso_status отдаёт SSO, с ней — новости."""

    def __init__(self, push_html: str, install_html: str, news_html: str) -> None:
        self.headers: dict[str, str] = {}
        self.cookies = RequestsCookieJar()
        self.calls: list[str] = []
        self._push, self._install, self._news = push_html, install_html, news_html

    def get(self, url, timeout):
        self.calls.append("GET")
        if self.cookies.get("sso_status"):
            return FakeResponse(self._news, url)
        return FakeResponse(self._push, "https://sso.passport.yandex.ru/push?uuid=x")

    def post(self, url, data, timeout):
        self.calls.append("POST")
        assert url.startswith("https://sso.dzen.ru/install")
        assert set(data) == {"retpath", "container", "dzen"}
        return FakeResponse(self._install, url)


def test_passes_sso_chain(push_html, install_html, news_html):
    session = FakeDzen(push_html, install_html, news_html)
    html = RequestsPageSource(session=session).fetch()

    assert html is news_html
    assert session.cookies.get("sso_status") == "sso.passport.yandex.ru:synchronized"
    assert session.calls == ["GET", "POST", "GET"]


def test_captcha_is_error():
    class Captcha(FakeDzen):
        def get(self, url, timeout):
            return FakeResponse("", "https://dzen.ru/showcaptcha?x")

    with pytest.raises(StubPageError, match="captcha"):
        RequestsPageSource(session=Captcha("", "", "")).fetch()
