from dataclasses import dataclass

from .durable import Durable
from .note import Note
from .tokens import AboveBelowToken
from .interface import GenericStartStop


@dataclass(kw_only=True)
class Tie(GenericStartStop[Durable]):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/tied/

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/tie/
    """
    placement: AboveBelowToken

    def __post_init__(self):
        super().__post_init__()
        self._check_start_is_set()
        self._check_start_stop_onset_strong()
        
        assert self.start is not None
        if self.stop is not None:
            assert self.start.in_measure_fractional_end_onset == self.stop.in_measure_fractional_onset
        if isinstance(self.start, Note) and isinstance(self.stop, Note):
            assert self.start.pitch == self.stop.pitch
        
    @property
    def is_let_ring(self) -> bool:
        return len(self) == 1
    