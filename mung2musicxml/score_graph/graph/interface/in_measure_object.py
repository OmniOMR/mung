from dataclasses import dataclass
from fractions import Fraction
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ..scene_object import SceneObject

if TYPE_CHECKING:
    from ..score_part import ScorePart
    from ..part_measure import PartMeasure


@dataclass
class InMeasureObject(SceneObject, ABC):
    """
    Printed symbol that sits inside a measure.
    It has an onset.
    """

    def __post_init__(self) -> None:
        assert self.in_measure_fractional_onset >= 0

    @property
    @abstractmethod
    def score_part(self) -> "ScorePart":
        pass

    @property
    @abstractmethod
    def part_measure(self) -> "PartMeasure":
        pass

    @property
    @abstractmethod
    def in_measure_fractional_onset(self) -> Fraction:
        pass

    @property
    def global_fractional_onset(self) -> Fraction:
        return (
            self.part_measure.global_fractional_onset + self.in_measure_fractional_onset
        )

    @property
    def global_onset(self) -> int:
        onset = self.score_part.divisions * self.global_fractional_onset
        assert onset.denominator == 1
        return onset.numerator
    
    @property
    def in_measure_onset(self) -> int:
        onset = self.score_part.divisions * self.in_measure_fractional_onset
        assert onset.denominator == 1
        return onset.numerator
