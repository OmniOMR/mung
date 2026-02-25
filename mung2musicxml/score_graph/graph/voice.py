from dataclasses import dataclass

from .scene_object import SceneObject
from .durable import Durable


@dataclass
class Voice(SceneObject):
    id_: int
    durables: list[Durable]
