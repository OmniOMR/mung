from dataclasses import dataclass
from fractions import Fraction
from abc import ABC, abstractmethod

from .in_measure_object import InMeasureObject


@dataclass
class DurationObject(InMeasureObject, ABC):
    """
    Extension of `InMeasureObject`,
    sits inside a measure and has a duration.
    """

    @property
    @abstractmethod
    def fractional_duration(self) -> Fraction:
        pass

    @property
    def duration(self) -> int:
        duration = self.score_part.divisions * self.fractional_duration
        assert duration.denominator == 1
        return duration.numerator

    @property
    def in_measure_fractional_end_onset(self) -> Fraction:
        return self.in_measure_fractional_onset + self.fractional_duration

    @property
    def global_fractional_end_onset(self) -> Fraction:
        return self.global_fractional_onset + self.fractional_duration
    