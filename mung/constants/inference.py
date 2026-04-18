from fractions import Fraction

from .class_names import ClassNameConstants as C
from .general import STEP_ORDER


class InferenceEngineConstants(C):
    """This class stores the constants used for pitch inference."""

    ON_STAFFLINE_RATIO_THRESHOLD = 0.2
    '''Magic number for determining whether a notehead is *on* a leger
    line, or *next* to a leger line: if the ratio between the smaller
    and larger vertical difference of (top, bottom) vs. l.l. (top, bottom)
    is smaller than this, it means the notehead is most probably *NOT*
    on the l.l. and is next to it.'''
    
    STAFF_CLASSES = C.Staves.ALL()

    STAFFLINE_CLASS_NAMES = [
        C.Staves.STAFF_LINE,
        C.Staves.STAFF_SPACE
    ]

    STAFFLINE_LIKE_CLASS_NAMES = [
        C.NoteheadAttachments.LEGER_LINE,
        C.Staves.STAFF_LINE
    ]

    STAFF_RELATED_CLASS_NAMES = {
        C.StaffGroupingBracketsAndBraces.STAFF_GROUPING,
        C.Barlines.MEASURE_SEPARATOR,
        C.TimeSignatures.TIME_SIGNATURE,
        C.KeySignature.KEY_SIGNATURE,
    } | set(C.Clefs.ALL())

    INSTRUMENT_GROUP_BRACKETS = {
        C.StaffGroupingBracketsAndBraces.BRACE,
        C.StaffGroupingBracketsAndBraces.BRACKET,
    }

    SYSTEM_LEVEL_CLASS_NAMES = [
        C.StaffGroupingBracketsAndBraces.STAFF_GROUPING,
        C.Barlines.MEASURE_SEPARATOR,
    ]

    NOTEHEAD_CLASS_NAMES = C.Noteheads.ALL()

    NOTEHEADS_EMPTY = [
        C.Noteheads.NOTEHEAD_HALF,
        C.Noteheads.NOTEHEAD_WHOLE,
    ]

    GRACE_NOTEHEAD_CLASS_NAMES = [
        C.Noteheads.NOTEHEAD_HALF_SMALL,
        C.Noteheads.NOTEHEAD_BLACK_SMALL,
    ]

    NONGRACE_NOTEHEAD_CLASS_NAMES = [
        C.Noteheads.NOTEHEAD_BLACK,
        C.Noteheads.NOTEHEAD_HALF,
        C.Noteheads.NOTEHEAD_WHOLE,
    ]

    NOTEHEADS_AND_RESTS = (
        NONGRACE_NOTEHEAD_CLASS_NAMES
        + C.Rests.ALL()
    )

    CLEF_CLASS_NAMES = C.Clefs.ALL()

    MEASURE_SEPARATOR_CLASS_NAMES = [
        C.Barlines.MEASURE_SEPARATOR,
    ]

    FLAGS_CLASS_NAMES = C.Flags.ALL()

    BEAM_CLASS_NAMES = [
        C.NoteheadAttachments.BEAM,
    ]

    FLAGS_AND_BEAMS = list(FLAGS_CLASS_NAMES + BEAM_CLASS_NAMES)

    ACCIDENTAL_CLASS_NAMES = C.Accidentals.ALL()

    HAIRPINS = [
        C.Dynamics.DYNAMIC_CRESCENDO_HAIRPIN,
        C.Dynamics.DYNAMIC_DIMINUENDO_HAIRPIN,
    ]

    TREMOLO_SINGLES = C.Tremolo.all_numeral_members()

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
    @staticmethod
    def clef_change_delta(from_clef: str, to_clef: str) -> int:
        f = from_clef.replace("Change", "")
        t = to_clef.replace("Change", "")
        return InferenceEngineConstants._CLEF_CHANGE_DELTA[C.Clefs(f)][C.Clefs(t)]
    
    CC = C.Clefs
    _CLEF_CHANGE_DELTA = {
        CC.G_CLEF: {
            CC.G_CLEF: 0,
            CC.C_CLEF: 6,
            CC.F_CLEF: 12,
        },
        CC.C_CLEF: {
            CC.G_CLEF: -6,
            CC.C_CLEF: 0,
            CC.F_CLEF: 6,
        },
        CC.F_CLEF: {
            CC.G_CLEF: -12,
            CC.C_CLEF: -6,
            CC.F_CLEF: 0,
        }
    }

    PITCH_STEPS = STEP_ORDER + STEP_ORDER
    # Wrap around twice for easier indexing.

    ACCIDENTAL_CODES = {
        C.Accidentals.ACCIDENTAL_SHARP: '#',
        C.Accidentals.ACCIDENTAL_FLAT: 'b',
        C.Accidentals.ACCIDENTAL_DOUBLE_SHARP: 'x',
        C.Accidentals.ACCIDENTAL_DOUBLE_FLAT: 'bb'
    }

    REST_CLASS_NAMES = C.Rests.ALL()

    MEASURE_LASTING_CLASS_NAMES = [
        C.Rests.REST_WHOLE,
        C.Rests.REST_DOUBLE_WHOLE,
        C.Rests.REST_LONGA,
        C.Rests.REST_H_BAR,
        C.Repeat.REPEAT_1_BAR
    ]

    TIME_SIGNATURES = [
        C.TimeSignatures.TIME_SIGNATURE
    ]

    TIME_SIGNATURE_MEMBERS = [
        # all but the container class
        tsm for tsm in C.TimeSignatures.ALL() if tsm != C.TimeSignatures.TIME_SIGNATURE
    ]

    NUMERALS = C.Numerals.ALL()

    IN_MEASURE = (
        TIME_SIGNATURES
        + [C.KeySignature.KEY_SIGNATURE]
        + CLEF_CLASS_NAMES
        
        + NOTEHEAD_CLASS_NAMES
        + REST_CLASS_NAMES
        + [C.Repeat.REPEAT_1_BAR]
    )
    
    CLASSES_AFFECTING_ONSETS = list(set(
        NONGRACE_NOTEHEAD_CLASS_NAMES
        + REST_CLASS_NAMES
        + MEASURE_SEPARATOR_CLASS_NAMES
        + TIME_SIGNATURES
        + [C.Repeat.REPEAT_1_BAR]
    ))

    CLASSES_BEARING_DURATIONS = list(set(
        NONGRACE_NOTEHEAD_CLASS_NAMES
        + REST_CLASS_NAMES
        + [C.Repeat.REPEAT_1_BAR]
    ))

    DEFAULT_MEASURE_DURATION = Fraction(4)

    @staticmethod
    def rest_name_to_duration(rest_name: str) -> Fraction:
        """
        Returns the duration of a rest as a fraction based on a rest name.

        :param rest_name: The rest class name.
        :return: The duration of the rest as a Fraction.
        """
        
        _LOOK_UP = {
            C.Rests.REST_LONGA: Fraction(16, 1),  # !!! We should find the Time Signature.
            C.Rests.REST_DOUBLE_WHOLE: Fraction(
                8, 1
            ),  # !!! We should find the Time Signature.
            C.Rests.REST_WHOLE: Fraction(4, 1),  # !!! We should find the Time Signature.
            C.Rests.REST_HALF: Fraction(2, 1),
            C.Rests.REST_QUARTER: Fraction(1, 1),
            C.Rests.REST_8TH: Fraction(1, 2),
            C.Rests.REST_16TH: Fraction(1, 4),
            C.Rests.REST_32ND: Fraction(1, 8),
            C.Rests.REST_64TH: Fraction(1, 16),
            # Technically, these two should just apply time sig.,
            # but the measure-factorized precedence graph
            # means these durations never have sounding
            # descendants anyway:
            C.Rests.REST_H_BAR: Fraction(4, 1),
            C.Repeat.REPEAT_1_BAR: Fraction(4, 1),
        }
        duration = _LOOK_UP.get(rest_name, None)
        if duration is None:
            raise ValueError(f'Unknown rest name "{rest_name}"')
        return duration
