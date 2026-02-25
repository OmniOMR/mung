from dataclasses import dataclass, field

from ...graph import ClefSign
from mung import __version__ as LIBRARY_VERSION


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
    """ """

    default_time_signature: int = -1
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
