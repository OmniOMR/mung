from dataclasses import dataclass
from typing import TYPE_CHECKING

from .tuplet import GenericStartStopContinue
from .tokens import AboveBelowToken, WedgeType
from .subevent import Subevent

if TYPE_CHECKING:
    from .staff import Staff


@dataclass(kw_only=True)
class Wedge(GenericStartStopContinue[Subevent]):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/wedge/
    """
    type_: WedgeType
    placement: AboveBelowToken
    
    @property
    def staff(self) -> "Staff":
        from .staff import Staff
        return Staff.of(self, lambda s: s.other_symbols)
    
    @property
    def staff_id(self) -> int:
        return self.staff.id

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other
    