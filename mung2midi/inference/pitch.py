"""
This module implements Pitch.

It is more or less a copy of Jiri Mayer's work.
URL: https://github.com/OMR-Research/Smashcima/blob/main/smashcima/scene/semantic/Pitch.py
"""

from enum import StrEnum, IntEnum
from typing import Self
import re
from dataclasses import dataclass, field


class Octave(IntEnum):
    """
    Octave number of the scientific pitch notation¨
    
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/octave/
    """
    o0 = 0
    o1 = 1
    o2 = 2
    o3 = 3
    o4 = 4
    o5 = 5
    o6 = 6
    o7 = 7
    o8 = 8
    o9 = 9


class Step(StrEnum):
    """
    Step name of the scientific pitch notation
    
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/step/
    """
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    A = "A"
    B = "B"


_STEP_MIDI_OFFSETS = {
    Step.C: 0,
    Step.D: 2,
    Step.E: 4,
    Step.F: 5,
    Step.G: 7,
    Step.A: 9,
    Step.B: 11,
}


class Alter(IntEnum):
    """
    Semitone alter number (based on MusicXML)

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/semitones/
    """
    double_flat = -2
    flat = -1
    none = 0
    sharp = 1
    double_sharp = 2

    @property
    def accidental_code(self) -> str:
        match self:
            case Alter.double_flat:
                return "bb"
            case Alter.flat:
                return "b"
            case Alter.none:
                return ""
            case Alter.sharp:
                return "#"
            case Alter.double_sharp:
                return "x"
            case _:
                raise NotImplementedError()

    @classmethod
    def from_str(cls, text: str) -> Self:
        text = text.lower()
        match text:
            case "bb":
                return cls(-2)
            case "b":
                return cls(-1)
            case "":
                return cls(0)
            case "#":
                return cls(1)
            case "x":
                return cls(2)
            case _:
                raise ValueError()


@dataclass(frozen=True, eq=True)
class Pitch:
    """
    Represents an audible pitch in the scientific pitch notation.
    
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/pitch/
    """
    octave: Octave
    step: Step
    alter: Alter = field(default=Alter.none)

    def __str__(self) -> str:
        return f"{self.step}{self.alter.accidental_code}{self.octave.value}"

    def to_tuple_repr(self) -> tuple[str, int]:
        return f"{self.step}{self.alter.accidental_code}", self.octave.value

    @staticmethod
    def _split_before_digit(text: str) -> tuple[str, str]:
        match = re.match(r"([^\d]*)(\d.*)", text)
        if match:
            return match.groups()[0], match.groups()[1]

        raise ValueError(f"Invalid input text: {text}")

    @classmethod
    def from_string(cls, text: str) -> Self:
        step = Step(text[0].upper())
        alter_text, octave_text = cls._split_before_digit(text[1:])
        alter = Alter.from_str(alter_text)
        try:
            o = int(octave_text)
        except ValueError as _:
            raise ValueError(f"Invalid octave, not an integer: {octave_text}")
        octave = Octave(o)

        return cls(octave, step, alter)

    @classmethod
    def from_list_of_strings(cls, lst: list[str]) -> list[Self]:
        return [cls.from_string(x) for x in lst]

    def to_midi(self) -> int:
        """
        Convert Pitch to its corresponding MIDI note number (0-127).
        """
        base = _STEP_MIDI_OFFSETS[self.step]
        midi_num = 12 * (self.octave.value + 1) + base + int(self.alter)

        if not (0 <= midi_num <= 127):
            raise ValueError(f"MIDI note out of range (0-127): {midi_num} for {self}")

        return midi_num
    
    def __lt__(self, other: Self) -> bool:
        if not isinstance(other, Pitch):
            return NotImplemented
        return self.to_midi() < other.to_midi()


class OttavaConstants(StrEnum):
    """
    Keys for storing computed information about ottavas.
    """
    
    DIRECTION = "direction"
    SIZE = "size"


OTTAVA_SIZE_DEFAULT = 8
OTTAVA_SIZE_TO_OCTAVE_MAPPING: dict[int, int] = {8: 1, 13: 2, 22: 3}
