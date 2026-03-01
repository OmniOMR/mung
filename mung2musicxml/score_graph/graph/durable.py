from dataclasses import dataclass
from fractions import Fraction
from typing import TYPE_CHECKING, Optional

from .tokens import NoteTypeValue
from .interface import DurationObject

if TYPE_CHECKING:
    from .voice import Voice
    from .dot import Dot
    from .staff import Staff
    from .score_part import ScorePart
    from .beam import DurableBeam
    from .subevent import Subevent
    from .tuplet import Tuplet
    from .slur import Slur
    from .tie import Tie
    from .wedge import Wedge
    from .articulation import Articulation
    from .tremolo_beam import TremoloBeam
    from .tremolo_single import TremoloSingle
    from .part_measure import PartMeasure


@dataclass
class Durable(DurationObject):
    """
    Durable is a single symbol on a staff
    that has duration, onset and a type.
    """
    type_: NoteTypeValue
    fractional_duration_: Fraction
    fractional_onset_: Fraction

    @property
    def in_measure_fractional_onset(self) -> Fraction:
        return self.fractional_onset_
    
    @property
    def fractional_duration(self) -> Fraction:
        return self.fractional_duration_

    @property
    def part_measure(self) -> "PartMeasure":
        from .part_measure import PartMeasure
        return PartMeasure.of(self.subevent, lambda m: m.subevents)
    
    @property
    def voice(self) -> "Voice":
        from .voice import Voice
        return Voice.of(self, lambda v: v.durables)
    
    @property
    def staff(self) -> "Staff":
        from .staff import Staff
        return Staff.of(self, lambda s: s.durables)
    
    @property
    def score_part(self) -> "ScorePart":
        from .score_part import ScorePart
        return ScorePart.of(self.staff, lambda sp: sp.staffs)

    @property
    def dots(self) -> list["Dot"]:
        from .dot import Dot
        return Dot.many_of(self, lambda d: d.durable)
    
    @property
    def subevent(self) -> "Subevent":
        from .note import Note
        from .chord import Chord
        from .rest import Rest
        from .repeat import RepeatBar
        if isinstance(self, Note):
            return Chord.of(self, lambda c: c.notes)
        elif isinstance(self, Rest):
            return self
        elif isinstance(self, RepeatBar):
            return self
        raise NotImplementedError
    
    @property
    def beams(self) -> list["DurableBeam"]:
        from .beam import DurableBeam
        subevent = self.subevent
        return DurableBeam.many_of(subevent, lambda b: b.all)

    @property
    def tuplet(self) -> Optional["Tuplet"]:
        from .tuplet import Tuplet
        subevent = self.subevent
        return Tuplet.of_or_none(subevent, lambda t: t.all)

    @property
    def slurs(self) -> list["Slur"]:
        from .slur import Slur
        return Slur.many_of(self.subevent, lambda t: t.all)

    @property
    def ties(self) -> list["Tie"]:
        from .tie import Tie
        return Tie.many_of(self, lambda t: t.all)
    
    @property
    def wedges(self) -> list["Wedge"]:
        from .wedge import Wedge
        return Wedge.many_of(self, lambda w: w.all)
    
    @property
    def articulations(self) -> list["Articulation"]:
        from .articulation import Articulation
        return Articulation.many_of(self, lambda a: a.parent)
    
    @property
    def tremolo_beam(self) -> Optional["TremoloBeam"]:
        from .tremolo_beam import TremoloBeam
        return TremoloBeam.of_or_none(self.subevent, lambda t: t.all_subevents)
    
    @property
    def tremolo_single(self) -> Optional["TremoloSingle"]:
        from .tremolo_single import TremoloSingle
        return TremoloSingle.of_or_none(self.subevent, lambda t: t.subevent)
    