from dataclasses import dataclass
from typing import Optional

from .scene_object import SceneObject
from .tokens import DynamicsTypeToken, AboveBelowToken
from .subevent import Subevent

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .staff import Staff


@dataclass
class Dynamics(SceneObject):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/dynamics/
    """

    parent: Subevent
    type_: DynamicsTypeToken
    placement: AboveBelowToken
    text: Optional[str] = None

    def __post_init__(self) -> None:
        if self.type_ == DynamicsTypeToken.OTHER_DYNAMICS and self.text is None:
            raise ValueError(
                f"{Dynamics.__name__} of type {DynamicsTypeToken.OTHER_DYNAMICS} must have 'other string' specified"
            )
        if self.text is not None and self.type_ != DynamicsTypeToken.OTHER_DYNAMICS:
            raise ValueError(
                f"{Dynamics.__name__} of type {DynamicsTypeToken.OTHER_DYNAMICS} cannot specify 'other string'"
            )

    @property
    def staff(self) -> "Staff":
        return min(self.parent.staffs, key=lambda s: s.id)
