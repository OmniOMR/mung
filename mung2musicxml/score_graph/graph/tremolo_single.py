from dataclasses import dataclass

from .scene_object import SceneObject
from .subevent import Subevent
from .tokens import PlacementToken


@dataclass
class TremoloSingle(SceneObject):
    subevent: Subevent
    marks: int
    placement: PlacementToken
