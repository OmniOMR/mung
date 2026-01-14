from typing import Optional
from mung import Node, NotationGraph
from mung.constants import ClassNameConstants as C


class _DummyStaffGenerator:
    """
    Dummy staff with noteheads for testing, implemented with NotationGraph.
    This graph contains a staff with stafflines and staffspaces,
    a notehead for each staff position is also generated.

    These nodes have no information within them, have zero width, height
    and are located at `(0, 0)`. Only stafflines and staffspaces have
    some top coordinate, as it is important for their ordering
    inside some algorithms.

    Structure:

        (id)
        0:               (staffSpace)
        1: ------------- (staffLine)
        2:
        3: -------------
        4:
        5: -------------
        6:
        7: -------------
        8:
        9: -------------
        10:

        11: staff
    """
    def __call__(
            self, 
            clef_name: Optional[str] = None,
            clef_delta: Optional[int] = None,
            key_signature: Optional[int] = None
            ) -> NotationGraph:
        graph = self._add_notehead_to_every_dummy_staff_position(
            self._create_dummy_staff(staffline_count=self._staffline_count)
        )
        self._staff_id = graph.filter_vertices(C.Staves.STAFF)[0].id

        if clef_name is not None:
            graph = self._add_clef(graph, clef_name, clef_delta)
        
        if key_signature is not None and key_signature != 0:
            graph = self._add_key_signature(graph, key_signature)
        
        return graph

    def __init__(self, staffline_count: int = 5):
        self._staffline_count = staffline_count
    
    @staticmethod
    def _create_dummy_staff(
        staffline_count: int = 5, spacing: int = 5
    ) -> NotationGraph:
        assert staffline_count > 0
        nodes: list[Node] = []
        _id = 0
        # create stafflines and staffspaces
        for i in range(staffline_count * 2 + 1):
            nodes.append(
                Node(
                    _id,
                    C.Staves.STAFF_SPACE
                    if i % 2 == 0
                    else C.Staves.STAFF_LINE,
                    spacing * i, 0, 0, 0,
                )
            )
            _id += 1

        # add staff
        staff_id = _id
        nodes.append(Node(staff_id, C.Staves.STAFF, 0, 0, 0, 0))

        graph = NotationGraph(nodes)
        for n in range(len(nodes) - 1):
            graph.add_edge(staff_id, n)

        return graph

    @staticmethod
    def _add_notehead_to_every_dummy_staff_position(
        graph: NotationGraph,
    ) -> NotationGraph:
        noteheads: list[Node] = []
        staff = graph.filter_vertices(C.Staves.STAFF)[0]
        positions = graph.filter_vertices(
            [C.Staves.STAFF_LINE, C.Staves.STAFF_SPACE]
        )

        _id = graph.next_node_id
        for _ in positions:
            noteheads.append(Node(_id, C.Noteheads.NOTEHEAD_BLACK, 0, 0, 0, 0))
            _id += 1

        graph = NotationGraph(graph.vertices + noteheads)
        for notehead, pos in zip(noteheads, positions):
            graph.add_edge(notehead.id, pos.id)
            graph.add_edge(notehead.id, staff.id)
        return graph

    def _sorted_staffline_ids(self, graph: NotationGraph) -> list[int]:
        return [
            x.id
            for x in sorted(
                graph.filter_vertices(C.Staves.STAFF_LINE),
                key=lambda s: s.top,
                reverse=True
            )
        ]

    def _add_clef(self, graph: NotationGraph, clef_name: str, delta_from_bottom: Optional[int] = None) -> NotationGraph:
        """
        Adds given clef to the graph and modifies the graph.
        If ``delta_from_bottom`` is specified, also snaps
        the clef to a staffline ``delta_from_bottom`` steps
        from the bottom - if delta is 0, clef is snapped
        to the most bottom staffline.
        """
        assert delta_from_bottom is None or 0 <= delta_from_bottom < self._staffline_count
        
        clef_id = graph.next_node_id
        clef = Node(clef_id, clef_name, 0, 0, 0, 0)
        new_graph = NotationGraph(graph.vertices + [clef])
        new_graph.add_edge(clef_id, self._staff_id)
        if delta_from_bottom is not None:
            new_graph.add_edge(clef_id, self._sorted_staffline_ids(graph)[delta_from_bottom])
        
        return new_graph
    
    def _add_key_signature(self, graph: NotationGraph, key_signature: int) -> NotationGraph:
        assert abs(key_signature) <= 7

        if key_signature == 0:
            return graph
        elif key_signature > 0:
            accidental_type = C.Accidentals.ACCIDENTAL_SHARP
        else:
            accidental_type = C.Accidentals.ACCIDENTAL_FLAT

        _id = graph.next_node_id
        sig_node = Node(_id, C.KeySignature.KEY_SIGNATURE, 0, 0, 0, 0)
        _id += 1
        accidentals: list[Node] = []
        for _ in range(abs(key_signature)):
            accidentals.append(Node(_id, accidental_type, 0, 0, 0, 0))
            _id += 1
        
        new_graph = NotationGraph(graph.vertices + accidentals + [sig_node])

        new_graph.add_edge(sig_node.id, self._staff_id)
        for a in accidentals:
            new_graph.add_edge(sig_node.id, a.id)

        return new_graph


