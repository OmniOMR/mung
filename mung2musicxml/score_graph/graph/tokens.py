from enum import StrEnum
from fractions import Fraction
from mung.constants import ClassNameConstants as C

from .utils import AutoOrderedStrEnum


class AboveBelowToken(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/above-below/
    """
    ABOVE = "above"
    BELOW = "below"

    @classmethod
    def default(cls) -> "AboveBelowToken":
        return cls.BELOW
    
    @classmethod
    def from_int(cls, value: int) -> "AboveBelowToken":
        if value > 0:
            return cls.ABOVE
        else:
            return cls.BELOW
    

class StemValueToken(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/stem-value/
    """
    UP = "up"
    DOWN = "down"
    NONE = "none"

    @classmethod
    def default(cls) -> "StemValueToken":
        return cls.UP
    
    @classmethod
    def from_int(cls, value: int) -> "StemValueToken":
        """
        `+1` means up, `-1` down.
        """
        if value == 1:
            return cls.UP
        elif value == -1:
            return cls.DOWN

        raise ValueError(f"Unknown orientation value '{value}'")


class BeamValueToken(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/beam/
    """
    BACKWARD_HOOK = "backward hook"
    BEGIN = "begin"
    CONTINUE = "continue"
    END = "end"
    FORWARD_HOOK = "forward hook"

    @classmethod
    def default_hook(cls) -> "BeamValueToken":
        return cls.FORWARD_HOOK


class ShowTupleToken(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/show-tuplet/
    """
    ACTUAL = "actual"
    BOTH = "both"
    NONE = "none"

    @classmethod
    def default(cls) -> "ShowTupleToken":
        return cls.NONE
    

class YesNoToken(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/yes-no/
    """
    YES = "yes"
    NO = "no"

    @classmethod
    def from_bool(cls, value: bool) -> "YesNoToken":
        if value:
            return cls.YES
        elif not value:
            return cls.NO
        raise ValueError


class StartStopContinueToken(AutoOrderedStrEnum):
    """
    `start-stop-continue` tokens, also used for `start-stop`.

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/start-stop-continue/

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/start-stop/
    """
    START = "start"
    CONTINUE = "continue"
    STOP = "stop"


class TiedTypeToken(AutoOrderedStrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/tied-type/
    """
    START = "start"
    CONTINUE = "continue"
    STOP = "stop"
    LET_RING = "let-ring"


class TimeSymbolToken(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/time-symbol/
    """
    COMMON = "common"
    CUT = "cut"
    DOTTED_NOTE = "dotted-note"
    NORMAL = "normal"
    NOTE = "note"
    SINGLE_NUMBER = "single-number"


class TimeSeparatorToken(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/time-separator/
    """
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

    __measure_lasting = {
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

    def can_be_measure_lasting(self) -> bool:
        """
        Returns true if a rest of this type can be measure lasting.
        """
        return self in self.__measure_lasting

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


class AccidentalValue(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/accidental-value/
    """
    ARROW_DOWN = "arrow-down"
    ARROW_UP = "arrow-up"
    DOUBLE_SHARP = "double-sharp"
    DOUBLE_SHARP_DOWN = "double-sharp-down"
    DOUBLE_SHARP_UP = "double-sharp-up"
    DOUBLE_SLASH_FLAT = "double-slash-flat"
    FLAT = "flat"
    FLAT_1 = "flat-1"
    FLAT_2 = "flat-2"
    FLAT_3 = "flat-3"
    FLAT_4 = "flat-4"
    FLAT_DOWN = "flat-down"
    FLAT_FLAT = "flat-flat"
    FLAT_FLAT_DOWN = "flat-flat-down"
    FLAT_FLAT_UP = "flat-flat-up"
    FLAT_UP = "flat-up"
    KORON = "koron"
    NATURAL = "natural"
    NATURAL_DOWN = "natural-down"
    NATURAL_FLAT = "natural-flat"
    NATURAL_SHARP = "natural-sharp"
    NATURAL_UP = "natural-up"
    OTHER = "other"
    QUARTER_FLAT = "quarter-flat"
    QUARTER_SHARP = "quarter-sharp"
    SHARP = "sharp"
    SHARP_1 = "sharp-1"
    SHARP_2 = "sharp-2"
    SHARP_3 = "sharp-3"
    SHARP_5 = "sharp-5"
    SHARP_DOWN = "sharp-down"
    SHARP_SHARP = "sharp-sharp"
    SHARP_UP = "sharp-up"
    SLASH_FLAT = "slash-flat"
    SLASH_QUARTER_SHARP = "slash-quarter-sharp"
    SLASH_SHARP = "slash-sharp"
    SORI = "sori"
    THREE_QUARTERS_FLAT = "three-quarters-flat"
    THREE_QUARTERS_SHARP = "three-quarters-sharp"
    TRIPLE_FLAT = "triple-flat"
    TRIPLE_SHARP = "triple-sharp"


class DynamicsTypeToken(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/dynamics/
    """
    P = "p"
    PP = "pp"
    PPP = "ppp"
    PPPP = "pppp"
    PPPPP = "ppppp"
    PPPPPP = "pppppp"
    F = "f"
    FF = "ff"
    FFF = "fff"
    FFFF = "ffff"
    FFFFF = "fffff"
    FFFFFF = "ffffff"
    MP = "mp"
    MF = "mf"
    SF = "sf"
    SFP = "sfp"
    SFPP = "sfpp"
    FP = "fp"
    RF = "rf"
    RFZ = "rfz"
    SFZ = "sfz"
    SFFZ = "sffz"
    FZ = "fz"
    N = "n"
    PF = "pf"
    SFZP = "sfzp"

    OTHER_DYNAMICS = "other-dynamics"


class FermataOrientationToken(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/upright-inverted/
    """
    UPRIGHT = "upright" 
    INVERTED = "inverted" 


class SyllabicTypeToken(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/syllabic/
    """
    BEGIN = "begin"
    END = "end"
    MIDDLE = "middle"
    SINGLE = "single"


class FontStyleToken(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/font-style/
    """
    NORMAL = "normal"
    ITALIC = "italic"


class FontWeightToken(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/font-weight/
    """
    NORMAL = "normal"
    BOLD = "bold"


class BarStyleToken(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/bar-style/
    """
    DASHED = "dashed"
    DOTTED = "dotted"
    HEAVY = "heavy"
    HEAVY_HEAVY= "heavy-heavy"
    HEAVY_LIGHT= "heavy-light"
    LIGHT_HEAVY= "light-heavy"
    LIGHT_LIGHT= "light-light"
    NONE = "none"
    REGULAR = "regular"
    SHORT = "short"
    TICK = "tick"

    @classmethod
    def default(cls) -> "BarStyleToken":
        return cls.REGULAR
    

class BackwardForwardToken(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/backward-forward/
    """
    BACKWARD = "backward"
    FORWARD = "forward"


class WingedToken(StrEnum):
    NONE = "none"
    STRAIGHT = "straight"
    CURVED = "curved"
    DOUBLE_STRAIGHT = "double-straight"
    DOUBLE_CURVED = "double-curved"


class LeftRightMiddleToken(AutoOrderedStrEnum):
    RIGHT = "right"
    LEFT = "left"
    MIDDLE = "middle"


class StartStopDiscontinueToken(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/start-stop-discontinue/
    """
    START = "start"
    STOP = "stop"
    DISCONTINUE = "discontinue"


class DirectionToken(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/up-down/
    """
    UP = "up"
    DOWN = "down"


class OctaveShiftType(StrEnum):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/up-down-stop-continue/
    """
    
    UP = "up"
    DOWN = "down"
    STOP = "stop"
    CONTINUE = "continue"
    