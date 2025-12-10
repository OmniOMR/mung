from fractions import Fraction

from .class_names import ClassNamesConstants as C
from .general import STEP_ORDER


class InferenceEngineConstants(C):
    """This class stores the constants used for pitch inference."""

    ON_STAFFLINE_RATIO_THRESHOLD = 0.2
    '''Magic number for determining whether a notehead is *on* a leger
    line, or *next* to a leger line: if the ratio between the smaller
    and larger vertical difference of (top, bottom) vs. l.l. (top, bottom)
    is smaller than this, it means the notehead is most probably *NOT*
    on the l.l. and is next to it.'''
    
    STAFF_CLASSES = [
        C.STAFFLINE,
        C.STAFFSPACE,
        C.STAFF
    ]
    STAFFLINE_CLASS_NAMES = [
        C.STAFFLINE,
        C.STAFFSPACE
    ]

    STAFFLINE_LIKE_CLASS_NAMES = [
        C.STAFFLINE,
        C.LEGER_LINE
    ]

    STAFF_RELATED_CLASS_NAMES = {
        C.STAFF_GROUPING,
        C.MEASURE_SEPARATOR,
        C.TIME_SIGNATURE,
        C.KEY_SIGNATURE,
        C.G_CLEF,
        C.C_CLEF,
        C.F_CLEF
    }

    SYSTEM_LEVEL_CLASS_NAMES = [
        C.STAFF_GROUPING,
        C.MEASURE_SEPARATOR
    ]

    NOTEHEAD_CLASS_NAMES = [
        C.NOTEHEAD_FULL,
        C.NOTEHEAD_HALF,
        C.NOTEHEAD_WHOLE,
        C.NOTEHEAD_FULL_SMALL,
        C.NOTEHEAD_HALF_SMALL,
    ]

    NOTEHEADS_EMPTY = [
        C.NOTEHEAD_HALF,
        C.NOTEHEAD_WHOLE
    ]

    GRACE_NOTEHEAD_CLASS_NAMES = [
        C.NOTEHEAD_FULL_SMALL,
        C.NOTEHEAD_HALF_SMALL
    ]

    NONGRACE_NOTEHEAD_CLASS_NAMES = [
        C.NOTEHEAD_FULL,
        C.NOTEHEAD_HALF,
        C.NOTEHEAD_WHOLE
    ]

    CLEF_CLASS_NAMES = [
        C.G_CLEF,
        C.C_CLEF,
        C.F_CLEF
    ]

    MEASURE_SEPARATOR_CLASS_NAMES = [
        C.MEASURE_SEPARATOR,
    ]

    FLAGS_CLASS_NAMES = [
        C.FLAG_8TH_UP,
        C.FLAG_8TH_DOWN,
        C.FLAG_16TH_UP,
        C.FLAG_16TH_DOWN,
        C.FLAG_32ND_UP,
        C.FLAG_32ND_DOWN,
        C.FLAG_64TH_UP,
        C.FLAG_64TH_DOWN,
    ]

    BEAM_CLASS_NAMES = [
        C.BEAM,
    ]

    FLAGS_AND_BEAMS = list(FLAGS_CLASS_NAMES + BEAM_CLASS_NAMES)

    ACCIDENTAL_CLASS_NAMES = [
        C.ACCIDENTAL_SHARP,
        C.ACCIDENTAL_FLAT,
        C.ACCIDENTAL_NATURAL,
        C.ACCIDENTAL_DOUBLE_SHARP,
        C.ACCIDENTAL_DOUBLE_FLAT,
    ]

    HAIRPINS = [
        C.DYNAMIC_CRESHENDO_HAIRPIN,
        C.DYNAMIC_DIMINUENDO_HAIRPIN,
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
        C.G_CLEF: {
            C.G_CLEF: 0,
            C.C_CLEF: 6,
            C.F_CLEF: 12,
        },
        C.C_CLEF: {
            C.G_CLEF: -6,
            C.C_CLEF: 0,
            C.F_CLEF: 6,
        },
        C.F_CLEF: {
            C.G_CLEF: -12,
            C.C_CLEF: -6,
            C.F_CLEF: 0,
        }
    }

    PITCH_STEPS = STEP_ORDER + STEP_ORDER
    # Wrap around twice for easier indexing.

    ACCIDENTAL_CODES = {
        C.ACCIDENTAL_SHARP: '#',
        C.ACCIDENTAL_FLAT: 'b',
        C.ACCIDENTAL_DOUBLE_SHARP: 'x',
        C.ACCIDENTAL_DOUBLE_FLAT: 'bb'
    }

    REST_CLASS_NAMES = [
        C.REST_WHOLE,
        C.REST_HALF,
        C.REST_QUARTER,
        C.REST_8TH,
        C.REST_16TH,
        C.REST_32ND,
        C.REST_64TH,
        C.MULTI_MEASURE_REST,
        C.REST_BREVE,
        C.REST_LONGA
    ]

    MEASURE_LASTING_CLASS_NAMES = [
        C.REST_WHOLE,
        C.REST_BREVE,
        C.REST_LONGA,
        C.MULTI_MEASURE_REST,
        C.REPEAT_ONE_BAR
    ]

    TIME_SIGNATURES = [
        C.TIME_SIGNATURE
    ]

    TIME_SIGNATURE_MEMBERS = [
        C.TIME_SIG_COMMON,
        C.TIME_SIG_CUT_COMMON,
        C.N0,
        C.N1,
        C.N2,
        C.N3,
        C.N4,
        C.N5,
        C.N6,
        C.N7,
        C.N8,
        C.N9,
    ]

    NUMERALS = [
        C.N0,
        C.N1,
        C.N2,
        C.N3,
        C.N4,
        C.N5,
        C.N6,
        C.N7,
        C.N8,
        C.N9,
    ]

    IN_MEASURE = (
        TIME_SIGNATURES
        + [C.KEY_SIGNATURE]
        + CLEF_CLASS_NAMES
        
        + NOTEHEAD_CLASS_NAMES
        + REST_CLASS_NAMES
        + [C.REPEAT_ONE_BAR]
    )
    
    CLASSES_AFFECTING_ONSETS = list(set(
        NONGRACE_NOTEHEAD_CLASS_NAMES
        + REST_CLASS_NAMES
        + MEASURE_SEPARATOR_CLASS_NAMES
        + TIME_SIGNATURES
        + [C.REPEAT_ONE_BAR]
    ))

    CLASSES_BEARING_DURATIONS = list(set(
        NONGRACE_NOTEHEAD_CLASS_NAMES
        + REST_CLASS_NAMES
        + [C.REPEAT_ONE_BAR]
    ))

    DEFAULT_MEASURE_DURATION = Fraction(4)
