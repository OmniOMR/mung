from dataclasses import dataclass
from abc import abstractmethod
from typing import TYPE_CHECKING, Optional
from fractions import Fraction

from .interface import DurationObject
if TYPE_CHECKING:
    from .staff import Staff
    from .durable import Durable
    from .beam import Beam
    from .voice import Voice
    from .tuplet import Tuplet
    from .score_part import ScorePart
    from .part_measure import PartMeasure
    from .wedge import Wedge
    from .dynamics import Dynamics
    from .tempo import Tempo
    from .dynamics_text import DynamicsText
    from .interpretation_text import InterpretationText
    from .segno import Segno
    from .coda import Coda
    from .rest_text import RestText
    from .ottava import Ottava
    from .grace_note import GraceChord


@dataclass
class Subevent(DurationObject):
    """
    Subevent is a collection of durables
    that start at the same onset and belong the same voice.
    These are chords, rests and repeats.
    """
    
    @property
    def grace_chords(self) -> list["GraceChord"]:
        from .grace_note import GraceChord
        return GraceChord.many_of(self, lambda s: s.parent)
    
    @property
    def in_measure_fractional_onset(self) -> Fraction:
        # avoid infinite recursion for descendants
        from .durable import Durable
        if isinstance(self, Durable):
            return self.fractional_onset_
        return min(d.in_measure_fractional_onset for d in self.all_durables)
    
    @property
    def in_measure_fractional_end_onset(self) -> Fraction:
        # avoid infinite recursion for descendants
        from .durable import Durable
        if isinstance(self, Durable):
            return self.fractional_onset_ + self.fractional_duration_
        return max(d.in_measure_fractional_end_onset for d in self.all_durables)
    
    @property
    def fractional_duration(self) -> Fraction:
        # avoid infinite recursion for descendants
        from .durable import Durable
        if isinstance(self, Durable):
            return self.fractional_duration_
        return max(d.fractional_duration for d in self.all_durables)
    
    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other
    
    @property
    def staffs(self) -> list["Staff"]:
        return list({d.staff for d in self.all_durables})
    
    @property
    @abstractmethod
    def all_durables(self) -> list["Durable"]:
        raise NotImplementedError

    @property
    def beams(self) -> list["Beam"]:
        from .beam import Beam
        return Beam.many_of(self, lambda b: b.all)
    
    @property
    def tuplet(self) -> Optional["Tuplet"]:
        from .tuplet import Tuplet
        return Tuplet.of_or_none(self, lambda t: t.all)

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
        return Wedge.many_of(self, lambda w: w.all)
    
    @property
    def dynamics(self) -> list["Dynamics"]:
        from .dynamics import Dynamics
        return Dynamics.many_of(self, lambda d: d.parent)
    
    @property
    def segnos(self) -> list["Segno"]:
        from .segno import Segno
        return Segno.many_of(self, lambda d: d.parent)
    
    @property
    def codas(self) -> list["Coda"]:
        from .coda import Coda
        return Coda.many_of(self, lambda d: d.parent)
    
    @property
    def tempos(self) -> list["Tempo"]:
        from .tempo import Tempo
        return Tempo.many_of(self, lambda d: d.all)
    
    @property
    def dynamics_texts(self) -> list["DynamicsText"]:
        from .dynamics_text import DynamicsText
        return DynamicsText.many_of(self, lambda d: d.all)

    @property
    def interpretation_texts(self) -> list["InterpretationText"]:
        from .interpretation_text import InterpretationText
        return InterpretationText.many_of(self, lambda d: d.all)

    @property
    def rest_texts(self) -> list["RestText"]:
        from .rest_text import RestText
        return RestText.many_of(self, lambda d: d.all)
    
    @property
    def ottavas(self) -> list["Ottava"]:
        from .ottava import Ottava
        return Ottava.many_of(self, lambda d: d.all)
