from enum import StrEnum

from .utils import (
    AllExtendedStrEnum,
    AllStrEnumNumeralMapped,
    Numerals
)

    
class Staves(AllExtendedStrEnum):
    STAFF_LINE = "staffLine"
    STAFF_SPACE = "staffSpace"
    STAFF = "staff"


class Noteheads(AllExtendedStrEnum):
    NOTEHEAD_WHOLE = "noteheadWhole"
    NOTEHEAD_HALF = "noteheadHalf"
    NOTEHEAD_BLACK = "noteheadBlack"

    NOTEHEAD_HALF_SMALL = "noteheadHalfSmall"
    NOTEHEAD_BLACK_SMALL = "noteheadBlackSmall"


class Flags(AllExtendedStrEnum):
    FLAG_8_UP = "flag8thUp"
    FLAG_8_DOWN = "flag8thDown"
    FLAG_16_UP = "flag16thUp"
    FLAG_16_DOWN = "flag16thDown"
    FLAG_32_UP = "flag32ndUp"
    FLAG_32_DOWN = "flag32ndDown"
    FLAG_64_UP = "flag64thUp"
    FLAG_64_DOWN = "flag64thDown"


class NoteheadAttachments(StrEnum):
    STEM = "stem"
    BEAM = "beam"
    LEGER_LINE = "legerLine"
    AUGMENTATION_DOT = "augmentationDot"

    GRACE_NOTE_SLASH_STEM_UP = "graceNoteSlashStemUp"
    GRACE_NOTE_SLASH_STEM_DOWN = "graceNoteSlashStemDown"

    FERMATA_ABOVE = "fermataAbove"
    FERMATA_BELOW = "fermataBelow"


class Spanners(StrEnum):
    SLUR = "slur"
    TIE = "tie"


class Rests(AllExtendedStrEnum):
    REST_WHOLE = "restWhole"
    REST_HALF = "restHalf"
    REST_QUARTER = "restQuarter"
    REST_8TH = "rest8th"
    REST_16TH = "rest16th"
    REST_32ND = "rest32nd"
    REST_64TH = "rest64nd"
    REST_LONGA = "restLonga"
    REST_DOUBLE_WHOLE = "restDoubleWhole"
    REST_H_BAR = "restHBar"
    REST_TEXT = "restText"


class Accidentals(AllExtendedStrEnum):
    ACCIDENTAL_SHARP = "accidentalSharp"
    ACCIDENTAL_FLAT = "accidentalFlat"
    ACCIDENTAL_NATURAL = "accidentalNatural"
    ACCIDENTAL_DOUBLE_SHARP = "accidentalDoubleSharp"
    ACCIDENTAL_DOUBLE_FLAT = "accidentalDoubleFlat"


class Clefs(AllExtendedStrEnum):
    G_CLEF = "gClef"
    G_CLEF_CHANGE = "gClefChange"
    F_CLEF = "fClef"
    F_CLEF_CHANGE = "fClefChange"
    C_CLEF = "cClef"
    C_CLEF_CHANGE = "cClefChange"


class KeySignature(StrEnum):
    KEY_SIGNATURE = "keySignature"


class TimeSignatures(AllStrEnumNumeralMapped):
    TIME_SIG0 = "timeSig0"
    TIME_SIG1 = "timeSig1"
    TIME_SIG2 = "timeSig2"
    TIME_SIG3 = "timeSig3"
    TIME_SIG4 = "timeSig4"
    TIME_SIG5 = "timeSig5"
    TIME_SIG6 = "timeSig6"
    TIME_SIG7 = "timeSig7"
    TIME_SIG8 = "timeSig8"
    TIME_SIG9 = "timeSig9"

    TIME_SIG_COMMON = "timeSigCommon"
    MENSURAL_PROLATION_COMBINING_DOT = "mensuralProlationCombiningDot"
    TIME_SIG_CUT_COMMON = "timeSigCutCommon"
    TIME_SIG_SLASH = "timeSigSlash"
    TIME_SIG_FRACTIONAL_SLASH = "timeSigFractionalSlash"
    TIME_SIG_PLUS = "timeSigPlus"
    TIME_SIG_EQUALS = "timeSigEquals"
    TIME_SIGNATURE = "timeSignature"


class Lyrics(StrEnum):
    LYRICS_TEXT = "lyricsText"
    VERSE_NUMBER = "verseNumber"


class Tempo(StrEnum):
    TEMPO_TEXT = "tempoText"
    TEMPO_RITARDANDO = "tempoRitardando"
    TEMPO_ACCELERANDO = "tempoAccelerando"
    TEMPO_A_TEMPO = "tempoATempo"


class Text(StrEnum):
    INTERPRETATION_TEXT = "interpretationText"
    METADATA_TEXT = "metadataText"
    MEASURE_NUMBER = "measureNumber"
    PAGE_NUMBER = "pageNumber"
    OTHER_TEXT = "otherText"


class Barlines(StrEnum):
    BARLINE_SINGLE = "barlineSingle"
    BARLINE_HEAVY = "barlineHeavy"
    BARLINE_FINAL = "barlineFinal"
    BARLINE_WING = "barlineWing"
    MEASURE_SEPARATOR = "measureSeparator"


class StaffGroupingBracketsAndBraces(StrEnum):
    BRACE = "brace"
    BRACKET = "bracket"
    STAFF_GROUPING = "staffGrouping"
    SYSTEM_DIVIDER = "systemDivider"


class Articulation(StrEnum):
    ARTIC_ACCENT_ABOVE = "articAccentAbove"
    ARTIC_ACCENT_BELOW = "articAccentBelow"

    ARTIC_STACCATO_ABOVE = "articStaccatoAbove"
    ARTIC_STACCATO_BELOW = "articStaccatoBelow"

    ARTIC_TENUTO_ABOVE = "articTenutoAbove"
    ARTIC_TENUTO_BELOW = "articTenutoBelow"

    ARTIC_STACCATISSIMO_ABOVE = "articStaccatissimoAbove"
    ARTIC_STACCATISSIMO_BELOW = "articStaccatissimoBelow"

    ARTIC_MARCATO_ABOVE = "articMarcatoAbove"
    ARTIC_MARCATO_BELOW = "articMarcatoBelow"


class Dynamics(StrEnum):
    DYNAMICS_TEXT = "dynamicsText"

    DYNAMIC_CRESCENDO = "dynamicCrescendo"
    DYNAMIC_CRESCENDO_SPANNER = "dynamicCrescendoSpanner"
    DYNAMIC_DIMINUENDO = "dynamicDiminuendo"
    DYNAMIC_DIMINUENDO_SPANNER = "dynamicDiminuendoSpanner"

    DYNAMIC_PIANO = "dynamicPiano"
    DYNAMIC_MEZZO = "dynamicMezzo"
    DYNAMIC_FORTE = "dynamicForte"
    DYNAMIC_RINFORZANDO = "dynamicRinforzando"
    DYNAMIC_SFORZANDO = "dynamicSforzando"
    DYNAMIC_Z = "dynamicZ"

    DYNAMIC_CRESCENDO_HAIRPIN = "dynamicCrescendoHairpin"
    DYNAMIC_DIMINUENDO_HAIRPIN = "dynamicDiminuendoHairpin"

    DYNAMIC_NIENTE = "dynamicNiente"
    DYNAMIC_NIENTE_FOR_HAIRPIN = "dynamicNienteForHairpin"


class Repeat(StrEnum):
    REPEAT_LEFT = "repeatLeft"
    REPEAT_RIGHT = "repeatRight"
    REPEAT_DOT = "repeatDot"
    # TODO: voltas
    REPEAT_1_BAR = "repeat1Bar"


class Tuplets(AllStrEnumNumeralMapped):
    TUPLET0 = "tuplet0"
    TUPLET1 = "tuplet1"
    TUPLET2 = "tuplet2"
    TUPLET3 = "tuplet3"
    TUPLET4 = "tuplet4"
    TUPLET5 = "tuplet5"
    TUPLET6 = "tuplet6"
    TUPLET7 = "tuplet7"
    TUPLET8 = "tuplet8"
    TUPLET9 = "tuplet9"

    TUPLET_COLON = "tupletColon"
    TUPLET_BRACKET = "tupletBracket"
    TUPLET = "tuplet"


class Tremolo(AllStrEnumNumeralMapped):
    __digits__ = range(1, 5+1)
    TREMOLO_1 = "tremolo1"
    TREMOLO_2 = "tremolo2"
    TREMOLO_3 = "tremolo3"
    TREMOLO_4 = "tremolo4"
    TREMOLO_5 = "tremolo5"

    TREMOLO_BEAM = "tremoloBeam"


class Ornaments(StrEnum):
    ORNAMENT_TRILL = "ornamentTrill"
    WIGGLE_TRILL = "wiggleTrill"
    ORNAMENT_TURN = "ornamentTurn"
    ORNAMENT_TURN_INVERTED = "ornamentTurnInverted"
    ORNAMENT_SHORT_TRILL = "ornamentShortTrill"
    CUSTOS = "custos"
    ARPEGGIATO = "arpeggiato"


class FiguredBass(StrEnum):
    FIGURED_BASS_TEXT = "figuredBassText"
    FIGURED_BASS_SPANNER = "figured_bass_spanner"


class Other(StrEnum):
    UNCLASSIFIED = "unclassified"


class ClassNameConstants:
    Staves = Staves
    Noteheads = Noteheads
    Flags = Flags
    NoteheadAttachments = NoteheadAttachments
    Spanners = Spanners
    Rests = Rests
    Accidentals = Accidentals
    Clefs = Clefs
    KeySignature = KeySignature
    TimeSignatures = TimeSignatures
    Lyrics = Lyrics
    Text = Text
    Barlines = Barlines
    StaffGroupingBracketsAndBraces = StaffGroupingBracketsAndBraces
    Articulation = Articulation
    Dynamics = Dynamics
    Repeat = Repeat
    Tuplets = Tuplets
    Tremolo = Tremolo
    Ornaments = Ornaments
    FiguredBass = FiguredBass
    Other = Other
    Numerals = Numerals

    ALL = [
        value
        for value in vars().values()
        if isinstance(value, type) and issubclass(value, StrEnum)
    ]


# class ClassNamesConstants(Numerals):
#     """
#     This class stores all the current names of MuNG classes.
#     """

#     STAFF_GROUPING = "staffGrouping"
#     MEASURE_SEPARATOR = "measureSeparator"
#     BARLINE_SINGLE = "barlineSingle"
#     BARLINE_HEAVY = "barlineHeavy"
#     # BARLINE_SINGLE = "barlineSingle"

#     BRACE = "brace"
#     BRACKET = "bracket"

#     DYNAMIC_CRESCENDO_HAIRPIN = "dynamicCrescendoHairpin"
#     DYNAMIC_DIMINUENDO_HAIRPIN = "dynamicDiminuendoHairpin"

#     KEY_SIGNATURE = "keySignature"
#     TIME_SIGNATURE = "timeSignature"

#     STAFFLINE = "staffLine"
#     STAFFSPACE = "staffSpace"
#     STAFF = "staff"
#     LEGER_LINE = "legerLine"
#     STEM = "stem"

#     TIE_CLASS_NAME = "tie"
#     SLUR = "slur"

#     G_CLEF = "gClef"
#     C_CLEF = "cClef"
#     F_CLEF = "fClef"

#     G_CLEF_CHANGE = "gClefChange"
#     C_CLEF_CHANGE = "cClefChange"
#     F_CLEF_CHANGE = "fClefChange"

#     NOTEHEAD_BLACK = "noteheadBlack"
#     NOTEHEAD_HALF = "noteheadHalf"
#     NOTEHEAD_WHOLE = "noteheadWhole"
#     NOTEHEAD_FULL_SMALL = "noteheadBlackSmall"
#     NOTEHEAD_HALF_SMALL = "noteheadHalfSmall"

#     REST_WHOLE = "restWhole"
#     REST_HALF = "restHalf"
#     REST_QUARTER = "restQuarter"
#     REST_8TH = "rest8th"
#     REST_16TH = "rest16th"
#     REST_32ND = "rest32nd"
#     REST_64TH = "rest64th"

#     REST_DOUBLE_WHOLE = "restDoubleWhole"
#     REST_LONGA = "restLonga"

#     REPEAT_ONE_BAR = "repeat1Bar"
#     REST_H_BAR = "restHBar"
#     AUGMENTATION_DOT = "augmentationDot"

#     TUPLE = "tuple"
#     TUPLE_BRACKET = "tupletBracket"

#     FLAG_8TH_UP = "flag8thUp"
#     FLAG_8TH_DOWN = "flag8thDown"
#     FLAG_16TH_UP = "flag16thUp"
#     FLAG_16TH_DOWN = "flag16thDown"
#     FLAG_32ND_UP = "flag32ndUp"
#     FLAG_32ND_DOWN = "flag32ndDown"
#     FLAG_64TH_UP = "flag64thUp"
#     FLAG_64TH_DOWN = "flag64thDown"

#     BEAM = "beam"

#     ACCIDENTAL_SHARP = "accidentalSharp"
#     ACCIDENTAL_FLAT = "accidentalFlat"
#     ACCIDENTAL_NATURAL = "accidentalNatural"
#     ACCIDENTAL_DOUBLE_SHARP = "accidentalDoubleSharp"
#     ACCIDENTAL_DOUBLE_FLAT = "accidentalDoubleFlat"

#     TIME_SIG_COMMON = "timeSigCommon"
#     TIME_SIG_CUT_COMMON = "timeSigCutCommon"

#     LETTER_OTHER = "characterOther"

#     TREMOLO_MARK = "tremoloMark"

#     UNCLASSIFIED = "unclassified"

#     REST_TEXT = "restText"
#     LYRICS_TEXT = "lyricsText"
#     VERSE_NUMBER = "verseNumber"
#     DYNAMICS_TEXT = "dynamicsText"
#     INTERPRETATION_TEXT = "interpretationText"
#     METADATA_TEXT = "metadataText"
#     MEASURE_NUMBER = "measureNumber"
#     PAGE_NUMBER = "pageNumber"
#     OTHER_TEXT = "otherText"

#     TEMPO_TEXT = "tempoText"
#     TEMPO_RITARDANDO = "tempoRitardando"
#     TEMPO_ACCELERANDO = "tempoAccelerando"
#     TEMPO_A_TEMPO = "tempoATempo"

#     @staticmethod
#     def rest_name_to_duration(rest_name: str) -> Fraction:
#         """
#         Returns the duration of a rest as a fraction based on a rest name.

#         :param rest_name: The rest class name.
#         :return: The duration of the rest as a Fraction.
#         """
#         C = ClassNamesConstants
#         _LOOK_UP = {
#             C.REST_LONGA: Fraction(16, 1),  # !!! We should find the Time Signature.
#             C.REST_DOUBLE_WHOLE: Fraction(
#                 8, 1
#             ),  # !!! We should find the Time Signature.
#             C.REST_WHOLE: Fraction(4, 1),  # !!! We should find the Time Signature.
#             C.REST_HALF: Fraction(2, 1),
#             C.REST_QUARTER: Fraction(1, 1),
#             C.REST_8TH: Fraction(1, 2),
#             C.REST_16TH: Fraction(1, 4),
#             C.REST_32ND: Fraction(1, 8),
#             C.REST_64TH: Fraction(1, 16),
#             # Technically, these two should just apply time sig.,
#             # but the measure-factorized precedence graph
#             # means these durations never have sounding
#             # descendants anyway:
#             C.REST_H_BAR: Fraction(4, 1),
#             C.REPEAT_ONE_BAR: Fraction(4, 1),
#         }
#         duration = _LOOK_UP.get(rest_name, None)
#         if duration is None:
#             raise ValueError(f'Unknown rest name "{rest_name}"')
#         return duration

#     @staticmethod
#     def all_class_names() -> list[str]:
#         """
#         Returns all class names defined in this class.
#         """
#         return [
#             value
#             for key, value in vars(ClassNamesConstants).items()
#             if isinstance(value, str) and not key.startswith("_")
#         ]
