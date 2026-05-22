from dataclasses import dataclass
from fractions import Fraction
from typing import TYPE_CHECKING
from functools import cached_property

from .scene_object import SceneObject
from .part_measure import PartMeasure
if TYPE_CHECKING:
    from .score import Score


@dataclass
class ScoreMeasure(SceneObject):
    """
    Contains all `PartMeasure`s across `Score`
    that have the same `id`.
    """
    id: int
    part_measures: list[PartMeasure]
    is_new_system: bool
    
    def __post_init__(self) -> None:
        assert len(self.part_measures) > 0
        assert all(m.id == self.id for m in self.part_measures)
    
    @cached_property
    def previous(self) -> "ScoreMeasure":
        assert self.id > 1
        return self.score.get_system_measure_by_id(self.id - 1)

    @cached_property
    def fractional_onset(self) -> Fraction:
        if self.id == 1:
            return Fraction(0)
        return self.previous.fractional_end_onset
    
    @cached_property
    def fractional_duration(self) -> Fraction:
        return self._get_duration_impl()
    
    @cached_property
    def fractional_end_onset(self) -> Fraction:
        return self.fractional_onset + self.fractional_duration
    
    def _get_duration_impl(self) -> Fraction:
        return max((pm.fractional_duration for pm in self.part_measures), default=Fraction(0))
    
    @property
    def score(self) -> "Score":
        from .score import Score
        return Score.of(self, lambda s: s.score_measures)        

    def get_most_common_onset(self) -> Fraction:
        return min(
            (pm.in_measure_fractional_onset for pm in self.part_measures if pm.in_measure_fractional_onset > 0),
            default=Fraction(0)
        )

    def _check_part_measure_in_system_measure(self, part_measure: PartMeasure) -> None:
        assert part_measure.system_measure == self

    def get_expected_onset_for_part_measure(self, part_measure: PartMeasure) -> int:
        self._check_part_measure_in_system_measure(part_measure)
        onset = part_measure.score_part.divisions * self.fractional_onset
        assert onset.denominator == 1
        return onset.numerator
    
    def get_expected_end_onset_for_part_measure(self, part_measure: PartMeasure) -> int:
        self._check_part_measure_in_system_measure(part_measure)
        end = part_measure.score_part.divisions * self.fractional_end_onset
        assert end.denominator == 1
        return end.numerator
    
    def get_expected_duration_for_part_measure(self, part_measure: PartMeasure) -> int:
        self._check_part_measure_in_system_measure(part_measure)
        duration = part_measure.score_part.divisions * self.fractional_duration
        assert duration.denominator == 1
        return duration.numerator
    