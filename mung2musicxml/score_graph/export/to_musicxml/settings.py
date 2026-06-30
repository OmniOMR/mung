from dataclasses import dataclass, field
from typing import Type

from ...graph import (
    ClefSign,
    SceneObject,
    WordsAttributes,
    Tempo,
    DynamicsText,
    FontStyleToken,
    FontWeightToken,
    RestText,
)
from mung import __version__ as LIBRARY_VERSION
from mung.interpret import TimeSigStruct


PMCG_CREDIT = "Exported using the MuNG Python library.\nDeveloped and maintained by the Prague Music Computing Group (PMCG)."


@dataclass
class CreditSettings:
    """
    Stores credit text and if it appears in the output.
    """

    text: str = field(default=PMCG_CREDIT)
    show: bool = True


@dataclass
class TimeSignatureSettings:
    """
    If no time signatures are found, the engine
    tries to match durations of measures
    to one of the `canonical_time_sigs`
    """

    canonical_time_sigs: list[TimeSigStruct] = field(
        default_factory=lambda: [
            TimeSigStruct(2, 3),
            TimeSigStruct(4, 4),
            TimeSigStruct(3, 4),
            TimeSigStruct(2, 4),
            TimeSigStruct(9, 8),
            TimeSigStruct(3, 2),
            TimeSigStruct(5, 4),
            TimeSigStruct(7, 8),
        ]
    )
    default_time_signature: TimeSigStruct = field(default=TimeSigStruct(4, 4))
    fallback_to_default_time_signature: bool = False


@dataclass
class ClefSettings:
    fallback_to_default_clefs: bool = True
    default_clefs_by_staff_index: dict[int, tuple[ClefSign, int]] = field(
        default_factory=lambda: {
            # for grand staff
            # top staff
            1: (ClefSign.G, 2),
            # bottom staff
            2: (ClefSign.G, 2),
        }
    )


@dataclass
class ErrorHandlingSettings:
    skip_broken_measure: bool = False


@dataclass
class MusicXMLExportSettings:
    musicxml_version: str = "4.0"
    software_name: str = f"MuNGv{LIBRARY_VERSION}"
    indent: int | str = 2
    first_voices: set[int] = field(default_factory=lambda: {1, 5})
    credit: CreditSettings = field(default_factory=CreditSettings)
    clefs: ClefSettings = field(default_factory=ClefSettings)
    time_sig: TimeSignatureSettings = field(default_factory=TimeSignatureSettings)
    error_handling: ErrorHandlingSettings = field(default_factory=ErrorHandlingSettings)
    text_settings: dict[Type[SceneObject], WordsAttributes] = field(
        default_factory=lambda: {
            Tempo: WordsAttributes(font_weight=FontWeightToken.BOLD, font_size=12),
            DynamicsText: WordsAttributes(
                font_family="Edwin", font_style=FontStyleToken.ITALIC, font_size=10
            ),
            RestText: WordsAttributes(font_weight=FontWeightToken.BOLD, font_size=12),
        }
    )
    use_mss4_compatible_repeat_barline_style: bool = True
