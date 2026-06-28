from dataclasses import dataclass

from .score_measure import ScoreMeasure
from .interface import GenericStartStop


@dataclass(kw_only=True)
class Volta(GenericStartStop[ScoreMeasure]):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/examples/ending-element/
    """

    text: str
    numbers: list[int]

    def _t_lt(self, first: ScoreMeasure, second: ScoreMeasure) -> bool:
        return first.id < second.id

    def __post_init__(self) -> None:
        super().__post_init__()
        self._check_start_is_set()
        self._check_stop_is_set()
