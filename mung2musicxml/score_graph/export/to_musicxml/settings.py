from dataclasses import dataclass, field

from ...graph import ClefSign
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

    canonical_time_sigs: list[TimeSigStruct] = field(default_factory=lambda: [
        TimeSigStruct(2, 3),
        TimeSigStruct(4, 4),
        TimeSigStruct(3, 4),
        TimeSigStruct(2, 4),
        TimeSigStruct(9, 8),
        TimeSigStruct(3, 2),
        TimeSigStruct(5, 4),
        TimeSigStruct(7, 8),
    ])
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
class MusicXMLExportSettings:
    musicxml_version: str = "4.0"
    software_name: str = f"MuNGv{LIBRARY_VERSION}"
    indent: int | str = 2
    first_voices: set[int] = field(default_factory=lambda: {1, 5})
    credit: CreditSettings = field(default_factory=CreditSettings)
    clefs: ClefSettings = field(default_factory=ClefSettings)
    time_sig: TimeSignatureSettings = field(default_factory=TimeSignatureSettings)
