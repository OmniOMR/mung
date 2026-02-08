
from . import AllExtendedStrEnum
from typing import Optional


class Numerals(AllExtendedStrEnum):
    N0 = "numeral0"
    N1 = "numeral1"
    N2 = "numeral2"
    N3 = "numeral3"
    N4 = "numeral4"
    N5 = "numeral5"
    N6 = "numeral6"
    N7 = "numeral7"
    N8 = "numeral8"
    N9 = "numeral9"

    @classmethod
    def from_digit(cls, digit: int) -> "Numerals":
        if not (0 <= digit <= 9):
            raise ValueError(digit)
        return cls[f"N{digit}"]

    @property
    def digit(self) -> int:
        return int(self.name[1])

    @classmethod
    def interpret_numerals(cls, numeral_list: list[str] | str) -> Optional[int]:
        if isinstance(numeral_list, str):
            numeral_list = [numeral_list]
        if len(numeral_list) == 0:
            return None

        result = 0
        for numeral in numeral_list:
            current_num = cls(numeral).digit
            if current_num is None:
                return None
            result = result * 10 + current_num
        return result
