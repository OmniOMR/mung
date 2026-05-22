from dataclasses import dataclass, field
from typing import TypeVar, Optional
from functools import cached_property
from abc import ABC, abstractmethod

from .scene_object import SceneObject
from .subevent import Subevent
from .grace_note import GraceNote
from .tokens import BeamValueToken
from .interface import GenericStartStopContinue
from .interface import InMeasureObject
from ...logger import logger

T = TypeVar("T", bound=InMeasureObject)


@dataclass
class GenericBeam(GenericStartStopContinue[T], ABC):
    """
    Beam between one and more Subevents.

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/beam/
    """
    _beam_value_mapping: dict[T, BeamValueToken] = field(init=False, repr=False)

    def __post_init__(self):
        super().__post_init__()
        self._check_start_is_set()
        self._check_continue_onset_strong()
        self._beam_value_mapping = self._compute_beam_values()

    def _check_onsets(self) -> None:
        onsets = [s.in_measure_fractional_onset for s in self.all]
        assert len(onsets) == len(set(onsets)), f"Onsets for all subevents inside beam must differ, {onsets}"
    
    @abstractmethod
    def _get_start_beams(self) -> list:
        pass

    def _compute_beam_values(self) -> dict[T, BeamValueToken]:
        assert self.start is not None

        logger.debug(f"Computing beam values for {self}")
        mapping: dict[T, BeamValueToken] = {}
        # only start
        if self.is_hook:
            # get all beams that are connected to the same subevent
            # as this beam,
            # based on direction of other
            begins = 0
            ends = 0
            for b in self._get_start_beams():
                if not b.is_hook:
                    if b.is_start(self.start):
                        begins += 1
                    elif b.is_stop(self.start):
                        ends += 1
            
            # more starts
            #  -> forward hook
            # more ends
            #  -> backward hook
            # same count (both can be zero)
            #  -> default hook (forward hook)
            
            if begins > ends:
                mapping[self.start] = BeamValueToken.FORWARD_HOOK
            elif ends > begins:
                mapping[self.start] = BeamValueToken.BACKWARD_HOOK
            else:
                mapping[self.start] = BeamValueToken.default_hook()
        
        # is not hook, has all three values
        else:
            assert self.stop is not None
            mapping[self.start] = BeamValueToken.BEGIN
            mapping[self.stop] = BeamValueToken.END
            if self.continue_ is not None:
                for s in self.continue_:
                    mapping[s] = BeamValueToken.CONTINUE
        
        return mapping
    
    def _compute_number(self) -> int:
        assert self.start is not None
        beams = sorted(self._get_start_beams(), key=lambda b: (len(b), id(b)), reverse=True)
        return beams.index(self) + 1 # MuseScore indexes from 1

    @cached_property
    def number(self) -> str:
        return str(self._compute_number())

    @property
    def is_hook(self) -> bool:
        return len(self.all) == 1

    def beam_value(self, obj: T) -> BeamValueToken:        
        value = self._beam_value_mapping.get(obj)
        if value is None:
            raise ValueError("Durable has no link to this beam")
        
        return value

@dataclass
class DurableBeam(GenericBeam[Subevent]):
    def _get_start_beams(self) -> list:
        assert self.start is not None
        return self.start.beams


@dataclass
class GraceNoteBeam(SceneObject):
    begin: GraceNote
    end: Optional[GraceNote] = None
    continue_: Optional[list[GraceNote]] = None
    all_grace_notes: list[GraceNote] = field(init=False, repr=False)
    _beam_value_mapping: dict[GraceNote, BeamValueToken] | None = field(init=False, repr=False, default=None)

    def __post_init__(self):
        # assert types
        assert isinstance(self.begin, GraceNote)
        assert self.end is None or isinstance(self.end, GraceNote)
        assert self.continue_ is None or all(isinstance(x, GraceNote) for x in self.continue_)
        
        # assert continue is None or at least one element
        assert self.continue_ is None or len(self.continue_) > 0, f"{self.continue_=} has to be None or list with at least one element"
        
        self.all_grace_notes = self._collect()
        self._check_onsets()
        self._beam_value_mapping = None

    def _check_onsets(self) -> None:
        if not isinstance(self.begin, Subevent):
            return
        onsets = [s.at_durable_index for s in self.all_grace_notes]
        assert len(onsets) == len(set(onsets)), f"Onsets for all subevents inside beam must differ, {onsets}"

    def _collect(self) -> list[GraceNote]:
        output: list[GraceNote] = [self.begin]
        if self.continue_ is not None:
            output += self.continue_
        if self.end is not None:
            output.append(self.end)
        return output
    
    def __len__(self) -> int:
        return len(self.all_grace_notes)
    
    def is_begin(self, grace: GraceNote) -> bool:
        return self.begin == grace
    
    def is_end(self, grace: GraceNote) -> bool:
        if self.end is None:
            return False
        
        return self.end == grace
    
    def is_continue(self, grace: GraceNote) -> bool:
        if self.continue_ is None:
            return False
        
        return grace in self.continue_

    def _compute_beam_values(self) -> dict[GraceNote, BeamValueToken]:
        logger.debug(f"Computing beam values for {self}")

        mapping: dict[GraceNote, BeamValueToken] = {}
        # only start, only one grace note
        if self.is_hook:
            mapping[self.begin] = BeamValueToken.default_hook()
        
        # is not hook, has all three values
        else:
            assert self.end is not None
            mapping[self.begin] = BeamValueToken.BEGIN
            mapping[self.end] = BeamValueToken.END
            if self.continue_ is not None:
                for s in self.continue_:
                    mapping[s] = BeamValueToken.CONTINUE
        
        return mapping
    
    def _compute_number(self) -> int:
        beams = sorted(self.begin.beams, key=lambda b: (len(b), id(b)), reverse=True)
        return beams.index(self) + 1 # MuseScore indexes from 1

    @cached_property
    def number(self) -> str:
        return str(self._compute_number())

    @property
    def is_hook(self) -> bool:
        return len(self.all_grace_notes) == 1

    def beam_value(self, grace: GraceNote) -> BeamValueToken:
        if self._beam_value_mapping is None:
            self._beam_value_mapping = self._compute_beam_values()
        
        value = self._beam_value_mapping.get(grace)
        if value is None:
            raise ValueError("Durable has no link to this beam")
        
        return value
