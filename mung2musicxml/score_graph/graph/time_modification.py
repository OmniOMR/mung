from fractions import Fraction
from dataclasses import dataclass

from .scene_object import SceneObject


@dataclass(eq=True)
class TimeModification(SceneObject):
    actual: int
    normal: int

    def __post_init__(self) -> None:
        assert isinstance(self.actual, int) and self.actual > 0
        assert isinstance(self.normal, int) and self.normal > 0

    @classmethod
    def from_tuple_time_modifier(cls, modifier: Fraction):
        return cls(modifier.denominator, modifier.numerator)

    def to_tuple_time_modifier(self) -> Fraction:
        return Fraction(self.normal, self.actual)
