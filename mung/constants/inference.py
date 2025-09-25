from .class_names import ClassNamesConstants
from .general import STEP_ORDER


class InferenceEngineConstants(ClassNamesConstants):
    """This class stores the constants used for pitch inference."""

    ON_STAFFLINE_RATIO_THRESHOLD = 0.2
    '''Magic number for determining whether a notehead is *on* a leger
    line, or *next* to a leger line: if the ratio between the smaller
    and larger vertical difference of (top, bottom) vs. l.l. (top, bottom)
    is smaller than this, it means the notehead is most probably *NOT*
    on the l.l. and is next to it.'''
    
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

    SYSTEM_LEVEL_CLASS_NAMES = [
        ClassNamesConstants.STAFF_GROUPING,
        ClassNamesConstants.MEASURE_SEPARATOR
    ]

    NOTEHEAD_CLASS_NAMES = [
        ClassNamesConstants.NOTEHEAD_FULL,
        ClassNamesConstants.NOTEHEAD_HALF,
        ClassNamesConstants.NOTEHEAD_WHOLE,
        ClassNamesConstants.NOTEHEAD_FULL_SMALL,
        ClassNamesConstants.NOTEHEAD_HALF_SMALL,
    ]

    NOTEHEADS_EMPTY = [
        ClassNamesConstants.NOTEHEAD_HALF,
        ClassNamesConstants.NOTEHEAD_WHOLE
    ]

    GRACE_NOTEHEAD_CLASS_NAMES = [
        ClassNamesConstants.NOTEHEAD_FULL_SMALL,
        ClassNamesConstants.NOTEHEAD_HALF_SMALL
    ]

    NONGRACE_NOTEHEAD_CLASS_NAMES = [
        ClassNamesConstants.NOTEHEAD_FULL,
        ClassNamesConstants.NOTEHEAD_HALF,
        ClassNamesConstants.NOTEHEAD_WHOLE
    ]

    CLEF_CLASS_NAMES = [
        ClassNamesConstants.G_CLEF,
        ClassNamesConstants.C_CLEF,
        ClassNamesConstants.F_CLEF
    ]

    MEASURE_SEPARATOR_CLASS_NAMES = [
        ClassNamesConstants.MEASURE_SEPARATOR,
    ]

    FLAGS_CLASS_NAMES = [
        ClassNamesConstants.FLAG_8TH_UP,
        ClassNamesConstants.FLAG_8TH_DOWN,
        ClassNamesConstants.FLAG_16TH_UP,
        ClassNamesConstants.FLAG_16TH_DOWN,
        ClassNamesConstants.FLAG_32ND_UP,
        ClassNamesConstants.FLAG_32ND_DOWN,
        ClassNamesConstants.FLAG_64TH_UP,
        ClassNamesConstants.FLAG_64TH_DOWN,
    ]

    BEAM_CLASS_NAMES = [
        ClassNamesConstants.BEAM,
    ]

    FLAGS_AND_BEAMS = list(FLAGS_CLASS_NAMES + BEAM_CLASS_NAMES)

    ACCIDENTAL_CLASS_NAMES = [
        ClassNamesConstants.ACCIDENTAL_SHARP,
        ClassNamesConstants.ACCIDENTAL_FLAT,
        ClassNamesConstants.ACCIDENTAL_NATURAL,
        ClassNamesConstants.ACCIDENTAL_DOUBLE_SHARP,
        ClassNamesConstants.ACCIDENTAL_DOUBLE_FLAT,
    ]

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

    PITCH_STEPS = STEP_ORDER + STEP_ORDER
    # Wrap around twice for easier indexing.

    ACCIDENTAL_CODES = {
        ClassNamesConstants.ACCIDENTAL_SHARP: '#',
        ClassNamesConstants.ACCIDENTAL_FLAT: 'b',
        ClassNamesConstants.ACCIDENTAL_DOUBLE_SHARP: 'x',
        ClassNamesConstants.ACCIDENTAL_DOUBLE_FLAT: 'bb'
    }

    REST_CLASS_NAMES = [
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
    ]

    MEASURE_LASTING_CLASS_NAMES = [
        ClassNamesConstants.REST_WHOLE,
        ClassNamesConstants.REST_BREVE,
        ClassNamesConstants.REST_LONGA,
        ClassNamesConstants.MULTI_MEASURE_REST,
        ClassNamesConstants.REPEAT_ONE_BAR
    ]

    TIME_SIGNATURES = [
        ClassNamesConstants.TIME_SIGNATURE
    ]

    TIME_SIGNATURE_MEMBERS = [
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
    ]

    NUMERALS = [
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
    ]

    @property
    def CLASSES_AFFECTING_ONSETS(self) -> list[str]:
        """Returns a list of Node class names for objects
        that affect onsets. Assumes notehead and rest durations
        have already been given."""
        return list(set(self.NONGRACE_NOTEHEAD_CLASS_NAMES
        + self.REST_CLASS_NAMES
        + self.MEASURE_SEPARATOR_CLASS_NAMES
        + self.TIME_SIGNATURES
        + [ClassNamesConstants.REPEAT_ONE_BAR]
        ))

    @property
    def CLASSES_BEARING_DURATIONS(self) -> list[str]:
        """Returns the list of classes that actually bear duration,
        i.e. contribute to onsets of their descendants in the precedence
        graph."""
        return list(set(
        self.NONGRACE_NOTEHEAD_CLASS_NAMES
        + self.REST_CLASS_NAMES
        ))
