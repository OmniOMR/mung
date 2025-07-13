from mung import NotationGraph, Node
import logging
from mung.constants import ClassNamesConstants


def remove_duplicate_groupings(graph: NotationGraph) -> bool:
    """
    Removes duplicate groupings that are a direct result of export scripts.
    Modifies the graph in place.
    
    Returns ``True`` if any groupings were removed.
    """
    logging.info("Removing duplicate groupings")

    removed_any = False

    def _merge_groupings(graph: NotationGraph, grouping_to_merge_to: Node, other_grouping: Node):
        """
        Transfers all links from the duplicate grouping
        and removes it from the graph.
        """
        # Transfer all links from big one to small one
        to_id = grouping_to_merge_to.id
        for from_id in other_grouping.outlinks:
            if from_id != to_id:
                graph.add_edge(from_id, to_id)
        from_id = grouping_to_merge_to.id
        for to_id in other_grouping.inlinks:
            if from_id != to_id:
                graph.add_edge(from_id, to_id)

        graph.remove_vertex(other_grouping.id)
        logging.info(f"Transferred {other_grouping.id} to {to_id} and removed {other_grouping.id}")

    to_remove: list[tuple[Node, Node]] = []
    groupings = graph.filter_vertices(ClassNamesConstants.STAFF_GROUPING)

    for grouping in groupings:
        if len(grouping.inlinks) == 1 and graph[
            grouping.inlinks[0]].class_name == ClassNamesConstants.STAFF_GROUPING and len(grouping.outlinks) == 0:
            to_remove.append((grouping, graph[grouping.inlinks[0]]))
            logging.debug(
                f"Marked {grouping.class_name} {grouping.id} to merge with {graph[grouping.inlinks[0]].id}, duplicate")

    for grouping, other_grouping in to_remove:
        _merge_groupings(graph, grouping, other_grouping)

    removed_any = len(to_remove) > 0

    if not removed_any:
        logging.info("No duplicate groupings found")

    return removed_any

