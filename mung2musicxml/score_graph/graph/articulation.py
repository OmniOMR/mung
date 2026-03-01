from dataclasses import dataclass

from .scene_object import SceneObject
from .durable import Durable
from .tokens import ArticulationType, AboveBelowToken


@dataclass
class Articulation(SceneObject):
    """
    Articulation is a single articulation symbol
    above/below a notehead.

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/articulations/
    """
    parent: Durable
    type_: ArticulationType
    placement: AboveBelowToken
