from dataclasses import dataclass
from fractions import Fraction
from typing import TYPE_CHECKING

from .scene_object import SceneObject
from .interface import IOnset
if TYPE_CHECKING:
    from .score_part import ScorePart
    from .part_measure import PartMeasure


@dataclass
class InPartMeasureModifier(IOnset, SceneObject):
    """
    Base class for symbols that change pitch or duration
    for following symbols - time signature, clef, ...
    """
    fractional_onset_: Fraction

    @property
    def in_measure_fractional_onset(self) -> Fraction:
        return self.fractional_onset_

    @property
    def in_measure_fractional_end_onset(self) -> Fraction:
        return self.fractional_onset_
    
    @property
    def in_measure_onset(self) -> int:
        onset =  self.in_measure_fractional_onset * self._get_divisions()
        assert onset.denominator == 1
        return onset.numerator
    
    def _get_divisions(self) -> int:
        return self.score_part.divisions
    
    @property
    def score_part(self) -> "ScorePart":
        from .score_part import ScorePart
        pm = self.part_measure
        return ScorePart.of(pm, lambda sp: sp.part_measures)
    
    @property
    def part_measure(self) -> "PartMeasure":
        from .part_measure import PartMeasure
        return PartMeasure.of(self, lambda pm: pm.modifiers)