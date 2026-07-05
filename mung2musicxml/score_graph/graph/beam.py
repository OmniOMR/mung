from dataclasses import dataclass, field

from .subevent import Subevent
from .tokens import BeamValueToken
from .interface import GenericStartStopContinueOnset
from ...logger import logger


@dataclass
class Beam(GenericStartStopContinueOnset[Subevent]):
    """
    Beam between one and more Subevents.

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/beam/
    """

    _beam_value_mapping: dict[Subevent, BeamValueToken] = field(init=False, repr=False)

    def __post_init__(self):
        super().__post_init__()
        self._check_start_is_set()
        self._check_continue_onset_strong()
        self._beam_value_mapping = self._compute_beam_values()

    def _check_onsets(self) -> None:
        onsets = [s.in_measure_fractional_onset for s in self.all]
        assert len(onsets) == len(
            set(onsets)
        ), f"Onsets for all subevents inside beam must differ, {onsets}"

    def _get_start_beams(self) -> list:
        assert self.start is not None
        return self.start.beams

    def _compute_beam_values(self) -> dict[Subevent, BeamValueToken]:
        assert self.start is not None

        logger.debug(f"Computing beam values for {self}")
        mapping: dict[Subevent, BeamValueToken] = {}
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

    @property
    def is_hook(self) -> bool:
        return len(self.all) == 1

    def beam_value(self, obj: Subevent) -> BeamValueToken:
        value = self._beam_value_mapping.get(obj)
        if value is None:
            raise ValueError("Durable has no link to this beam")

        return value

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other
