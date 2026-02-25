from dataclasses import dataclass
from abc import abstractmethod
from typing import TYPE_CHECKING, Optional
from fractions import Fraction

from .interface import IDuration, IOnset
from .scene_object import SceneObject
if TYPE_CHECKING:
    from .staff import Staff
    from .durable import Durable
    from .beam import DurableBeam
    from .voice import Voice
    from .tuplet import Tuplet
    from .score_part import ScorePart
    from .part_measure import PartMeasure
    from .wedge import Wedge


@dataclass
class Subevent(IDuration, IOnset, SceneObject):
    @property
    def in_measure_fractional_onset(self) -> Fraction:
        return min(d.in_measure_fractional_onset for d in self.all_durables)
    
    @property
    def in_measure_onset(self) -> int:
        onset =  self.in_measure_fractional_onset * self._get_divisions()
        assert onset.denominator == 1
        return onset.numerator

    @property
    def in_measure_fractional_end_onset(self) -> Fraction:
        return max(d.in_measure_fractional_end_onset for d in self.all_durables)
    
    @property
    def global_fractional_onset(self) -> Fraction:
        return self.part_measure.global_fractional_onset + self.in_measure_fractional_onset
    
    @property
    def fractional_duration(self) -> Fraction:
        return max(d.fractional_duration for d in self.all_durables)
    
    @property
    def duration(self) -> int:
        duration = self.fractional_duration * self._get_divisions()
        assert duration.denominator == 1
        return duration.numerator
    
    def _get_divisions(self) -> int:
        return self.score_part.divisions
    
    @property
    def staffs(self) -> list["Staff"]:
        return list({d.staff for d in self.all_durables})
    
    @property
    @abstractmethod
    def all_durables(self) -> list["Durable"]:
        raise NotImplementedError

    @property
    def beams(self) -> list["DurableBeam"]:
        from .beam import DurableBeam
        return DurableBeam.many_of(self, lambda b: b.all_subevents)
    
    @property
    def tuplet(self) -> Optional["Tuplet"]:
        from .tuplet import Tuplet
        return Tuplet.of_or_none(self, lambda t: t.all_subevents)

    @property
    def voice(self) -> "Voice":
        return self.all_durables[0].voice
    
    @property
    def part_measure(self) -> "PartMeasure":
        from .part_measure import PartMeasure
        return PartMeasure.of(self, lambda pm: pm.subevents)
    
    @property
    def score_part(self) -> "ScorePart":
        from .score_part import ScorePart
        pm = self.part_measure
        return ScorePart.of(pm, lambda sp: sp.part_measures)

    @property
    def wedges(self) -> list["Wedge"]:
        from .wedge import Wedge
        return Wedge.many_of(self, lambda w: w.all_subevents)
