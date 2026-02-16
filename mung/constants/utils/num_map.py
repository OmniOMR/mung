from functools import cache
from typing import Self, Iterable

from .all_strenum import AllExtendedStrEnum
from .numerals import Numerals


class AllStrEnumNumeralMapped(AllExtendedStrEnum):
    """
    Abstract StrEnum that maps `<NAME><digit>` <-> `Numerals.N<digit>`
    Subclasses must define __digits__ = iterable[int]
    """
    __digits__: Iterable[int] = range(10)  # default 0–9

    @classmethod
    @cache
    def _digit_to_self(cls) -> dict[int, Self]:
        allowed = set(cls.__digits__)
        nums: dict[int, Self] = {}

        for member in cls:
            name = member.name
            if not name[-1].isdigit():
                continue

            digit = int(name[-1])
            if digit not in allowed:
                continue

            if digit in nums:
                raise ValueError(
                    f"Duplicate digit {digit} in {cls.__name__}"
                )
            nums[digit] = member

        missing = allowed - nums.keys()
        if missing:
            raise ValueError(
                f"{cls.__name__} missing digits: {sorted(missing)}"
            )

        return nums

    @classmethod
    @cache
    def _self_to_numerals(cls) -> dict[Self, Numerals]:
        return {v: Numerals.from_digit(k) for k, v in cls._digit_to_self().items()}

    @classmethod
    @cache
    def _numerals_to_self(cls) -> dict[Numerals, Self]:
        return {Numerals.from_digit(k): v for k, v in cls._digit_to_self().items()}

    def to_numeral(self) -> Numerals:
        return type(self)._self_to_numerals()[self]

    @classmethod
    def from_numeral(cls, numeral: Numerals) -> Self:
        return cls._numerals_to_self()[numeral]

    @classmethod
    def from_digit(cls, number: int) -> Self:
        return cls.from_numeral(Numerals.from_digit(number))
    
    def to_digit(self) -> int:
        return self.to_numeral().digit
    
    @classmethod
    def all_numeral_members(cls) -> set[Self]:
        """
        Get all available digit numbers.
        """
        return set(cls._digit_to_self().values())
