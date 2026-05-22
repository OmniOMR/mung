from dataclasses import dataclass

from .scene_object import SceneObject
from .subevent import Subevent
from .tokens import AboveBelowToken


@dataclass
class TremoloSingle(SceneObject):
    """
    Equivalent to MusicXML Tremolo on a single note.

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/tremolo/
    """
    subevent: Subevent
    marks: int
    placement: AboveBelowToken
