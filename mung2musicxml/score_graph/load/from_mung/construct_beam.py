from mung import Node

from ...graph import *


def construct_durable_beam(mung_beam: Node, subevents: list[Subevent]) -> DurableBeam:
    assert len(subevents) > 0, f"No subevents for {mung_beam}"
    subevents.sort(key=lambda s: s.global_fractional_onset)
    try:
        if len(subevents) == 1:
            return DurableBeam(
                start=subevents[0]
            )
        elif len(subevents) == 2:
            return DurableBeam(
                start=subevents[0],
                stop=subevents[1]
            )
        else:
            return DurableBeam(
                start=subevents[0],
                continue_=subevents[1:-1],
                stop=subevents[-1]
            )
    except Exception as e:
        raise ValueError(f"Failed to construct {DurableBeam.__name__} for node {mung_beam} for {subevents}") from e
    