from dataclasses import dataclass

from .tokens import AboveBelowToken
from .scene_object import SceneObject
from .subevent import Subevent


@dataclass
class Segno(SceneObject):
    parent: Subevent
    placement: AboveBelowToken
