"""Распознавание промежуточных страниц SSO Яндекса — чистые функции без сети.

Первый запрос к dzen.ru/news без cookie приходит не на новости, а на две
страницы синхронизации сессии, которые браузер проходит скриптом:

PUSH    sso.passport.yandex.ru/push — скрытая форма retpath/container/dzen,
        отправляется POST на адрес из поля host;
INSTALL sso.dzen.ru/install — ставит cookie sso_status=<root>:synchronized
        и уходит на retpath.

Это не защита от ботов: капчи на этих страницах нет. Капча распознаётся
отдельно и считается тупиком.
"""

import json
import re
from dataclasses import dataclass
from enum import Enum


class PageKind(Enum):
    NEWS = "news"
    SSO_PUSH = "sso_push"
    SSO_INSTALL = "sso_install"
    CAPTCHA = "captcha"
    UNKNOWN = "unknown"


class StubPageError(RuntimeError):
    """Вместо страницы новостей пришла заглушка, которую пройти не удалось."""


@dataclass(frozen=True)
class PushForm:
    action: str
    fields: dict[str, str]


@dataclass(frozen=True)
class InstallStep:
    cookie_name: str
    cookie_value: str
    cookie_domain: str
    retpath: str


_IT = re.compile(r"var it = (\{.*?\});")
_CONTAINER = re.compile(r"element2\.value = '([^']+)'")
_STORY_LINK = "/news/story/"


def classify(html: str, url: str) -> PageKind:
    if "showcaptcha" in url or "SmartCaptcha" in html:
        return PageKind.CAPTCHA
    if "sso.passport.yandex.ru/push" in url or ("element2.name = 'container'" in html):
        return PageKind.SSO_PUSH
    if "SSO.init(" in html and "cookieCheck" in html:
        return PageKind.SSO_INSTALL
    if _STORY_LINK in html:
        return PageKind.NEWS
    return PageKind.UNKNOWN


def _it(html: str) -> dict:
    m = _IT.search(html)
    if m is None:
        raise StubPageError("в странице SSO нет объекта `var it`")
    return json.loads(m.group(1))


def parse_push(html: str) -> PushForm:
    it = _it(html)
    m = _CONTAINER.search(html)
    if m is None:
        raise StubPageError("в странице SSO push нет поля container")
    fields = {"retpath": it["retpath"], "container": m.group(1)}
    if it.get("dzen") == "1":
        fields["dzen"] = "1"
    return PushForm(action=it["host"], fields=fields)


def parse_install(html: str) -> InstallStep:
    """Повторяет SSO.saveStatus: непустой authStatus → статус synchronized."""
    it = _it(html)
    if not it["authStatus"]:
        raise StubPageError("SSO install без authStatus — сессия не синхронизируется")
    return InstallStep(
        cookie_name="sso_status",
        cookie_value=f"{it['root']}:synchronized",
        cookie_domain="." + it["currentDomain"],
        retpath=it["retpath"],
    )
