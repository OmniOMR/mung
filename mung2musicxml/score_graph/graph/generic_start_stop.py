from dataclasses import dataclass, field
from typing import Optional

from .scene_object import SceneObject
from .subevent import Subevent


@dataclass
class GenericStartStop(SceneObject):
    start: Optional[Subevent] = None
    # Subevents included in the object that are not `start` nor `stop`
    continue_: Optional[list[Subevent]] = None
    stop: Optional[Subevent] = None

    all_subevents: list[Subevent] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Automatically checks that::
        - Start or stop is set.
        - Onset of start is less than or equal to onset of stop.
        - Onsets of `continue_`, if set, 
            are greater than or equal to onset of start
            and less than or equal to onset of stop.
        - `continue_` is None or not empty.
        """
        self._check_any_is_set()
        self._check_continue_onset()
        self._check_continue_onset()
        self._check_continue_none_or_not_empty()
        self.all_subevents = self._collect()

    def _collect(self) -> list[Subevent]:
        output: list[Subevent] = []
        if self.start is not None:
            output.append(self.start)
        if self.continue_ is not None:
            output.extend(self.continue_)
        if self.stop is not None:
            output.append(self.stop)
        return list(set(output))

    def _check_continue_onset(self) -> None:
        """
        If start, stop and continue are set,
        checks that every value in continue has
        onset in interval [start.onset, stop.onset].
        """
        if self.continue_ is not None:
            assert self.start is not None and self.stop is not None, "Cannot have 'continue_' set and both 'start', 'stop' set to None"
            for d in self.continue_:
                if not (self.start.global_fractional_onset
                    <= d.global_fractional_onset
                    <= self.stop.global_fractional_onset
                ):
                    raise ValueError(f"Onset {d.global_fractional_onset} of {d} not in allowed range: {self.start.global_fractional_onset} <= x <= {self.stop.global_fractional_onset}]")
    
    def _check_continue_onset_strong(self) -> None:
        """
        If start, stop and continue are set,
        checks that every value in continue has
        onset in interval (start.onset, stop.onset).
        (Strong inequality.)
        """
        if self.continue_ is not None:
            assert self.start is not None and self.stop is not None, "Cannot have 'continue_' set and both 'start', 'stop' set to None"
            for d in self.continue_:
                if not (self.start.global_fractional_onset
                    < d.global_fractional_onset
                    < self.stop.global_fractional_onset
                ):
                    raise ValueError(f"Onset of {d} not in allowed range: {self.start.global_fractional_onset} < {d.global_fractional_onset} < {self.stop.global_fractional_onset}]")
    
    def _check_any_is_set(self) -> None:
        assert self.start is not None or self.stop is not None, "At least one of 'start', 'stop' has to be set"
    
    def _check_start_is_set(self) -> None:
        assert self.start is not None, f"{type(self).__name__} requires 'start' to be set"
    
    def _check_stop_is_set(self) -> None:
        assert self.stop is not None, f"{type(self).__name__} requires 'stop' to be set"
    
    def _check_start_stop_onset(self) -> None:
        if self.start is not None and self.stop is not None:
            assert self.start.global_fractional_onset <= self.stop.global_fractional_onset
    
    def _check_start_stop_onset_strong(self) -> None:
        if self.start is not None and self.stop is not None:
            assert self.start.global_fractional_onset < self.stop.global_fractional_onset
    
    def _check_continue_none_or_not_empty(self) -> None:
        if self.continue_ is not None:
            assert len(self.continue_) > 0, "'continue_' cannot be set and empty"

    def is_start(self, subevent: Subevent) -> bool:
        if self.start is None:
            return False
        return self.start == subevent
    
    def is_stop(self, subevent: Subevent) -> bool:
        if self.stop is None:
            return False
        return self.stop == subevent
    
    def is_continue(self, subevent: Subevent) -> bool:
        if self.continue_ is None:
            return False
        return subevent in self.continue_
