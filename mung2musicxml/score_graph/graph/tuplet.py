from dataclasses import dataclass, field

from .tokens import AboveBelowToken, ShowTupleTokens, YesNoToken
from .time_modification import TimeModification
from .generic_start_stop import GenericStartStop


# TODO: supports only simple (not nested) tuplets
@dataclass(kw_only=True)
class Tuplet(GenericStartStop):
    time_modification: TimeModification

    placement: AboveBelowToken = field(default=AboveBelowToken.default())
    show_number: ShowTupleTokens = field(default=ShowTupleTokens.default())
    bracket: YesNoToken = field(default=YesNoToken.YES)

    def __post_init__(self) -> None:
        super().__post_init__()
        self._check_continue_onset_strong()
        self._check_start_is_set()
        self._check_stop_is_set()
        self._check_start_stop_onset_strong()
        
        assert not (self.placement != AboveBelowToken.NONE and self.bracket == YesNoToken.NO)
