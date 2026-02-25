from dataclasses import dataclass

from .in_part_measure_modifier import InPartMeasureModifier
from .tokens import TimeSymbolToken, TimeSeparatorToken


@dataclass
class TimeSignature(InPartMeasureModifier):
    numerator: int
    denominator: int
    symbol_type: TimeSymbolToken
    separator_type: TimeSeparatorToken

    def __post_init__(self) -> None:
        assert self.numerator > 0
        assert self.denominator > 0
    