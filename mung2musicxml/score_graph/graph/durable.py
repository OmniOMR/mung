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
    from .beam import Beam
    from .subevent import Subevent
    from .tuplet import Tuplet
    from .slur import Slur
    from .tie import Tie
    from .wedge import Wedge
    from .articulation import Articulation
    from .tremolo_beam import TremoloBeam
    from .tremolo_single import TremoloSingle
    from .part_measure import PartMeasure
    from .fermata import Fermata
    from .lyric import Lyric
    from .ornaments import Turn, Trill, ShortTrill, Arpeggiato
    from .grace_note import GraceSlur


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
    def beams(self) -> list["Beam"]:
        from .beam import Beam
        return Beam.many_of(self.subevent, lambda b: b.all)

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
    def grace_slurs(self) -> list["GraceSlur"]:
        from .grace_note import GraceSlur
        return GraceSlur.many_of(self.subevent, lambda gs: gs.stop)

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
        return Articulation.many_of(self.subevent, lambda a: a.parent)
    
    @property
    def tremolo_beam(self) -> Optional["TremoloBeam"]:
        from .tremolo_beam import TremoloBeam
        return TremoloBeam.of_or_none(self.subevent, lambda t: t.all)
    
    @property
    def tremolo_single(self) -> Optional["TremoloSingle"]:
        from .tremolo_single import TremoloSingle
        return TremoloSingle.of_or_none(self.subevent, lambda t: t.parent)
    
    @property
    def turn(self) -> Optional["Turn"]:
        from .ornaments import Turn
        return Turn.of_or_none(self.subevent, lambda t: t.parent)
    
    @property
    def trill(self) -> Optional["Trill"]:
        from .ornaments import Trill
        return Trill.of_or_none(self.subevent, lambda t: t.parent)
    
    @property
    def short_trill(self) -> Optional["ShortTrill"]:
        from .ornaments import ShortTrill
        return ShortTrill.of_or_none(self.subevent, lambda t: t.parent)
    
    @property
    def arpeggiato(self) -> Optional["Arpeggiato"]:
        from .ornaments import Arpeggiato
        return Arpeggiato.of_or_none(self.subevent, lambda t: t.parent)
    
    @property
    def fermatas(self) -> list["Fermata"]:
        from .fermata import Fermata
        return Fermata.many_of(self.subevent, lambda t: t.parent)
    
    @property
    def lyrics(self) -> list["Lyric"]:
        from .lyric import Lyric
        return Lyric.many_of(self.subevent, lambda t: t.all)
    