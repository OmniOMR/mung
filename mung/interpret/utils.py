from .. import Node, NotationGraph


def precedence_graph_sort(nodes: list[Node], graph: NotationGraph) -> list[Node]:
    """
    Sort nodes that form a path graph from source to sink,
    according to precedence edges.
    
    :param nodes: List of nodes to sort
    :returns: List of nodes sorted from source to sink
    """
    if not nodes:
        return []
    
    if len(nodes) == 1:
        return nodes
    
    # Find the source node (has no parent)
    source = None
    for node in nodes:
        has_parent = False
        for other in nodes:
            if node != other and graph.is_precedence_child_of(node, other):
                has_parent = True
                break
        if not has_parent:
            if source is not None:
                raise ValueError("Multiple source nodes found - graph is not a valid path")
            source = node
    
    if source is None:
        raise ValueError("No source node found - graph contains a cycle")
    
    # Build the path from source to sink
    result = [source]
    current = source
    visited = {source}
    
    while len(result) < len(nodes):
        # Find the child of current node
        child = None
        for node in nodes:
            if node not in visited and graph.is_precedence_child_of(node, current):
                if child is not None:
                    raise ValueError(f"Node {current} has multiple children - graph is not a valid path")
                child = node
        
        if child is None:
            raise ValueError(f"Path terminated early at node {current} - graph is not connected")
        
        result.append(child)
        visited.add(child)
        current = child
    
    assert len(result) == len(nodes)
    return result
