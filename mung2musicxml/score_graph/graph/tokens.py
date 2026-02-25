from enum import StrEnum
from typing import Any
from fractions import Fraction
from mung.constants import ClassNameConstants as C


class PlacementToken(StrEnum):
    ABOVE = "above"
    BELOW = "below"

    @classmethod
    def default(cls) -> "PlacementToken":
        return cls.BELOW
    
    @classmethod
    def from_int(cls, value: int) -> "PlacementToken":
        if value > 0:
            return cls.ABOVE
        else:
            return cls.BELOW
    

class StemOrientationToken(StrEnum):
    UP = "up"
    DOWN = "down"
    NONE = "none"

    @classmethod
    def default(cls) -> "StemOrientationToken":
        return cls.UP
    
    @classmethod
    def from_int(cls, value: int) -> "StemOrientationToken":
        """
        `+1` means up, `-1` down.
        """
        if value == 1:
            return cls.UP
        elif value == -1:
            return cls.DOWN

        raise ValueError(f"Unknown orientation value '{value}'")


class BeamValueToken(StrEnum):
    BACKWARD_HOOK = "backward hook"
    BEGIN = "begin"
    CONTINUE = "continue"
    END = "end"
    FORWARD_HOOK = "forward hook"

    @classmethod
    def default_hook(cls) -> "BeamValueToken":
        return cls.FORWARD_HOOK


class AboveBelowToken(StrEnum):
    # This element appears above the reference element.
    ABOVE = "above"
    # This element appears below the reference element.
    BELOW = "below"
    NONE = "none"

    @classmethod
    def default(cls) -> "AboveBelowToken":
        return cls.NONE


class ShowTupleTokens(StrEnum):
    ACTUAL = "actual"
    BOTH = "both"
    NONE = "none"

    @classmethod
    def default(cls) -> "ShowTupleTokens":
        return cls.NONE
    

class YesNoToken(StrEnum):
    YES = "yes"
    NO = "no"

    @classmethod
    def from_bool(cls, value: bool) -> "YesNoToken":
        if value:
            return cls.YES
        elif not value:
            return cls.NO
        raise ValueError


class AutoOrderedStrEnum(StrEnum):
    @classmethod
    def _order_map(cls):
        return {name: i for i, name in enumerate(cls._member_names_)}

    def _rank(self):
        return self._order_map()[self.name]

    def __lt__(self, other: Any):
        if type(other) is type(self):
            return self._rank() < other._rank()
        return NotImplemented

    def __le__(self, other: Any):
        if type(other) is type(self):
            return self._rank() <= other._rank()
        return NotImplemented

    def __gt__(self, other: Any):
        if type(other) is type(self):
            return self._rank() > other._rank()
        return NotImplemented

    def __ge__(self, other: Any):
        if type(other) is type(self):
            return self._rank() >= other._rank()
        return NotImplemented


class StartStopContinueToken(AutoOrderedStrEnum):
    START = "start"
    CONTINUE = "continue"
    STOP = "stop"


class TiedTypeToken(AutoOrderedStrEnum):
    START = "start"
    CONTINUE = "continue"
    STOP = "stop"
    LET_RING = "let-ring"


class TimeSymbolToken(StrEnum):
    COMMON = "common"
    CUT = "cut"
    DOTTED_NOTE = "dotted-note"
    NORMAL = "normal"
    NOTE = "note"
    SINGLE_NUMBER = "single-number"


class TimeSeparatorToken(StrEnum):
    ADJACENT = "adjacent"
    DIAGONAL = "diagonal"
    HORIZONTAL = "horizontal"
    NONE = "none"
    VERTICAL = "vertical"


class GroupSymbolToken(StrEnum):
    """
    Group symbol value, bracket type at the start of group.

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/group-symbol-value/
    """
    BRACE = "brace"
    BRACKET = "bracket"
    LINE = "line"
    NONE = "none"
    SQUARE = "square"


class GroupBarlineToken(StrEnum):
    """
    Indicates if the group should have common barlines.

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/group-barline-value/
    """
    YES = "yes"
    NO = "no"
    MENSURSTRICH = "Mensurstrich"


class ArticulationType(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/articulations/
    """

    ACCENT = "accent"
    STACCATO = "staccato"
    TENUTO = "tenuto"
    STACCATISSIMO = "staccatissimo"
    # also known as Marcato
    STRONG_ACCENT = "strong-accent"
    

class TremoloType(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/tremolo-type/
    """
    START = "start"
    STOP = "stop"
    SINGLE = "single"
    UNMEASURED = "unmeasured"


class WedgeDirectionType(AutoOrderedStrEnum):
    """
    Corresponds to MusicXML wedge-type.

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/wedge/
    """
    CRESCENDO = "crescendo"
    DIMINUENDO = "diminuendo"
    CONTINUE = "continue"
    STOP = "stop"


class WedgeType(StrEnum):
    """
    Use to distinguish Crescendo and Diminuendo.

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/wedge/
    """
    CRESCENDO = WedgeDirectionType.CRESCENDO
    DIMINUENDO = WedgeDirectionType.DIMINUENDO

    @classmethod
    def fromm_mung_class_name(cls, value: str) -> "WedgeType":
        match value:
            case C.Dynamics.DYNAMIC_CRESCENDO_HAIRPIN:
                return cls.CRESCENDO
            case C.Dynamics.DYNAMIC_DIMINUENDO_HAIRPIN:
                return cls.DIMINUENDO
            case _:
                raise ValueError(f"Unknown {cls.__name__}: '{value}'")


class NoteTypeValue(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/note-type-value/
    """
    T1024 = "1024th"
    T512 = "512th"
    T256 = "256th"
    T128 = "128th"
    T64 = "64th"
    T32 = "32nd"
    T16 = "16th"
    EIGHT = "eighth"
    QUARTER = "quarter"
    HALF = "half"
    WHOLE = "whole"
    BREVE = "breve"
    LONG = "long"
    MAXIMA = "maxima"

    NONE = "none"

    __without_stem = {
        WHOLE,
        BREVE,
        LONG,
        MAXIMA
    }

    @classmethod
    def default(cls) -> "NoteTypeValue":
        return cls.QUARTER

    def has_stem(self) -> bool:
        """
        Returns true a note of this type has a stem.
        """
        return self not in self.__without_stem

    @classmethod
    def from_fraction(cls, value: Fraction) -> "NoteTypeValue":
        """
        Maps note duration to a string, assuming quarter = Fraction(1).
        """
        _LOOKUP = {
            Fraction(1, 256): cls.T1024,
            Fraction(1, 128): cls.T512,
            Fraction(1, 64): cls.T256,
            Fraction(1, 32): cls.T128,
            Fraction(1, 16): cls.T64,
            Fraction(1, 8): cls.T32,
            Fraction(1, 4): cls.T16,
            Fraction(1, 2): cls.EIGHT,
            Fraction(1, 1): cls.QUARTER,
            Fraction(2, 1): cls.HALF,
            Fraction(4, 1): cls.WHOLE,
            Fraction(8, 1): cls.BREVE,
            Fraction(16, 1): cls.LONG,
            Fraction(32, 1): cls.MAXIMA,
        }

        try:
            return _LOOKUP[value]
        except KeyError:
            raise ValueError(f"No note value corresponds to duration {value}")


class ClefSign(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/clef-sign/
    """
    G = "G"
    F = "F"
    C = "C"
    PERCUSSION = "percussion"
    TAB = "TAB"
    JIANPU = "jianpu"

    @classmethod
    def default(cls) -> "ClefSign":
        return cls.G

    