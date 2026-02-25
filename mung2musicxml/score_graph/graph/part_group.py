from dataclasses import dataclass, field

from .scene_object import SceneObject
from .score_part import ScorePart
from .tokens import GroupBarlineToken, GroupSymbolToken


@dataclass
class PartGroup(SceneObject):
    parts: list[ScorePart]
    bracket_type: GroupSymbolToken
    barline_type: GroupBarlineToken = field(default=GroupBarlineToken.YES)

    def __post_init__(self) -> None:
        self.parts.sort(key=lambda p: p.id)

    def is_start(self, part: ScorePart) -> bool:
        return self.parts[0].id == part.id
    
    def is_stop(self, part: ScorePart) -> bool:
        return self.parts[-1].id == part.id
    
    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other
    