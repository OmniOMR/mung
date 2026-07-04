from dataclasses import dataclass
from .interface import GenericStartStopContinueOnset
from .subevent import Subevent
from .tokens import AboveBelowToken, OctaveShiftType
from .staff import Staff


@dataclass(kw_only=True)
class Ottava(GenericStartStopContinueOnset[Subevent]):
    start: Subevent  # type: ignore
    stop: Subevent  # type: ignore
    placement: AboveBelowToken
    direction: OctaveShiftType
    size: int

    def __post_init__(self) -> None:
        super().__post_init__()
        self._check_start_is_set()
        self._check_stop_is_set()
        assert self.size in {8, 15, 22}

    @property
    def staffs(self) -> list[Staff]:
        staffs: set[Staff] = set()
        for s in self.all:
            staffs.update(s.staffs)
        return list(staffs)

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other
