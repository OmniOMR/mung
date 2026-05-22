from dataclasses import dataclass

from .scene_object import SceneObject
from .subevent import Subevent
from .tokens import FermataOrientationToken


@dataclass
class Fermata(SceneObject):
    parent: Subevent
    type_: FermataOrientationToken
    