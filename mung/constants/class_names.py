from enum import Enum
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
    SLUR_CLASS_NAME = "slur"

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

    @staticmethod
    def rest_name_to_duration(rest_name: str) -> Fraction:
        """
        Returns the duration of a rest as a fraction based on a rest name.

        :param rest_name: The rest class name.
        :return: The duration of the rest as a Fraction.
        """
        _LOOK_UP = {
            ClassNamesConstants.REST_LONGA: Fraction(16, 1),  # !!! We should find the Time Signature.
            ClassNamesConstants.REST_BREVE: Fraction(8, 1),  # !!! We should find the Time Signature.
            ClassNamesConstants.REST_WHOLE: Fraction(4, 1),  # !!! We should find the Time Signature.
            ClassNamesConstants.REST_HALF: Fraction(2, 1),
            ClassNamesConstants.REST_QUARTER: Fraction(1, 1),
            ClassNamesConstants.REST_8TH: Fraction(1, 2),
            ClassNamesConstants.REST_16TH: Fraction(1, 4),
            ClassNamesConstants.REST_32ND: Fraction(1, 8),
            ClassNamesConstants.REST_64TH: Fraction(1, 16),
            # Technically, these two should just apply time sig.,
            # but the measure-factorized precedence graph
            # means these durations never have sounding
            # descendants anyway:
            ClassNamesConstants.MULTI_MEASURE_REST: Fraction(4, 1),
            ClassNamesConstants.REPEAT_ONE_BAR: Fraction(4, 1),
        }
        duration = _LOOK_UP.get(rest_name, None)
        if duration is None:
            raise ValueError(f"Unknown rest name \"{rest_name}\"")
        return duration

    class Numerals(Enum):

        n0 = "numeral0"
        n1 = "numeral1"
        n2 = "numeral2"
        n3 = "numeral3"
        n4 = "numeral4"
        n5 = "numeral5"
        n6 = "numeral6"
        n7 = "numeral7"
        n8 = "numeral8"
        n9 = "numeral9"

        @classmethod
        def interpret(cls, numeral_list: list[str] | str) -> Optional[int]:
            if isinstance(numeral_list, str):
                numeral_list = [numeral_list]
            if len(numeral_list) == 0:
                return None

            numeral_to_digit = {
                cls.n0.value: 0,
                cls.n1.value: 1,
                cls.n2.value: 2,
                cls.n3.value: 3,
                cls.n4.value: 4,
                cls.n5.value: 5,
                cls.n6.value: 6,
                cls.n7.value: 7,
                cls.n8.value: 8,
                cls.n9.value: 9,
            }
            result = 0
            for numeral in numeral_list:
                current_num = numeral_to_digit.get(numeral, None)
                if current_num is None:
                    return None
                result = result * 10 + current_num
            return result
