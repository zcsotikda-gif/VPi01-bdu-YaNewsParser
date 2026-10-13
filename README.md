# ya-news-parser

Собирает заголовки с главной страницы Яндекс.Новостей (`dzen.ru/news`) и
сохраняет их в CSV: `title, rubric, url, fetched_at`.

## Установка

```sh
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Запуск

```sh
.venv/bin/python -m ya_news_parser                    # → news.csv
.venv/bin/python -m ya_news_parser --out today.csv
.venv/bin/python -m ya_news_parser --html samples/news.html   # без сети
```

CSV пишется в `utf-8-sig` и открывается в Excel без ручного импорта.
Время `fetched_at` в UTC. Одна строка на сюжет; `rubric` пустая у верхнего
блока страницы, у которого нет заголовка.

Код выхода `2` — вместо новостей пришла заглушка (капча, неизвестная страница)
или в странице не нашлось ни одного заголовка.

## Как получается страница

Запрос к `dzen.ru/news` без cookie сначала приходит на две страницы
синхронизации сессии Яндекса, которые браузер проходит скриптом. Загрузчик
повторяет эти шаги через `requests.Session`: отправляет скрытую форму,
ставит cookie `sso_status` и запрашивает новости ещё раз. Капчу он не обходит.

## Устройство

```
src/ya_news_parser/
  parsing.py   HTML → заголовки (чистая функция)
  sso.py       распознавание страниц SSO и капчи (чистые функции)
  fetcher.py   requests + проход SSO
  csv_sink.py  запись CSV
  ports.py     протоколы источника и приёмника
  __main__.py  сборка и CLI
samples/       снятые страницы: две SSO-заглушки и страница новостей — фикстуры тестов
```

## Тесты

```sh
.venv/bin/pytest
.venv/bin/ruff check
docker compose -f docker/compose.yaml up --build --abort-on-container-exit
```

Тесты работают без сети по `samples/`. Разметка Дзена меняется; когда парсер
перестаёт находить заголовки, снимите новую страницу и пересчитайте числа в
`tests/test_parsing.py`.
