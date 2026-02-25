from dataclasses import dataclass
from fractions import Fraction
from abc import abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..score_part import ScorePart

@dataclass
class IOnset:

    @property
    @abstractmethod
    def in_measure_fractional_onset(self) -> Fraction:
        raise NotImplementedError

    @property
    @abstractmethod
    def in_measure_fractional_end_onset(self) -> Fraction:
        raise NotImplementedError
