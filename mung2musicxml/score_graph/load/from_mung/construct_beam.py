from mung import Node

from ...graph import *


def construct_durable_beam(mung_beam: Node, subevents: list[Subevent]) -> Beam:
    assert len(subevents) > 0, f"No subevents for {mung_beam}"
    subevents.sort(key=lambda s: s.global_fractional_onset)
    try:
        if len(subevents) == 1:
            return Beam(
                start=subevents[0]
            )
        elif len(subevents) == 2:
            return Beam(
                start=subevents[0],
                stop=subevents[1]
            )
        else:
            return Beam(
                start=subevents[0],
                continue_=subevents[1:-1],
                stop=subevents[-1]
            )
    except Exception as e:
        raise ValueError(f"Failed to construct {Beam.__name__} for node {mung_beam} for {subevents}") from e
    