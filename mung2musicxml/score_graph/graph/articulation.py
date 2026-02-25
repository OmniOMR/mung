from dataclasses import dataclass

from .scene_object import SceneObject
from .durable import Durable
from .tokens import ArticulationType, PlacementToken


@dataclass
class Articulation(SceneObject):
    parent: Durable
    type_: ArticulationType
    placement: PlacementToken
