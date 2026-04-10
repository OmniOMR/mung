from mung import Node, NotationGraph
from mung.constants import ClassNameConstants as C

from ...graph import *


def construct_dots_for_durable_like(mung_durable: Node, durable: Durable | GraceNote, graph: NotationGraph) -> None:
    dots = graph.children(mung_durable, class_filter=C.NoteheadAttachments.AUGMENTATION_DOT)
    for _ in dots:
        Dot(durable=durable)