from dataclasses import dataclass, field
from typing import ClassVar

from .subevent import Subevent
from .time_modification import TimeModification
from .interface import GenericStartStop


@dataclass(kw_only=True)
class TremoloBeam(GenericStartStop[Subevent]):
    """
    Equivalent to MusicXML Tremolo Double.

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/tremolo/
    """
    marks: int
    all_subevents: list[Subevent] = field(init=False)
    time_modification: ClassVar[TimeModification] = TimeModification(2, 1)

    def __post_init__(self) -> None:
        super().__post_init__()
        self._check_start_is_set()
        self._check_stop_is_set()
        self._check_start_stop_onset_strong()
    