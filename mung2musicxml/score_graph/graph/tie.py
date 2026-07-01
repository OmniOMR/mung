from dataclasses import dataclass

from .durable import Durable
from .note import Note
from .tokens import AboveBelowToken
from .interface import GenericStartStopOnset


@dataclass(kw_only=True)
class Tie(GenericStartStopOnset[Durable]):
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
            if self.start.global_fractional_end_onset != self.stop.global_fractional_onset:
                raise ValueError(
                    "Start durable has to end on the same onset at which the stop durable starts, "
                    f"start durable end onset: {self.start.global_fractional_end_onset}, stop durable start onset: {self.stop.global_fractional_onset}, "
                    f"start: {self.start}, stop: {self.stop}"
                )
        if isinstance(self.start, Note) and isinstance(self.stop, Note):
            assert self.start.pitch == self.stop.pitch
        
    @property
    def is_let_ring(self) -> bool:
        return len(self) == 1
    