from dataclasses import dataclass
from typing import TYPE_CHECKING
from functools import cached_property

from .scene_object import SceneObject
from .pitch import Pitch
from .tokens import StemOrientationToken, NoteTypeValue
from .voice import Voice
if TYPE_CHECKING:
    from .note import Note
    from .staff import Staff
    from .beam import GraceNoteBeam

# TODO: add support for slash (yes/no)

@dataclass
class GraceNote(SceneObject):
    pitch: Pitch
    type_: NoteTypeValue
    at_durable_index: int
    stem_orientation: StemOrientationToken

    @cached_property
    def parent_note(self) -> "Note":
        from .note import Note
        return Note.of(self, lambda n: n.grace_notes)
    
    @property
    def voice(self) -> Voice:
        return self.parent_note.voice

    @property
    def staff(self) -> "Staff":
        return self.parent_note.staff
    
    @property
    def beams(self) -> list["GraceNoteBeam"]:
        from .beam import GraceNoteBeam
        return GraceNoteBeam.many_of(self, lambda gn: gn.all_grace_notes)
    
    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other
