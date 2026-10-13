from pathlib import Path

import pytest

SAMPLES = Path(__file__).resolve().parent.parent / "samples"


@pytest.fixture(scope="session")
def news_html() -> str:
    return (SAMPLES / "news.html").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def push_html() -> str:
    return (SAMPLES / "01_sso_push.html").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def install_html() -> str:
    return (SAMPLES / "02_sso_install.html").read_text(encoding="utf-8")
