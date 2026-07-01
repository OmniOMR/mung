from dataclasses import dataclass

from .scene_object import SceneObject
from .subevent import Subevent
from .tokens import AboveBelowToken


@dataclass
class Ornament(SceneObject):
    parent: Subevent
    placement: AboveBelowToken


@dataclass
class Turn(Ornament):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/turn/

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/inverted-turn/
    """

    is_inverted: bool


@dataclass
class Trill(Ornament):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/trill-mark/

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/wavy-line/
    """

    has_wiggle: bool


@dataclass
class ShortTrill(Ornament):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/inverted-mordent/
    """

    pass
