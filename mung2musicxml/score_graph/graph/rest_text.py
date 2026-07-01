from dataclasses import dataclass

from .interface import ScoreText


@dataclass(kw_only=True)
class RestText(ScoreText):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/words/
    """

    pass
