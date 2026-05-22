from dataclasses import dataclass

from .in_part_measure_modifier import InMeasureModifier
from .tokens import TimeSymbolToken, TimeSeparatorToken


@dataclass
class TimeSignature(InMeasureModifier):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/time/
    """
    numerator: int
    denominator: int
    symbol_type: TimeSymbolToken
    separator_type: TimeSeparatorToken

    def __post_init__(self) -> None:
        assert self.numerator > 0
        assert self.denominator > 0
    