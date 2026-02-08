from collections import defaultdict
from typing import TypeVar, Callable

T = TypeVar("T")


def topological_sort(nodes: list[T], is_predecessor_of: Callable[[T, T], bool]) -> list[T]:
    # Build adjacency list
    adj = defaultdict(list)
    for u in nodes:
        for v in nodes:
            if u != v and is_predecessor_of(u, v):
                adj[u].append(v)

    visited = set()
    visiting = set()
    order = []
    parent = {}

    def dfs(u: T):
        if u in visiting:
            # cycle found: reconstruct it
            cycle = [u]
            cur = parent[u]
            while cur != u:
                cycle.append(cur)
                cur = parent[cur]
            cycle.append(u)
            cycle.reverse()
            raise ValueError(f"Cycle detected: {' --> '.join(map(str, cycle))}")

        if u in visited:
            return

        visiting.add(u)

        for v in adj[u]:
            if v not in visited:
                parent[v] = u
            dfs(v)

        visiting.remove(u)
        visited.add(u)
        order.append(u)

    for node in nodes:
        if node not in visited:
            parent[node] = node
            dfs(node)

    return list(reversed(order))
