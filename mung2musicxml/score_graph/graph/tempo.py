from dataclasses import dataclass
from .interface import ScoreText


@dataclass(kw_only=True)
class Tempo(ScoreText):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/words/
    """

    pass
