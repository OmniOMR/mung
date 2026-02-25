from dataclasses import dataclass
from fractions import Fraction
from abc import abstractmethod


@dataclass
class IDuration:
    @property
    @abstractmethod
    def fractional_duration(self) -> Fraction:
        raise NotImplementedError
