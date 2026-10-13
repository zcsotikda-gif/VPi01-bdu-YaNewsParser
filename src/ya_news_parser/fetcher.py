"""Получение страницы новостей через requests с проходом SSO."""

import requests

from . import sso
from .sso import PageKind, StubPageError

NEWS_URL = "https://dzen.ru/news"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0 Safari/537.36"
)
# PUSH → INSTALL → NEWS: два шага SSO и запас на один повтор.
MAX_STEPS = 4


class RequestsPageSource:
    def __init__(self, session: requests.Session | None = None,
                 url: str = NEWS_URL, timeout: float = 20.0) -> None:
        self._session = session or requests.Session()
        self._session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "ru-RU,ru;q=0.9",
        })
        self._url = url
        self._timeout = timeout

    def fetch(self) -> str:
        response = self._get(self._url)
        for _ in range(MAX_STEPS):
            kind = sso.classify(response.text, response.url)
            if kind is PageKind.NEWS:
                return response.text
            if kind is PageKind.SSO_PUSH:
                form = sso.parse_push(response.text)
                response = self._send(self._session.post(
                    form.action, data=form.fields, timeout=self._timeout))
            elif kind is PageKind.SSO_INSTALL:
                step = sso.parse_install(response.text)
                self._session.cookies.set(step.cookie_name, step.cookie_value,
                                          domain=step.cookie_domain, path="/")
                response = self._get(step.retpath)
            else:
                raise StubPageError(f"страница {kind.value} по адресу {response.url}")
        raise StubPageError(f"SSO не пройден за {MAX_STEPS} шага, последний адрес {response.url}")

    def _get(self, url: str) -> requests.Response:
        return self._send(self._session.get(url, timeout=self._timeout))

    @staticmethod
    def _send(response: requests.Response) -> requests.Response:
        response.raise_for_status()
        return response
