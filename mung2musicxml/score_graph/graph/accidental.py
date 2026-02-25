from dataclasses import dataclass

from .scene_object import SceneObject
from .accidental_type import AccidentalType
from .note import Note
from .grace_note import GraceNote
from .key import Key

@dataclass
class Accidental(SceneObject):
    type_: AccidentalType
    parent: GraceNote | Note | Key
