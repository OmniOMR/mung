from mung import Node

from ...graph import *
from ....logger import logger


def try_match_dynamics(mung_dynamics: Node) -> DynamicsTypeToken:
    transcription = mung_dynamics.text_transcription
    assert transcription is not None

    for token in DynamicsTypeToken:
        if transcription == token:
            return token
    else:
        return DynamicsTypeToken.OTHER_DYNAMICS


def construct_dynamics(mung_dynamics: Node, subs: set[Subevent]) -> Dynamics:
    if any(s.global_fractional_onset != next(iter(subs)).global_fractional_onset for s in subs):
        logger.warning(f"Subevents linked to {mung_dynamics} differ in onsets, choosing the first one")
    
    sub = min(subs, key=lambda s: (s.global_fractional_onset, s.voice))
    type_ = try_match_dynamics(mung_dynamics)
    if type_ != DynamicsTypeToken.OTHER_DYNAMICS:
        return Dynamics(sub, type_)
    else:
        return Dynamics(sub, type_, mung_dynamics.text_transcription)
