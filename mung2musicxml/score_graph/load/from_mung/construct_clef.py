from mung import Node, NotationGraph
from mung.constants import ClassNameConstants as C

from ...graph import *
from .utils import onset_beats, find_line_index_for_clef

def construct_clef(mung_clef: Node, graph: NotationGraph) -> Clef:
    return Clef(
        fractional_onset_=onset_beats(mung_clef),
        sign=_get_clef_sign(mung_clef.class_name),
        line=find_line_index_for_clef(mung_clef, graph)
    )


def _get_clef_sign(class_name: str) -> ClefSign:
    _LOOKUP: dict[str, ClefSign] = {
        C.Clefs.C_CLEF : ClefSign.C,
        C.Clefs.F_CLEF : ClefSign.F,
        C.Clefs.G_CLEF : ClefSign.G,
    }
    return _LOOKUP[C.Clefs.simplify(class_name)]
