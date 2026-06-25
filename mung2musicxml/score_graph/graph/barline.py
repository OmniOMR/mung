from dataclasses import dataclass, field
from fractions import Fraction
from typing import TYPE_CHECKING, Optional

from .scene_object import SceneObject
from .tokens import BarStyleToken, LeftRightMiddleToken
from .interface import InMeasureObject

if TYPE_CHECKING:
    from .score_part import ScorePart
    from .part_measure import PartMeasure


@dataclass
class Barline(SceneObject):
    style: BarStyleToken
    location: LeftRightMiddleToken
    fractional_onset_: Optional[Fraction] = None

    def __post_init__(self) -> None:
        if self.location == LeftRightMiddleToken.MIDDLE:
            print(self)
            assert self.fractional_onset_ is not None
    
    @property
    def in_measure_fractional_onset(self) -> Optional[Fraction]:
        return self.fractional_onset_
