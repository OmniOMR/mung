from mung import NotationGraph, Node
from mung.constants import (
    InferenceEngineConstants as I,
    ClassNameConstants as C,
)
from ...utils import find_subgraphs_bfs
from ...logger import logger


def link_grace_notes_to_parent(graph: NotationGraph) -> None:
    """
    Finds subgraphs of grace notes based on precedence links
    and connects them to a single parent notehead.
    """
    grace_notes = graph.filter_vertices(class_filter=I.GRACE_NOTEHEAD_CLASS_NAMES)
    if len(grace_notes) == 0:
        return
    
    def _has_edge(lyric1: Node, lyric2: Node, graph: NotationGraph) -> bool:
        return (
            graph.is_precedence_parent_of(lyric1, lyric2)
            or graph.is_precedence_parent_of(lyric2, lyric1)
        )
    subgraphs = find_subgraphs_bfs(grace_notes, lambda f, s: _has_edge(f, s, graph))

    for sg in subgraphs:
        parent: Node | None = None
        for node in sg:
            parents = graph.parents(node, class_filter=I.NONGRACE_NOTEHEAD_CLASS_NAMES)
            if len(parents) > 0:
                parent = parents[0]
                break
        
        if parent is None:
            logger.warning(f"Unable to find shared parent notehead for {sg}")
        
        else:
            for node in sg:
                graph.add_edge(parent, node)
