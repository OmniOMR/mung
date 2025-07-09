"""This module implements constants that are used inside the pitch,
duration and onset inference algorithm."""

from enum import Enum
from fractions import Fraction
from typing import Optional


class PrecedenceLinksConstants(object):
    """
    This class stores names of precedence-link-related fields in ``Node.data``.
    """
    PrecedenceInlinks: str = "precedence_inlinks"
    PrecedenceOutlinks: str = "precedence_outlinks"


class ClassNamesConstants(object):
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

    REST_BREVE = "rest_breve"
    REST_LONGA = "rest_longa"

    REPEAT_ONE_BAR = "repeat1Bar"
    MULTI_MEASURE_REST = "multiMeasureRest"
    AUGMENTATION_DOT = "augmentationDot"

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

    ACCIDENTAL_SHAPR = "accidentalSharp"
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


class InferenceEngineConstants(ClassNamesConstants):
    """This class stores the constants used for pitch inference."""

    ON_STAFFLINE_RATIO_THRESHOLD = 0.2
    '''Magic number for determining whether a notehead is *on* a leger
    line, or *next* to a leger line: if the ratio between the smaller
    and larger vertical difference of (top, bottom) vs. l.l. (top, bottom)
    is smaller than this, it means the notehead is most probably *NOT*
    on the l.l. and is next to it.'''

    # TODO: why are some groups lists and some sets?
    STAFF_CLASSES = [
        ClassNamesConstants.STAFFLINE,
        ClassNamesConstants.STAFFSPACE,
        ClassNamesConstants.STAFF
    ]
    STAFFLINE_CLASS_NAMES = [
        ClassNamesConstants.STAFFLINE,
        ClassNamesConstants.STAFFSPACE
    ]

    STAFFLINE_LIKE_CLASS_NAMES = [
        ClassNamesConstants.STAFFLINE,
        ClassNamesConstants.LEGER_LINE
    ]

    STAFF_RELATED_CLASS_NAMES = {
        ClassNamesConstants.STAFF_GROUPING,
        ClassNamesConstants.MEASURE_SEPARATOR,
        ClassNamesConstants.TIME_SIGNATURE,
        ClassNamesConstants.KEY_SIGNATURE,
        ClassNamesConstants.G_CLEF,
        ClassNamesConstants.C_CLEF,
        ClassNamesConstants.F_CLEF
    }

    SYSTEM_LEVEL_CLASS_NAMES = {
        ClassNamesConstants.STAFF_GROUPING,
        ClassNamesConstants.MEASURE_SEPARATOR
    }

    NOTEHEAD_CLASS_NAMES = {
        ClassNamesConstants.NOTEHEAD_FULL,
        ClassNamesConstants.NOTEHEAD_HALF,
        ClassNamesConstants.NOTEHEAD_WHOLE,
        ClassNamesConstants.NOTEHEAD_FULL_SMALL,
        ClassNamesConstants.NOTEHEAD_HALF_SMALL,
    }

    NOTEHEADS_EMPTY = {
        ClassNamesConstants.NOTEHEAD_HALF,
        ClassNamesConstants.NOTEHEAD_WHOLE
    }

    GRACE_NOTEHEAD_CLASS_NAMES = {
        ClassNamesConstants.NOTEHEAD_FULL_SMALL,
        ClassNamesConstants.NOTEHEAD_HALF_SMALL
    }

    NONGRACE_NOTEHEAD_CLASS_NAMES = {
        ClassNamesConstants.NOTEHEAD_FULL,
        ClassNamesConstants.NOTEHEAD_HALF,
        ClassNamesConstants.NOTEHEAD_WHOLE
    }

    CLEF_CLASS_NAMES = {
        ClassNamesConstants.G_CLEF,
        ClassNamesConstants.C_CLEF,
        ClassNamesConstants.F_CLEF
    }

    MEASURE_SEPARATOR_CLASS_NAMES = {
        ClassNamesConstants.MEASURE_SEPARATOR,
    }

    FLAGS_CLASS_NAMES = {
        ClassNamesConstants.FLAG_8TH_UP,
        ClassNamesConstants.FLAG_8TH_DOWN,
        ClassNamesConstants.FLAG_16TH_UP,
        ClassNamesConstants.FLAG_16TH_DOWN,
        ClassNamesConstants.FLAG_32ND_UP,
        ClassNamesConstants.FLAG_32ND_DOWN,
        ClassNamesConstants.FLAG_64TH_UP,
        ClassNamesConstants.FLAG_64TH_DOWN,
    }

    BEAM_CLASS_NAMES = {
        ClassNamesConstants.BEAM,
    }

    FLAGS_AND_BEAMS = set(list(FLAGS_CLASS_NAMES) + list(BEAM_CLASS_NAMES))

    ACCIDENTAL_CLASS_NAMES = {
        ClassNamesConstants.ACCIDENTAL_SHAPR: 1,
        ClassNamesConstants.ACCIDENTAL_FLAT: -1,
        ClassNamesConstants.ACCIDENTAL_NATURAL: 0,
        ClassNamesConstants.ACCIDENTAL_DOUBLE_SHARP: 2,
        ClassNamesConstants.ACCIDENTAL_DOUBLE_FLAT: -2,
    }

    MIDI_CODE_RESIDUES_FOR_PITCH_STEPS = {
        0: 'C',
        1: 'C#',
        2: 'D',
        3: 'Eb',
        4: 'E',
        5: 'F',
        6: 'F#',
        7: 'G',
        8: 'Ab',
        9: 'A',
        10: 'Bb',
        11: 'B',
    }
    '''Simplified pitch naming.'''

    # The individual MIDI codes for for the unmodified steps.
    _fs = list(range(5, 114, 12))
    _cs = list(range(0, 121, 12))
    _gs = list(range(7, 116, 12))
    _ds = list(range(2, 110, 12))
    _as = list(range(9, 118, 12))
    _es = list(range(4, 112, 12))
    _bs = list(range(11, 120, 12))

    KEY_TABLE_SHARPS = {
        0: {},
        1: {i: 1 for i in _fs},
        2: {i: 1 for i in _fs + _cs},
        3: {i: 1 for i in _fs + _cs + _gs},
        4: {i: 1 for i in _fs + _cs + _gs + _ds},
        5: {i: 1 for i in _fs + _cs + _gs + _ds + _as},
        6: {i: 1 for i in _fs + _cs + _gs + _ds + _as + _es},
        7: {i: 1 for i in _fs + _cs + _gs + _ds + _as + _es + _bs},
    }

    KEY_TABLE_FLATS = {
        0: {},
        1: {i: -1 for i in _bs},
        2: {i: -1 for i in _bs + _es},
        3: {i: -1 for i in _bs + _es + _as},
        4: {i: -1 for i in _bs + _es + _as + _ds},
        5: {i: -1 for i in _bs + _es + _as + _ds + _gs},
        6: {i: -1 for i in _bs + _es + _as + _ds + _gs + _cs},
        7: {i: -1 for i in _bs + _es + _as + _ds + _gs + _cs + _fs},
    }

    # FROM clef --> TO clef. Imagine this on inline accidental delta
    CLEF_CHANGE_DELTA = {
        ClassNamesConstants.G_CLEF: {
            ClassNamesConstants.G_CLEF: 0,
            ClassNamesConstants.C_CLEF: 6,
            ClassNamesConstants.F_CLEF: 12,
        },
        ClassNamesConstants.C_CLEF: {
            ClassNamesConstants.G_CLEF: -6,
            ClassNamesConstants.C_CLEF: 0,
            ClassNamesConstants.F_CLEF: 6,
        },
        ClassNamesConstants.F_CLEF: {
            ClassNamesConstants.G_CLEF: -12,
            ClassNamesConstants.C_CLEF: -6,
            ClassNamesConstants.F_CLEF: 0,
        }
    }

    PITCH_STEPS = ['C', 'D', 'E', 'F', 'G', 'A', 'B',
                   'C', 'D', 'E', 'F', 'G', 'A', 'B']
    # Wrap around twice for easier indexing.

    ACCIDENTAL_CODES = {
        ClassNamesConstants.ACCIDENTAL_SHAPR: '#',
        ClassNamesConstants.ACCIDENTAL_FLAT: 'b',
        ClassNamesConstants.ACCIDENTAL_DOUBLE_SHARP: 'x',
        ClassNamesConstants.ACCIDENTAL_DOUBLE_FLAT: 'bb'
    }

    REST_CLASS_NAMES = {
        ClassNamesConstants.REST_WHOLE,
        ClassNamesConstants.REST_HALF,
        ClassNamesConstants.REST_QUARTER,
        ClassNamesConstants.REST_8TH,
        ClassNamesConstants.REST_16TH,
        ClassNamesConstants.REST_32ND,
        ClassNamesConstants.REST_64TH,
        ClassNamesConstants.MULTI_MEASURE_REST,
        ClassNamesConstants.REST_BREVE,
        ClassNamesConstants.REST_LONGA
    }

    MEASURE_LASTING_CLASS_NAMES = {
        ClassNamesConstants.REST_WHOLE,
        ClassNamesConstants.REST_BREVE,
        ClassNamesConstants.REST_LONGA,
        ClassNamesConstants.MULTI_MEASURE_REST,
        ClassNamesConstants.REPEAT_ONE_BAR
    }

    TIME_SIGNATURES = {
        ClassNamesConstants.TIME_SIGNATURE
    }

    TIME_SIGNATURE_MEMBERS = {
        ClassNamesConstants.TIME_SIG_COMMON,
        ClassNamesConstants.TIME_SIG_CUT_COMMON,
        ClassNamesConstants.Numerals.n0.value,
        ClassNamesConstants.Numerals.n1.value,
        ClassNamesConstants.Numerals.n2.value,
        ClassNamesConstants.Numerals.n3.value,
        ClassNamesConstants.Numerals.n4.value,
        ClassNamesConstants.Numerals.n5.value,
        ClassNamesConstants.Numerals.n6.value,
        ClassNamesConstants.Numerals.n7.value,
        ClassNamesConstants.Numerals.n8.value,
        ClassNamesConstants.Numerals.n9.value
    }

    NUMERALS = {
        ClassNamesConstants.Numerals.n0.value,
        ClassNamesConstants.Numerals.n1.value,
        ClassNamesConstants.Numerals.n2.value,
        ClassNamesConstants.Numerals.n3.value,
        ClassNamesConstants.Numerals.n4.value,
        ClassNamesConstants.Numerals.n5.value,
        ClassNamesConstants.Numerals.n6.value,
        ClassNamesConstants.Numerals.n7.value,
        ClassNamesConstants.Numerals.n8.value,
        ClassNamesConstants.Numerals.n9.value
    }

    @property
    def classes_affecting_onsets(self):
        """Returns a list of Node class names for objects
        that affect onsets. Assumes notehead and rest durations
        have already been given."""
        output = set()
        output.update(self.NONGRACE_NOTEHEAD_CLASS_NAMES)
        output.update(self.REST_CLASS_NAMES)
        output.update(self.MEASURE_SEPARATOR_CLASS_NAMES)
        output.update(self.TIME_SIGNATURES)
        output.add(ClassNamesConstants.REPEAT_ONE_BAR)
        return output

    @property
    def classes_bearing_duration(self):
        """Returns the list of classes that actually bear duration,
        i.e. contribute to onsets of their descendants in the precedence
        graph."""
        output = set()
        output.update(self.NONGRACE_NOTEHEAD_CLASS_NAMES)
        output.update(self.REST_CLASS_NAMES)
        return output
