from dataclasses import dataclass

from .tokens import ClefSign
from .in_part_measure_modifier import InPartMeasureModifier

# TODO: support clef transposition

@dataclass
class Clef(InPartMeasureModifier):
    __priority__ = 0
    sign: ClefSign
    line: int

    def __post_init__(self) -> None:
        assert 0 < self.line < 6

    @property
    def number(self) -> int:
        from .staff import Staff
        return Staff.of(self, lambda s: s.other_symbols).staff_id
