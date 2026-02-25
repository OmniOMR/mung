from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from .durable import Durable
from .pitch import Pitch
from .grace_note import GraceNote
from .tokens import StemOrientationToken
if TYPE_CHECKING:
    from .staff import Staff
    from .chord import Chord
    from .accidental import Accidental


@dataclass
class Note(Durable):
    pitch: Pitch
    stem_orientation: StemOrientationToken
    grace_notes: list[GraceNote] = field(default_factory=list)

    @property
    def staff(self) -> "Staff":
        from .staff import Staff
        return Staff.of(self, lambda s: s.durables)
    
    @property
    def chord(self) -> "Chord":
        from .chord import Chord
        return Chord.of(self, lambda c: c.notes)
    
    @property
    def chord_stem_orientation(self) -> StemOrientationToken:
        return self.chord.stem_orientation
    
    @property
    def accidental(self) -> Optional["Accidental"]:
        from .accidental import Accidental
        return Accidental.of_or_none(self, lambda a: a.parent)
    
    @property
    def is_first_in_chord(self) -> bool:
        """
        Returns true, if this note is first in its chord
        """
        return self == self.chord.first_note
    
    @property
    def is_chord_continuation(self) -> bool:
        """
        Returns true, if this note is a continuation of a chord -
        it is not first in the chord and has to contain the `chord` element.
        """
        return not self.is_first_in_chord

    @property
    def has_stem(self) -> bool:
        """
        Returns true, if the note type has stem.
        """
        return self.type_.has_stem()
    
    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other