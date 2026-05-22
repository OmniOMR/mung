from dataclasses import dataclass
from fractions import Fraction


@dataclass
class TimeSigStruct:
    """
    Holds information about a time signature
    as a numerator and denominator. Compared
    to the Python `Fraction`, it does not convert
    the fraction into a basic fraction.

    This is especially valuable when there
    is a need to distinguish between e.g.
    2/2 and 4/4 signatures.

    Can be used in computation as a fraction.
    """
    numerator: int
    denominator: int
    has_slash: bool = False
    is_single_number: bool = False
    is_common_cut: bool = False
    is_common: bool = False

    def as_fraction(self) -> Fraction:
        return Fraction(self.numerator, self.denominator)

    def __float__(self) -> float:
        return float(self.as_fraction())

    def __int__(self) -> int:
        return int(self.as_fraction())

    def __add__(self, other):
        return self.as_fraction() + Fraction(other)

    def __sub__(self, other):
        return self.as_fraction() - Fraction(other)

    def __mul__(self, other):
        return self.as_fraction() * Fraction(other)

    def __truediv__(self, other):
        return self.as_fraction() / Fraction(other)

    def __radd__(self, other):
        return Fraction(other) + self.as_fraction()

    def __rsub__(self, other):
        return Fraction(other) - self.as_fraction()

    def __rmul__(self, other):
        return Fraction(other) * self.as_fraction()

    def __rtruediv__(self, other):
        return Fraction(other) / self.as_fraction()

    def __eq__(self, other):
        return self.as_fraction() == Fraction(other)

    def __hash__(self):
        return hash(self.as_fraction())
