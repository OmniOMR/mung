from dataclasses import dataclass
from fractions import Fraction
from typing import TYPE_CHECKING

from .interface import InMeasureObject
if TYPE_CHECKING:
    from .score_part import ScorePart
    from .part_measure import PartMeasure


@dataclass
class InMeasureModifier(InMeasureObject):
    """
    Base class for symbols that change pitch or duration
    for following symbols - time signature, clef, ...
    """
    fractional_onset_: Fraction

    @property
    def in_measure_fractional_onset(self) -> Fraction:
        return self.fractional_onset_

    @property
    def score_part(self) -> "ScorePart":
        from .score_part import ScorePart
        pm = self.part_measure
        return ScorePart.of(pm, lambda sp: sp.part_measures)
    
    @property
    def part_measure(self) -> "PartMeasure":
        from .part_measure import PartMeasure
        return PartMeasure.of(self, lambda pm: pm.modifiers)