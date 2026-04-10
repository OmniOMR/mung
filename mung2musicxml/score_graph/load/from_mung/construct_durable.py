from collections import defaultdict
from mung import Node, NotationGraph
from mung.constants import (
    ClassNameConstants as C,
    InferenceEngineConstants as I
)

from ...graph import *
from ....logger import logger
from .utils import pitch, duration_beats, duration_beats_w_m, onset_beats
from .construct_note import construct_note
from .construct_rest import construct_rest
from .construct_repeat import construct_repeat


def construct_durable(durable: Node, graph: NotationGraph) -> Note | Rest | RepeatBar:
    
    if durable.class_name in I.NONGRACE_NOTEHEAD_CLASS_NAMES:
        return construct_note(durable, graph)
    
    elif durable.class_name in I.REST_CLASS_NAMES:
        return construct_rest(durable, graph)
    
    elif durable.class_name == C.Repeat.REPEAT_1_BAR:
        logger.info(f"Constructing {RepeatBar.__name__} based on {durable}")
        return construct_repeat(durable, graph)
    
    raise ValueError(f"Unknown durable type: {durable}")
