from dataclasses import dataclass

from .scene_object import SceneObject
from .durable import Durable


@dataclass
class Voice(SceneObject):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/voice/
    """
    id: int
    durables: list[Durable]
