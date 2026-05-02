from typing import TypeVar, Callable

T = TypeVar("T")


def find_subgraphs_bfs(nodes: list[T], has_edge: Callable[[T, T], bool]) -> list[list[T]]:
    """
    Find all connected components (subgraphs) using BFS.
    
    :param nodes: list of objects (nodes in the graph)
    :param has_edge: function(a, b) -> bool,
        returns ``True`` if an edge exists between a and b
    
    :return: list of components, where each component is a list of connected nodes
    """
    unvisited = set(range(len(nodes)))
    components = []

    while unvisited:
        # Start a new component from an arbitrary unvisited node
        start = next(iter(unvisited))
        component = []
        queue = [start]
        unvisited.remove(start)

        while queue:
            curr = queue.pop(0)
            component.append(nodes[curr])

            # Check all remaining unvisited nodes for adjacency
            neighbors = {n for n in unvisited if has_edge(nodes[curr], nodes[n])}
            unvisited -= neighbors
            queue.extend(neighbors)

        components.append(component)

    return components
