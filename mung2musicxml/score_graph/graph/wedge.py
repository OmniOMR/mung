from dataclasses import dataclass

from .tuplet import GenericStartStop
from .tokens import PlacementToken, WedgeType


@dataclass(kw_only=True)
class Wedge(GenericStartStop):
    type_: WedgeType
    placement: PlacementToken
    staff_id: int
    
    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other
    