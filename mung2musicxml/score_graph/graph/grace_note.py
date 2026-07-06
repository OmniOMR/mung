from dataclasses import dataclass
from typing import TYPE_CHECKING
from fractions import Fraction

from .chord import Chord
from .note import Note
from .subevent import Subevent
from .tokens import YesNoToken
from .slur import Slur

if TYPE_CHECKING:
    from .voice import Voice
    from .staff import Staff


@dataclass(kw_only=True)
class GraceNote(Note):
    fractional_duration_: Fraction = Fraction(0)
    slash: YesNoToken

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

    @property
    def grace_slurs(self) -> list["GraceSlur"]:
        return GraceSlur.many_of(self.subevent, lambda gs: gs.start)


@dataclass(kw_only=True)
class GraceChord(Chord):
    notes: list[GraceNote]  # type: ignore
    parent: Subevent

    @property
    def global_fractional_onset(self) -> Fraction:
        return self.notes[0].global_fractional_onset

    @property
    def slash(self) -> YesNoToken:
        return YesNoToken.from_bool(any(note.slash for note in self.notes))

    @property
    def voice(self) -> "Voice":
        return self.parent.voice

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other


@dataclass
class GraceSlur(Slur):
    """
    Equivalent to regular slur
    but between grace notes and regular notes.
    Has less strict validation rules during initialization.
    """

    start: GraceChord  # type: ignore
    stop: Subevent  # type: ignore

    def __post_init__(self):
        self._check_start_is_set()
        self._check_stop_is_set()

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other
