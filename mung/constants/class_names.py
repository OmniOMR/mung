from fractions import Fraction
from typing import Optional


class ClassNamesConstants:
    """
    This class stores all the current names of MuNG classes.
    """
    STAFF_GROUPING = "staffGrouping"
    MEASURE_SEPARATOR = "measureSeparator"

    KEY_SIGNATURE = "keySignature"
    TIME_SIGNATURE = "timeSignature"

    STAFFLINE = "staffLine"
    STAFFSPACE = "staffSpace"
    STAFF = "staff"
    LEGER_LINE = "legerLine"
    STEM = "stem"

    TIE_CLASS_NAME = "tie"
    SLUR = "slur"

    G_CLEF = "gClef"
    C_CLEF = "cClef"
    F_CLEF = "fClef"

    NOTEHEAD_FULL = "noteheadFull"
    NOTEHEAD_HALF = "noteheadHalf"
    NOTEHEAD_WHOLE = "noteheadWhole"
    NOTEHEAD_FULL_SMALL = "noteheadFullSmall"
    NOTEHEAD_HALF_SMALL = "noteheadHalfSmall"

    REST_WHOLE = "restWhole"
    REST_HALF = "restHalf"
    REST_QUARTER = "restQuarter"
    REST_8TH = "rest8th"
    REST_16TH = "rest16th"
    REST_32ND = "rest32nd"
    REST_64TH = "rest64th"

    REST_BREVE = "restBreve"
    REST_LONGA = "restLonga"

    REPEAT_ONE_BAR = "repeatOneBar"
    MULTI_MEASURE_REST = "multiMeasureRest"
    AUGMENTATION_DOT = "augmentationDot"

    DYNAMIC_CRESHENDO = "dynamicCrescendoHairpin"
    DYNAMIC_DIMINUENDO = "dynamicDiminuendoHairpin"

    TUPLE = "tuple"

    FLAG_8TH_UP = "flag8thUp"
    FLAG_8TH_DOWN = "flag8thDown"
    FLAG_16TH_UP = "flag16thUp"
    FLAG_16TH_DOWN = "flag16thDown"
    FLAG_32ND_UP = "flag32ndUp"
    FLAG_32ND_DOWN = "flag32ndDown"
    FLAG_64TH_UP = "flag64thUp"
    FLAG_64TH_DOWN = "flag64thDown"

    BEAM = "beam"

    ACCIDENTAL_SHARP = "accidentalSharp"
    ACCIDENTAL_FLAT = "accidentalFlat"
    ACCIDENTAL_NATURAL = "accidentalNatural"
    ACCIDENTAL_DOUBLE_SHARP = "accidentalDoubleSharp"
    ACCIDENTAL_DOUBLE_FLAT = "accidentalDoubleFlat"

    TIME_SIG_COMMON = "timeSigCommon"
    TIME_SIG_CUT_COMMON = "timeSigCutCommon"

    LETTER_OTHER = "characterOther"

    TREMOLO_MARK = "tremoloMark"

    @staticmethod
    def rest_name_to_duration(rest_name: str) -> Fraction:
        """
        Returns the duration of a rest as a fraction based on a rest name.

        :param rest_name: The rest class name.
        :return: The duration of the rest as a Fraction.
        """
        C = ClassNamesConstants
        _LOOK_UP = {
            C.REST_LONGA: Fraction(16, 1),  # !!! We should find the Time Signature.
            C.REST_BREVE: Fraction(8, 1),  # !!! We should find the Time Signature.
            C.REST_WHOLE: Fraction(4, 1),  # !!! We should find the Time Signature.
            C.REST_HALF: Fraction(2, 1),
            C.REST_QUARTER: Fraction(1, 1),
            C.REST_8TH: Fraction(1, 2),
            C.REST_16TH: Fraction(1, 4),
            C.REST_32ND: Fraction(1, 8),
            C.REST_64TH: Fraction(1, 16),
            # Technically, these two should just apply time sig.,
            # but the measure-factorized precedence graph
            # means these durations never have sounding
            # descendants anyway:
            C.MULTI_MEASURE_REST: Fraction(4, 1),
            C.REPEAT_ONE_BAR: Fraction(4, 1),
        }
        duration = _LOOK_UP.get(rest_name, None)
        if duration is None:
            raise ValueError(f"Unknown rest name \"{rest_name}\"")
        return duration

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

    @staticmethod
    def interpret_numerals(numeral_list: list[str] | str) -> Optional[int]:
        if isinstance(numeral_list, str):
            numeral_list = [numeral_list]
        if len(numeral_list) == 0:
            return None
        
        C = ClassNamesConstants
        numeral_to_digit = {
            C.N0: 0,
            C.N1: 1,
            C.N2: 2,
            C.N3: 3,
            C.N4: 4,
            C.N5: 5,
            C.N6: 6,
            C.N7: 7,
            C.N8: 8,
            C.N9: 9,
        }
        result = 0
        for numeral in numeral_list:
            current_num = numeral_to_digit.get(numeral, None)
            if current_num is None:
                return None
            result = result * 10 + current_num
        return result

    @staticmethod
    def all_class_names() -> list[str]:
        """
        Returns all class names defined in this class.
        """
        return [value for key, value in vars(ClassNamesConstants).items()
                if isinstance(value, str) and not key.startswith("_")]
    