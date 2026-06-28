from dataclasses import dataclass, field
from abc import abstractmethod, ABC
from typing import Optional
from typing import TypeVar, Generic

from ..scene_object import SceneObject
from . import InMeasureObject

T = TypeVar("T")


@dataclass
class GenericStartStop(SceneObject, Generic[T], ABC):
    start: Optional[T] = None
    stop: Optional[T] = None
    all: list[T] = field(init=False, repr=False)
    
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
        self._check_start_or_stop_is_set()
        self._check_start_stop_onset()
        self.all = self._collect()
    
    @abstractmethod
    def _t_lt(self, first: T, second: T) -> bool:
        """
        Compare two generic objects.
        """
        pass
    
    def _t_eq(self, first: T, second: T) -> bool:
        return not self._t_lt(first, second) and not self._t_lt(second, first)
    
    def _t_leq(self, first: T, second: T) -> bool:
        return self._t_lt(first, second) or self._t_eq(first, second)

    def __len__(self) -> int:
        return len(self.all)
    
    def _collect(self) -> list[T]:
        output: list[T] = []
        if self.start is not None:
            output.append(self.start)
        if self.stop is not None:
            output.append(self.stop)
        return list(set(output))
    
    def _check_start_or_stop_is_set(self) -> None:
        assert self.start is not None or self.stop is not None, "At least one of 'start', 'stop' has to be set"
    
    def _check_start_is_set(self) -> None:
        assert self.start is not None, f"{type(self).__name__} requires 'start' to be set"
    
    def _check_stop_is_set(self) -> None:
        assert self.stop is not None, f"{type(self).__name__} requires 'stop' to be set"
    
    def _check_start_stop_onset(self) -> None:
        if self.start is not None and self.stop is not None:
            assert self._t_leq(self.start, self.stop)
    
    def _check_start_stop_onset_strong(self) -> None:
        if self.start is not None and self.stop is not None:
            assert self._t_lt(self.start, self.stop)
    
    def is_start(self, subevent: T) -> bool:
        """
        Returns true, if the given `subevent`
        is start of this object.
        """
        if self.start is None:
            return False
        return self.start == subevent
    
    def is_stop(self, subevent: T) -> bool:
        """
        Returns true, if the given `subevent`
        is stop of this object.
        """
        if self.stop is None:
            return False
        return self.stop == subevent
    
    @property
    def has_start_and_stop_set(self) -> bool:
        """
        True, if both start and stop
        are set.
        """
        return (
            self.start is not None
            and self.stop is not None
        )

M = TypeVar("M", bound=InMeasureObject)


@dataclass
class GenericStartStopOnset(GenericStartStop[M]):
    start: Optional[M] = None
    stop: Optional[M] = None
    all: list[M] = field(init=False, repr=False)
    
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
        self._check_start_or_stop_is_set()
        self._check_start_stop_onset()
        self.all = self._collect()

    def __len__(self) -> int:
        return len(self.all)
    
    def _t_lt(self, first: M, second: M) -> bool:
        return first.global_fractional_onset < second.global_fractional_onset
    

@dataclass
class GenericStartStopContinueOnset(GenericStartStopOnset[M]):
    # objects included in the object that are not `start` nor `stop`
    continue_: Optional[list[M]] = None

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
        super().__post_init__()
        self._check_continue_none_or_not_empty()
        self._check_continue_onset()

    def _collect(self) -> list[M]:
        output: list[M] = []
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
    
    def _check_start_stop_onset_strong(self) -> None:
        if self.start is not None and self.stop is not None:
            assert self.start.global_fractional_onset < self.stop.global_fractional_onset
    
    def _check_continue_none_or_not_empty(self) -> None:
        if self.continue_ is not None:
            assert len(self.continue_) > 0, "'continue_' cannot be set and empty"

    def is_continue(self, subevent: T) -> bool:        
        """
        Returns true, if the given `subevent`
        is continue of this object.
        """
        if self.continue_ is None:
            return False
        return subevent in self.continue_
