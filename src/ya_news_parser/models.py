from dataclasses import dataclass


@dataclass(frozen=True)
class Headline:
    """Заголовок одного сюжета.

    rubric — название блока на странице; None у верхнего блока, у которого
    на странице нет заголовка.
    """

    title: str
    url: str
    rubric: str | None
