from dataclasses import dataclass

from .scene_object import SceneObject
from .tokens import AccidentalValue
from .note import Note
from .grace_note import GraceNote
from .key import Key


@dataclass
class Accidental(SceneObject):
    """
    Notehead accidental.

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/accidental/
    """
    type_: AccidentalValue
    parent: GraceNote | Note | Key
