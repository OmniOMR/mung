from dataclasses import dataclass

from .scene_object import SceneObject
from .durable import Durable
from .grace_note import GraceNote


@dataclass
class Dot(SceneObject):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/dot/
    """
    durable: Durable | GraceNote
