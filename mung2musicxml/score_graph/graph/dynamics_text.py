from dataclasses import dataclass

from .interface import ScoreText


@dataclass(kw_only=True)
class DynamicsText(ScoreText):
    """
    Represent dynamic diminuendo and crescendo.

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/words/
    """

    pass
