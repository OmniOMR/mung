from fractions import Fraction
from mung import Node, NotationGraph
from mung.constants import InferenceEngineConstants as I

from ...graph import *
from ....logger import logger
from .construct_accidental import construct_accidental_for_key


def construct_key_signature(
        key_signature: Node,
        onset: Fraction,
        graph: NotationGraph
) -> Key:
    """
    Constructs key signature.
    """
    key = Key(onset)

    for acc in graph.children(key_signature, class_filter=I.ACCIDENTAL_CLASS_NAMES):
        construct_accidental_for_key(acc, key)
    
    return key