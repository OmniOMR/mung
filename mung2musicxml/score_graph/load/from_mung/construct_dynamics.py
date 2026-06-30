from mung import Node, NotationGraph
from mung.graph import infer_vertical_object_placement_relative_to_notes

from ...graph import *
from ....logger import logger
from .collector import needs_graph


def try_match_dynamics(mung_dynamics: Node) -> DynamicsTypeToken:
    transcription = mung_dynamics.text_transcription
    assert transcription is not None

    for token in DynamicsTypeToken:
        if transcription == token:
            return token
    else:
        return DynamicsTypeToken.OTHER_DYNAMICS


@needs_graph
def construct_dynamics(mung_dynamics: Node, subs: list[Subevent], graph: NotationGraph) -> Dynamics:
    if any(s.global_fractional_onset != next(iter(subs)).global_fractional_onset for s in subs):
        logger.warning(f"Subevents linked to {mung_dynamics} differ in onsets, choosing the first one")
    
    sub = min(subs, key=lambda s: (s.global_fractional_onset, s.voice))
    type_ = try_match_dynamics(mung_dynamics)

    placement = AboveBelowToken.from_int(
        infer_vertical_object_placement_relative_to_notes(mung_dynamics, graph)
    )
    if type_ != DynamicsTypeToken.OTHER_DYNAMICS:
        return Dynamics(sub, type_, placement)
    else:
        return Dynamics(sub, type_, placement, mung_dynamics.text_transcription)
