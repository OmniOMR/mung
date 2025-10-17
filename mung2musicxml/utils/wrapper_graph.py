from typing import Callable, TypeVar, Generic, Self, Optional
from .topological_sort import topological_sort
from fractions import Fraction
from enum import Enum
from ..logger import logger

T = TypeVar("T")

class WrapperNode(Generic[T]):
    def __init__(
            self,
            obj: T,
            start: int | Fraction = 0,
            duration: int | Fraction = 1,
            priority: int = 0
        ):
        self.obj: T = obj
        self.children: list["WrapperNode"] = []
        self.parents: list["WrapperNode"] = []
        self.start = start if isinstance(start, Fraction) else Fraction(start)
        self.duration = duration if isinstance(duration, Fraction) else Fraction(duration)
        self.priority = priority

    def __repr__(self):
        return f"Node({self.obj!r})"

    @property
    def end(self) -> Fraction:
        return self.start + self.duration


class WrapperGraph:
    def __init__(self, nodes: list[WrapperNode] | set[WrapperNode]) -> None:
        self._nodes = list(nodes)
    
    def __getitem__(self, index: int) -> WrapperNode:
        assert -1 < index < len(self)
        return self._nodes[index]

    def __iter__(self):
        return (self[i] for i in range(len(self)))
    
    def __len__(self) -> int:
        return len(self._nodes)
    
    @classmethod
    def from_other_graph(cls, nodes: list[T], get_neighbors: Callable[[T], list[T]]) -> Self:
        return cls(cls.build_graph(nodes, get_neighbors))
    
    @staticmethod
    def _default_get_start_and_duration(_: T) -> tuple[Fraction, Fraction]:
        return Fraction(1), Fraction(1)

    @staticmethod
    def build_graph(
        objects: list[T],
        get_neighbors: Callable[[T], list[T]],
        get_start_and_duration: Optional[Callable[[T], tuple[ int | Fraction, int | Fraction]]] = None
        ) -> list[WrapperNode]:
        """
        Build a graph of Node wrappers around given objects.

        :param objects: list of original objects
        :param get_neighbors: function mapping object -> list of neighbor objects
        :return: list of Node instances, each linked to its neighbors
        """
        if get_start_and_duration is None:
            get_start_and_duration = WrapperGraph._default_get_start_and_duration
        # First create a mapping from original object to its Node
        obj_to_node: dict[T, WrapperNode] = dict()
        for obj in objects:
            start, duration = get_start_and_duration(obj)
            obj_to_node[obj] = WrapperNode(obj, start, duration)
            
        # Then populate neighbor relationships
        for obj, node in obj_to_node.items():
            for neigh in get_neighbors(obj):
                if neigh in obj_to_node:  # only link if neighbor is in our object set
                    node.children.append(obj_to_node[neigh])
                    obj_to_node[neigh].parents.append(node)

        return list(obj_to_node.values())
    
    def get_components(self) -> list["WrapperGraph"]:
        """
        Separate a DAG into weakly connected components.
        
        :param nodes: list of Node objects (graph may not be fully connected)
        :return: list of sets, each set is a weakly connected component
        """
        visited = set()
        components = []

        for node in self._nodes:
            if node not in visited:
                # BFS/DFS to collect component
                stack = [node]
                comp = set()
                while stack:
                    curr = stack.pop()
                    if curr not in visited:
                        visited.add(curr)
                        comp.add(curr)
                        # Neighbors in both directions
                        neighbors = set(curr.children)
                        neighbors.update(n for n in self._nodes if curr in n.children)
                        stack.extend(neighbors)
                components.append(comp)

        return [WrapperGraph(x) for x in components]
    
    def topological_sort(self) -> list[WrapperNode]:
        return topological_sort(self._nodes, lambda p, c: c in p.children)

    def schedule_and_find_width(self) -> list[WrapperNode]:
        """
        Compute schedule (start, end) for each node,
        maximum width (overlap),
        and the set of nodes active at that max width.
        """
        class EventType(Enum):
            START = +1
            END = -1

            def __lt__(self, other: Any) -> bool:
                assert isinstance(other, EventType)
                return self.value < other.value
        
        class Event:
            def __init__(
                    self,
                    onset: Fraction,
                    e_type: EventType,
                    node: WrapperNode
                ):
                self.onset = onset
                self.e_type = e_type
                self.node = node

            def __lt__(self, other: Any) -> bool:
                assert isinstance(other, Event)
                return (self.onset, self.e_type) < (other.onset, other.e_type)
            
            def __str__(self) -> str:
                return f"Event({self.onset}, {self.e_type.value}, {self.node.obj})"


        events: list[Event] = []
        for node in self:
            events.append(Event(node.start, EventType.START, node))
            events.append(Event(node.end, EventType.END, node))

        # at a point in time, always first deactivate nodes and than activate them
        # as the durations should be interpreted as [start, end)

        # A from 1 to 2, [1, 2), and B from 2 to 3, [2, 3), should not be active
        # at the same time, that's why we need to deactivate A first 
        # print([str(e) for e in events])
        events.sort()
        # print([str(e) for e in events])

        logger.debug(f"Found events sorted: {events}")

        max_width = 0
        active: set[WrapperNode] = set()
        max_active_snapshot: list[WrapperNode] = []

        for event in events:
            # print([str(e) for e in active])
            if event.e_type == EventType.START:
                active.add(event.node)
            elif event.e_type == EventType.END:
                active.remove(event.node)
            else:
                raise ValueError()

            if len(active) > max_width:
                max_width = len(active)
                max_active_snapshot = list(active)

        return max_active_snapshot

    def get_sources(self) -> list[WrapperNode]:
        indegree = {node: 0 for node in self}
        for node in self:
            for neigh in node.children:
                indegree[neigh] += 1
        
        return [node for node in self if indegree[node] == 0]
    

from collections import defaultdict
from queue import PriorityQueue
from typing import Any

from collections import defaultdict, deque
from typing import TypeVar, Callable, Generic

from collections import deque
from fractions import Fraction
from pathlib import Path
import numpy as np

def dag_layers(graph: WrapperGraph) -> list[list[WrapperNode]]:
    """
    Return a layered decomposition of the DAG.
    Each layer contains nodes whose predecessors are all in earlier layers.
    """
    indegree = {node: 0 for node in graph}
    for node in graph:
        for neigh in node.children:
            indegree[neigh] += 1

    layers: list[list[WrapperNode]] = []
    q = deque([n for n in graph if indegree[n] == 0])

    while q:
        layer = list(q)
        layers.append(layer)
        next_q = deque()

        while q:
            u = q.popleft()
            for v in u.children:
                indegree[v] -= 1
                if indegree[v] == 0:
                    next_q.append(v)

        q = next_q

    return layers

def assign_voices(
        graph: WrapperGraph,
        output_file: Path | str,
        fps: int = 1
) -> dict[WrapperNode, int]:
    """
    Assign line numbers (voices) to each node in the schedule.

    Finds the widest place in graph - where the most voices overlap,
    and then propagates voices from these nodes to others using a greedy
    approach. The node with the lowest voice propagates first.

    :param graph: A graph instance
    :return: dict[node] -> assigned line number)
    """
    voices: dict[WrapperNode, int] = {}
    
    # --- Core logic ---
    _, _, widest_nodes = graph.schedule_and_find_width()
    widest_sorted = sorted(widest_nodes, key=lambda n: n.priority)
    for i, node in enumerate(widest_sorted, start=1):
        voices[node] = i

    q: PriorityQueue[tuple[int, int, WrapperNode]] = PriorityQueue()
    for node in widest_sorted:
        q.put((voices[node], id(node), node))

    start_node = WrapperNode("__START__", duration=0, priority=-1)
    
    start_node.children = graph.get_sources()
    new_graph = WrapperGraph(graph._nodes + [start_node])
    # Forward and backward expansion at the same time
    def compute_next_voice(
            nodes: list[WrapperNode],
            voices: dict[WrapperNode, int],
            base_voice: int
        ) -> int:
        max_voice = max([node_voice + 1 for node in nodes if (node_voice := voices.get(node)) is not None], default=current_node_voice)
        return max(base_voice, max_voice)
    
    parents: defaultdict[WrapperNode, list[WrapperNode]] = defaultdict(list)
    for node in new_graph:
        for n in node.children:
            parents[n].append(node)

    operations: list[tuple[str, dict[WrapperNode, int], tuple[WrapperNode, WrapperNode], str]] = []

    while not q.empty():
        current_node_voice, _, node = q.get()
        print(f"Processing {node}")
        # process children, forward
        c_children = sorted(node.children, key=lambda n: n.priority)
        children_voice = compute_next_voice(c_children, voices, current_node_voice)
        for child in c_children:
            if child not in voices:
                voices[child] = children_voice
                q.put((children_voice, id(child), child))
                operations.append((
                    f"Assign {child.obj} -> voice {voices[child]}",
                    voices.copy(),
                    (node, child),
                    "red"
                ))
                children_voice += 1
        # process parents, backward
        c_parents = sorted(parents[node], key=lambda n: n.priority)
        parents_voice = compute_next_voice(c_parents, voices, current_node_voice)
        for parent in c_parents:
            if parent not in voices:
                voices[parent] = parents_voice
                q.put((parents_voice, id(parent), parent))
                operations.append((
                    f"Assign {parent.obj} -> voice {voices[parent]}",
                    voices.copy(),
                    (parent, node),
                    "blue"
                ))
                parents_voice += 1
    
    import networkx as nx
    from io import BytesIO
    import matplotlib.pyplot as plt
    import imageio

    G = nx.DiGraph()
    for node in new_graph:
        G.add_node(node)
        for neigh in node.children:
            G.add_edge(node, neigh)

    layers = dag_layers(new_graph)
    num_layers = len(layers)
    max_height = max(len(x) for x in layers)

    pos: dict["WrapperNode", np.ndarray] = {}
    # prio = assign_voice(graph)
    # print(prio)
    for l, layer in enumerate(layers):
        layer = sorted(layer, key=lambda n: voices[n])
        print(layer)
        for n, node in enumerate(layer):
            
            pos[node] = np.array([l / num_layers, - n / max_height]) # - len(layer) / max_height / 2])

    frames: list[bytes] = []

    default_color = "#0065bf"
    colors: defaultdict[int, str] = defaultdict(lambda: default_color)
    colors[1] = default_color
    colors[2] = "#007f00"
    colors[3] = "#c53f00"
    colors[4] = "#c31989"


    def make_frame(
            step_desc: str,
            voices: dict[WrapperNode, int],
            highlight_edge: Optional[tuple] = None,
            highlight_color: str = "red"
        ):
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.set_title(step_desc)

        # Draw all edges in gray
        nx.draw_networkx_edges(G, pos, edgelist=G.edges(), ax=ax,
                               arrowstyle="->", arrowsize=15, width=1.5, edge_color="gray",
                               min_source_margin=10, min_target_margin=10)

        # Highlight a specific edge if provided
        if highlight_edge:
            nx.draw_networkx_edges(G, pos, edgelist=[highlight_edge], ax=ax,
                                   edge_color=highlight_color, width=2.5, arrowstyle="->", arrowsize=20)

        # Draw nodes
        assigned = [n for n in G.nodes if n in voices]
        unassigned = [n for n in G.nodes if n not in voices]

        for node in assigned:
            nx.draw_networkx_nodes(G, pos, nodelist=[node], node_color=colors[voices[node]],
                               edgecolors="black", node_size=800, ax=ax)
        nx.draw_networkx_nodes(G, pos, nodelist=unassigned, node_color="white",
                               edgecolors="black", node_size=800, ax=ax)

        labels = {n: f"{n.obj}\n({voices[n]})" for n in assigned}
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, ax=ax)
        labels_unassigned = {n: str(n.obj) for n in unassigned}
        nx.draw_networkx_labels(G, pos, labels=labels_unassigned, font_size=8, ax=ax)

        ax.axis("off")
        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close(fig)
        frames.append(buf.getvalue())
    
    for desc, c_voices, edge, color in operations:
        make_frame(desc, c_voices, edge, color)

    
    if isinstance(output_file, str):
        output_file = Path(output_file)
    
    output_file.parent.mkdir(parents=True, exist_ok=True)

    imageio.mimsave(output_file, [imageio.v2.imread(f) for f in frames], fps=fps)
    voices.pop(start_node)
    print(voices)
    return voices

def build_large_graph():
    durations = {
        "A": 2, "B": 2, "C": 3, "D": 2, "E": 1,
        "F": 2, "G": 2, "H": 3
    }
    priorities = {k: i for i, k in enumerate(durations.keys(), start=1)}
    edges = [
        ("A", "B"), ("A", "C"),
        ("B", "D"), ("B", "E"),
        ("C", "F"),
        ("D", "G"), ("E", "G"),
        ("F", "H"), ("G", "H")
    ]

    def get_neighbors(x): return [v for u, v in edges if u == x]
    def get_duration(x): return durations[x]
    def get_priority(x): return priorities[x]

    nodes = WrapperGraph.build_graph(list(durations.keys()), get_neighbors, get_duration)
    for n in nodes:
        n.priority = get_priority(n.obj)
    return WrapperGraph(nodes)

if __name__ == "__main__":

    durations = {"A": 2, "B": 3, "C": 1}
    priorities = {"A": 1, "B": 2, "C": 3}
    edges = [("A", "B"), ("B", "C")]

    def get_neighbors(x): return [v for u, v in edges if u == x]
    def get_duration(x): return durations[x]
    def get_priority(x): return priorities[x]

    nodes = WrapperGraph.build_graph(list(durations.keys()), get_neighbors, get_duration)
    for n in nodes:
        n.priority = get_priority(n.obj)

    g = build_large_graph()
    # Nodes
    A = WrapperNode("A", priority=1)
    B = WrapperNode("B", priority=2)
    C = WrapperNode("C", priority=3)
    D = WrapperNode("D", priority=4)
    E = WrapperNode("E", priority=5)
    F = WrapperNode("F", priority=6)
    G = WrapperNode("G", priority=7)

    # Edges (A splits into B and C, which join into D, then split again)
    A.children = [B, C]
    B.children = [D]
    C.children = [D]
    D.children = [E, F]
    E.children = [G]
    F.children = [G]

    graph1 = [A, B, C, D, E, F, G]
    widest_nodes1 = [D]  # the widest layer in this DAG
    # g = WrapperGraph(graph1)

    U = WrapperNode("U", priority=1)
    V = WrapperNode("V", priority=2)
    W = WrapperNode("W", priority=3)
    X = WrapperNode("X", priority=4)
    Y = WrapperNode("Y", priority=5)
    Z = WrapperNode("Z", priority=6)
    AA = WrapperNode("AA", priority=7)
    BB = WrapperNode("BB", priority=8)

    U.children = [V, W]
    V.children = [X, Y]
    W.children = [Y, Z]
    X.children = [AA]
    Y.children = [AA, BB]
    Z.children = [BB]

    graph4 = [U, V, W, X, Y, Z, AA, BB]
    widest_nodes4 = [Y]  # widest layer

    U = WrapperNode("U", priority=1)
    V = WrapperNode("V", priority=2)
    W = WrapperNode("W", priority=3)
    X = WrapperNode("X", priority=4)
    Y = WrapperNode("Y", priority=5)
    Z = WrapperNode("Z", priority=6)
    AA = WrapperNode("AA", priority=7)
    BB = WrapperNode("BB", priority=8)

    U.children = [V, W]
    V.children = [X, Y]
    W.children = [Y, Z]
    X.children = [AA]
    Y.children = [AA, BB]
    Z.children = [BB]

    graph4 = [U, V, W, X, Y, Z, AA, BB]
    widest_nodes4 = [Y]  # widest layer

    M = WrapperNode("M", priority=1, duration=1)
    N = WrapperNode("N", priority=2, duration=1)
    O = WrapperNode("O", priority=3, duration=1)
    P = WrapperNode("P", priority=4, duration=2)
    Q = WrapperNode("Q", priority=5, duration=1)
    R = WrapperNode("R", priority=6, duration=1)
    S = WrapperNode("S", priority=7, duration=1)
    T = WrapperNode("T", priority=8, duration=1)
    U = WrapperNode("U", priority=9, duration=1)
    V = WrapperNode("V", priority=10, duration=1)
    W = WrapperNode("W", priority=11, duration=1)
    X = WrapperNode("X", priority=12, duration=2)

    M.children = [N, O]
    N.children = [P, Q]
    O.children = [Q ,V, X]
    # P.neighbors = [S]
    Q.children = [S]
    # R.neighbors = [T]
    U.children = [O]
    V.children = [R]
    W.children = [T]
    # R.neighbors = [W]
    # X.neighbors = [T]


    graph3 = [M, N, O,P, Q, R, S, T, U, V, W, X]
    widest_nodes3 = [Q]  # node with most concurrent paths

    g = WrapperGraph(graph3)

    width, times, widest = g.schedule_and_find_width()
    voices = assign_voices(g, "schedule.gif")
