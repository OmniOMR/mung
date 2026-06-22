from dataclasses import dataclass
from typing import Optional

from .tokens import FontStyleToken, FontWeightToken


@dataclass
class WordsAttributes:
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/words/
    """
    font_family: Optional[str] = None
    font_style: Optional[FontStyleToken] = None
    font_weight: Optional[FontWeightToken] = None
    font_size: Optional[int] = None
