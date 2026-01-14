from typing import Sequence, Self, Generator, Optional
from fractions import Fraction

from mung import Node, NotationGraph
from mung.constants import (
    OnsetDataConstants as O,
    ClassNamesConstants as C,
)
from ...inference import Pitch, PitchDataConstants
from ...utils import flatten


class _Subevent:
    """
    Represents durables that are played at the same time
    and are in chord together.
    """
    def __init__(self, nodes: Sequence[Node]) -> None:
        self.nodes = frozenset(nodes)
    
    def __iter__(self) -> Generator[Node, None, None]:
        return (n for n in self.nodes)
    
    def __len__(self) -> int:
        return len(self.nodes)

    def is_parent_of(self, child: Self, graph: NotationGraph) -> bool:
        ids: set[int] = set(x.id for x in child)

        for p_node in self:
            p_node: Node
            if any(graph.is_precedence_parent_of(p_node, id_) for id_ in ids):
                return True

        return False

    def get_neighbors(self, others: list[Self], graph: NotationGraph) -> list[Self]:
        output = []
        for o in others:
            if self.is_parent_of(o, graph):
                output.append(o)
        return output
    
    def get_start_onset(self) -> Fraction:
        return next(iter(self)).data[O.ONSET_BEATS]
    
    def get_end_onset(self) -> Fraction:
        return self.get_start_onset() + self.get_duration()

    def get_priority(self) -> int:
        """
        Computes the priority as mean vertical coordinate.
        """
        return sum(e.vertical_center for e in self) // len(self)
    
    def get_duration(self) -> Fraction:
        return max([e.data[O.DURATION_BEATS] for e in self])
    
    def get_pitches(self) -> list[Pitch]:
        return [p for x in self if (p := x.data.get(PitchDataConstants.PITCH)) is not None]
    
    def __repr__(self) -> str:
        return f"Subevent({[x.id for x in self]})"

    def get_any(self, graph: NotationGraph, class_name: str) -> Optional[Node]:
        """
        Returns the first found beam linked to any of the durables inside the subevent.
        """
        for s in self:
            beams = graph.children(s, class_filter=class_name)
            if len(beams) > 0:
                return beams[0]
        return None
        
    def get_staff(self, graph: NotationGraph) -> Node:
        """
        Returns the topmost staff linked to any of the durables inside the subevent.
        """
        staffs = flatten(graph.children(n, class_filter=C.STAFF) for n in self)
        staffs.sort(key=lambda s: s.top)
        return staffs[0]
    