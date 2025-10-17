from collections import defaultdict, deque
from typing import TypeVar, Callable

T = TypeVar("T")


def topological_sort(nodes: list[T], is_predecessor_of: Callable[[T, T], bool]) -> list[T]:
    """
    Sorts a given graph by its topological order.
    The given graph has to be a DAG.

    It is not stable.

    :param nodes: List of node objects
    :param is_predecessor_of: A method that,
        given a parent node and a child node, determines,
        if they are in a parent-child relationship
    :return: List of nodes sorted by topological order
    in ascending order
    """
    # Build adjacency list and indegree count
    adj = defaultdict(list)
    indegree = {node: 0 for node in nodes}

    for u in nodes:
        for v in nodes:
            if u != v and is_predecessor_of(u, v):
                adj[u].append(v)
                indegree[v] += 1

    # Initialize queue with nodes of indegree 0
    q = deque([n for n in nodes if indegree[n] == 0])
    sorted_nodes = []

    while q:
        u = q.popleft()
        sorted_nodes.append(u)
        for v in adj[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                q.append(v)

    # If not all nodes are sorted, there was a cycle (shouldn't happen for a DAG)
    if len(sorted_nodes) != len(nodes):
        raise ValueError("Graph is not a DAG!")

    return sorted_nodes
