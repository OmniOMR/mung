from pathlib import Path
from .dummy_node import DummyNode
from mung import Node, NotationGraph


def load_dot_graph(file_path: Path | str, load_edges_as_syntax: bool = True) -> NotationGraph:
    if isinstance(file_path, str):
        file_path = Path(file_path)

    nodes: list[Node] = []
    edges: list[tuple[int, int]] = []

    with open(file_path, "r", encoding="utf8") as f:
        for line in f.readlines():
            line = line.strip()
            tokens = line.split()
            if len(tokens) > 1:
                if "label" in tokens[1]:
                    class_name = tokens[1].split(":")[1].split("\"")[0]
                    id_ = int(tokens[0])
                    nodes.append(DummyNode(id_, class_name))
                elif "->" in tokens[1]:
                    tokens[2] = tokens[2].replace(";", "")
                    edges.append((int(tokens[0]), int(tokens[2])))
    
    graph = NotationGraph(nodes)
    for from_, to in edges:
        if load_edges_as_syntax:
            graph.add_edge(from_, to)
        else:
            graph.add_precedence_edge(from_, to)
    
    return graph
