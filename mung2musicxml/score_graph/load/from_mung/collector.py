from enum import StrEnum
from typing import Type, Optional
from collections import defaultdict
from dataclasses import dataclass, field

from mung import Node, NotationGraph
from ...graph.scene_object import SceneObject
from ...graph import Subevent


@dataclass
class CollectorRecord:
    type_: Type[SceneObject]
    class_names: set[str | StrEnum] | list[str | StrEnum] | str | StrEnum
    found_nodes: list[Node] = field(default_factory=list)
    subevents_by: defaultdict[Node, set[Subevent]] = field(
        default_factory=lambda: defaultdict(set)
    )

    def _reset_found(self) -> None:
        self.found_nodes.clear()


class SubeventCollector:
    """
    Temporarily gives links large objects in a MuNG score
    (slurs, beams, ...) to Score Graph Subevents.
    """
    def __init__(self, records: Optional[list[CollectorRecord]] = None) -> None:
        self._records: list[CollectorRecord] = records if records is not None else []
        self._index: dict[Type[SceneObject], CollectorRecord] = {
            r.type_: r for r in self._records
        }

    def collect_nodes(self, node: Node, graph: NotationGraph):
        """
        Collects all objects specified in records that are children
        of `node`.
        """
        for rec in self._records:
            found = graph.children(node, class_filter=rec.class_names)
            rec.found_nodes.extend(found)

    def add_subevent(self, subevent: Subevent) -> None:
        """
        Registers `subevent` to all found objects.
        """
        for rec in self._records:
            for node in rec.found_nodes:
                rec.subevents_by[node].add(subevent)
            rec._reset_found()

    def subevents_by(self, type_: Type[SceneObject]) -> dict[Node, set[Subevent]]:
        """
        Retrieve all objects linked to a subevent by the objects type.
        """
        return self._index[type_].subevents_by
