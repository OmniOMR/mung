from dataclasses import dataclass
from typing import Optional

from .scene_object import SceneObject
from .tokens import DynamicsTypeToken
from .subevent import Subevent


@dataclass
class Dynamics(SceneObject):
    parent: Subevent
    type_: DynamicsTypeToken
    other: Optional[str] = None

    def __post_init__(self) -> None:
        if self.type_ == DynamicsTypeToken.OTHER_DYNAMICS and self.other is None:
            raise ValueError(
                f"{Dynamics.__name__} of type {DynamicsTypeToken.OTHER_DYNAMICS} must have 'other string' specified"
            )
        if self.other is not None and self.type_ != DynamicsTypeToken.OTHER_DYNAMICS:
            raise ValueError(
                f"{Dynamics.__name__} of type {DynamicsTypeToken.OTHER_DYNAMICS} cannot specify 'other string'"
            )
