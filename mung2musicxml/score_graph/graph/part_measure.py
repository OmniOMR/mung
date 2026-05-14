from dataclasses import dataclass, field
from fractions import Fraction
from typing import TYPE_CHECKING, Optional
from functools import cached_property

from .scene_object import SceneObject
from .subevent import Subevent
from .durable import Durable
from .repeat import RepeatBar
from .in_part_measure_modifier import InMeasureModifier
from ...utils import flatten
if TYPE_CHECKING:
    from .score_measure import ScoreMeasure
    from .score_part import ScorePart


@dataclass
class PartMeasure(SceneObject):
    """
    Measure of an instrument.

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/measure-partwise/
    """
    id: int
    subevents: list[Subevent]
    modifiers: list[InMeasureModifier]
    visible: bool = True
    all_symbols: list[Subevent | InMeasureModifier] = field(init=False)

    def __post_init__(self) -> None:
        self.subevents.sort(key=lambda s: s.in_measure_fractional_onset)
        self.modifiers.sort(key=lambda m: m.in_measure_fractional_onset)
        self.all_symbols = sorted(self.subevents + self.modifiers, key=lambda s: s.in_measure_fractional_onset)

    def _get_divisions(self) -> int:
        return self.score_part.divisions

    @property
    def fractional_duration(self) -> Fraction:
        end = max((s.in_measure_fractional_end_onset for s in self.subevents), default=Fraction(0))
        return end
    
    @property
    def in_measure_fractional_onset(self) -> Fraction:
        return Fraction(0)
    
    @property
    def global_fractional_onset(self) -> Fraction:
        return self.system_measure.fractional_onset

    @property
    def system_measure(self) -> "ScoreMeasure":
        from .score_measure import ScoreMeasure
        return ScoreMeasure.of(self, lambda sm: sm.part_measures)
    
    @property
    def is_new_system(self) -> bool:
        return self.system_measure.is_new_system

    @property
    def is_first(self) -> bool:
        return self.id == 1
    
    @property
    def all_durables(self) -> list[Durable]:
        return flatten(m.all_durables for m in self.subevents)
    
    @property
    def score_part(self) -> "ScorePart":
        from .score_part import ScorePart
        return ScorePart.of(self, lambda sp: sp.part_measures)

    @cached_property
    def has_full_repeat(self) -> bool:
        """
        Returns True, if there is `RepeatBar`
        measure's durables.
        """
        return any(isinstance(s, RepeatBar) for s in self.subevents)
    
    @cached_property
    def is_full_repeat(self) -> bool:
        """
        Returns True, if the measure is only
        a `RepeatBar`.
        """
        return len(self.all_durables) > 0 and all(isinstance(d, RepeatBar) for d in self.all_durables)
    
    def get_previous(self) -> Optional["PartMeasure"]:
        # only second+ measure has previous measure
        if self.id > 1:
            return self.score_part.get_part_measure_by_id(self.id - 1)
        return None
