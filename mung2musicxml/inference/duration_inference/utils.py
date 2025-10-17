from fractions import Fraction

from mung import  Node
from mung.constants import OnsetDataConstants as O


def _add_duration_data_to_node(
    node: Node, duration: Fraction, duration_wo_m: Fraction
):
    node.data[O.DURATION_BEATS] = duration
    node.data[O.DURATION_BEATS_WO_M] = duration_wo_m
