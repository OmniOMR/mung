from dataclasses import dataclass

from .generic_start_stop import GenericStartStop
from ..subevent import Subevent
from ..tokens import AboveBelowToken
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..staff import Staff


@dataclass(kw_only=True)
class ScoreText(GenericStartStop[Subevent]):
    """
    Represents text that can span over multiple durables.
    """

    text: str
    placement: AboveBelowToken

    def __post_init__(self) -> None:
        super().__post_init__()
        self._check_start_is_set()
        self._check_start_stop_onset_strong()
        assert len(self.text) > 0

    @property
    def staff(self) -> "Staff":
        assert self.start is not None
        return min(self.start.staffs, key=lambda s: s.id)
