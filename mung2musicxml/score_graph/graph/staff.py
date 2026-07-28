from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .scene_object import SceneObject
from .durable import Durable
from .clef import Clef
from .wedge import Wedge
if TYPE_CHECKING:
    from .score_part import ScorePart


@dataclass
class Staff(SceneObject):
    """
    Container with all durables that belong to a staff.

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/staff/
    """
    durables: list[Durable]
    id: int
    other_symbols: list[Clef | Wedge] = field(default_factory=list)
    grace_notes: list = field(default_factory=list)

    def __post_init__(self) -> None:
        assert self.id in [1, 2]
    
    @property
    def score_part(self) -> "ScorePart":
        from .score_part import ScorePart
        return ScorePart.of(self, lambda p: p.staffs)

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other
