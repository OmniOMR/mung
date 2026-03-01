from dataclasses import dataclass, field
from typing import Optional

from .tokens import AboveBelowToken, ShowTupleToken, YesNoToken
from .time_modification import TimeModification
from .interface import GenericStartStopContinue
from .subevent import Subevent


# TODO: add support for nested tuplets
@dataclass(kw_only=True)
class Tuplet(GenericStartStopContinue[Subevent]):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/tuplet/
    """
    time_modification: TimeModification

    placement: Optional[AboveBelowToken] = field(default=AboveBelowToken.default())
    show_number: ShowTupleToken = field(default=ShowTupleToken.default())
    bracket: YesNoToken = field(default=YesNoToken.YES)

    def __post_init__(self) -> None:
        super().__post_init__()
        self._check_continue_onset_strong()
        self._check_start_is_set()
        self._check_stop_is_set()
        self._check_start_stop_onset_strong()
        