import pytest

from ya_news_parser import sso
from ya_news_parser.sso import PageKind, StubPageError

PUSH_URL = "https://sso.passport.yandex.ru/push?uuid=x&retpath=y"
INSTALL_URL = "https://sso.dzen.ru/install?uuid=x"
NEWS_URL = "https://dzen.ru/news?is_autologin_ya=true"


def test_classify_saved_pages(push_html, install_html, news_html):
    assert sso.classify(push_html, PUSH_URL) is PageKind.SSO_PUSH
    assert sso.classify(install_html, INSTALL_URL) is PageKind.SSO_INSTALL
    assert sso.classify(news_html, NEWS_URL) is PageKind.NEWS


def test_classify_captcha_and_unknown():
    assert sso.classify("", "https://dzen.ru/showcaptcha?x") is PageKind.CAPTCHA
    assert sso.classify("<html></html>", "https://dzen.ru/") is PageKind.UNKNOWN


def test_push_form(push_html):
    form = sso.parse_push(push_html)
    assert form.action.startswith("https://sso.dzen.ru/install?uuid=")
    assert set(form.fields) == {"retpath", "container", "dzen"}
    assert form.fields["retpath"].startswith("https://dzen.ru/news")


def test_install_step(install_html):
    step = sso.parse_install(install_html)
    assert step.cookie_name == "sso_status"
    assert step.cookie_value == "sso.passport.yandex.ru:synchronized"
    assert step.cookie_domain == ".dzen.ru"
    assert step.retpath.startswith("https://dzen.ru/news")


def test_page_without_state_object_is_error():
    with pytest.raises(StubPageError):
        sso.parse_push("<script>nothing</script>")
