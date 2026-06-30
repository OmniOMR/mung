from enum import StrEnum
from contextlib import contextmanager
from typing import Type, Optional, Callable, TypeAlias
from collections import defaultdict
from dataclasses import dataclass, field

from mung import Node, NotationGraph
from ...graph.scene_object import SceneObject
from ...graph import Subevent
from ....logger import logger
from .utils import _log_object_creation


SOConstructor: TypeAlias = (
    Callable[
        [Node, list[Subevent], NotationGraph], list[SceneObject] | SceneObject | None
    ]
    | Callable[[Node, list[Subevent]], list[SceneObject] | SceneObject | None]
    | Callable[[Node, Subevent, NotationGraph], list[SceneObject] | SceneObject | None]
    | Callable[[Node, Subevent], list[SceneObject] | SceneObject | None]
)


@contextmanager
def _construction_guard(mung_obj: Node, type_: type, critical: bool = False):
    result = None
    try:
        yield result
        if result is not None:
            _log_object_creation(result, mung_obj)
    except Exception as e:
        if not critical:
            logger.warning(
                f"Failed to create {type_.__name__} from {mung_obj}", exc_info=True
            )
        else:
            raise ValueError(
                f"Failed to create {type_.__name__} from {mung_obj}"
            ) from e


def needs_graph(fn):
    fn._needs_graph = True  # type: ignore
    return fn


def _constructor_needs_graph(fn: SOConstructor):
    return getattr(fn, "_needs_graph", False)


def single_subevent(fn):
    fn._single_sub = True  # type: ignore
    return fn


def _constructor_is_single_sub(fn: SOConstructor):
    return getattr(fn, "_single_sub", False)


@dataclass
class CollectorRecord:
    type_: Type[SceneObject]
    class_names: set[str | StrEnum] | list[str | StrEnum] | str | StrEnum
    constructor: SOConstructor | None
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

    def _run_constructor_impl(
        self, rec: CollectorRecord, graph: NotationGraph, is_critical: bool = False
    ) -> None:
        if rec.constructor is None:
            logger.warning(f"Constructor for '{rec.type_.__name__}' not specified")
            return

        _single_sub = _constructor_is_single_sub(rec.constructor)
        _needs_graph = _constructor_needs_graph(rec.constructor)

        for mung_node, subevents in rec.subevents_by.items():
            if _single_sub:
                for sub in subevents:
                    if _needs_graph:
                        args = (mung_node, sub, graph)
                    else:
                        args = (mung_node, sub)

                    with _construction_guard(mung_node, rec.type_, is_critical):
                        rec.constructor(*args)  # type: ignore

            else:
                if _needs_graph:
                    args = (mung_node, list(subevents), graph)
                else:
                    args = (mung_node, list(subevents))

                with _construction_guard(mung_node, rec.type_, is_critical):
                    rec.constructor(*args)  # type: ignore

    def run_constructor(
        self, type_: Type[SceneObject], graph: NotationGraph, is_critical: bool = False
    ) -> None:
        rec = self._index[type_]
        self._run_constructor_impl(rec, graph, is_critical)

    def run_constructors(
        self, graph: NotationGraph, critical_types: set[Type[SceneObject]]
    ) -> None:
        for rec in self._records:
            self._run_constructor_impl(rec, graph, rec.type_ in critical_types)
