from dataclasses import dataclass
from typing import TYPE_CHECKING
from fractions import Fraction

from .chord import Chord
from .note import Note
from .subevent import Subevent

if TYPE_CHECKING:
    from .voice import Voice
    from .staff import Staff


@dataclass(kw_only=True)
class GraceNote(Note):
    fractional_duration_: Fraction = Fraction(0)
    pass

    @property
    def global_fractional_onset(self) -> Fraction:
        return self.in_measure_fractional_onset

    @property
    def subevent(self) -> "GraceChord":
        return GraceChord.of(self, lambda gc: gc.notes)

    @property
    def voice(self) -> "Voice":
        return self.subevent.voice

    @property
    def staff(self) -> "Staff":
        from .staff import Staff

        return Staff.of(self, lambda s: s.grace_notes)


@dataclass(kw_only=True)
class GraceChord(Chord):
    notes: list[GraceNote]  # type: ignore
    parent: Subevent

    @property
    def global_fractional_onset(self) -> Fraction:
        return self.notes[0].global_fractional_onset

    @property
    def voice(self) -> "Voice":
        return self.parent.voice

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other
