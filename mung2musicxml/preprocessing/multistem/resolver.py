from typing import Optional
from mung import NotationGraph, Node
from mung.constants import ClassNameConstants as C, InferenceEngineConstants as I
from mung2midi.inference import OnsetsInferenceEngine

from .strategy import MultistemResolverStrategy
from .constants import GHOST_NODE_TAG
from ..staff_wrapper.mask_wrapper import MaskAverageIndexWrapper
from ...logger import logger
from ...utils import topological_sort


class MultistemResolver:
    """
    For successful inference of duration, we need to provide
    the algorithm with "ghost notes", whose only purpose is to
    server as placeholders for noteheads that are "obscured"
    by other notehead (notes from two voices have the same pitch).

    As these notes might have different durations - given by their
    modifiers.

    This resolver uses a simple approach of splitting the duration modifiers
    to top and bottom, as there can be at maximum two stems linked to one notehead,
    by default one pointing up and the other one down.
    
    Then, we need to link those duration modifiers that should apply
    to only a one of the noteheads. Other objects, such as tuples, slurs, ...,
    apply to both of the noteheads.

    For incoming links, in MuNG, every symbol can be connected to any other
    inside the same staff if they are played in that succession.
    In other words, we do not have to keep voices separated when resolving inlinks -
    everything preceding the original notehead should also precede the ghost notehead.

    Any precedence inlink is copied for the ghost node, the outlinks
    are assigned to the **shorter** notehead.
    """
    def __init__(self, strategy: Optional[MultistemResolverStrategy] = None):
        self._graph: NotationGraph = None # type: ignore
        self._strategy = strategy if strategy is not None else MultistemResolverStrategy()
        if self._strategy._GHOST_SHIFT > 0:
            logger.warning(
                f"{type(self).__name__} running in GHOST SHIFT MODE, "
                f"all created noteheads will be shifted down by "
                f"{self._strategy._GHOST_SHIFT} pixel{'s' if self._strategy._GHOST_SHIFT > 1 else ''}"
            )
        self._onset_engine = OnsetsInferenceEngine(self._strategy.ONSET_STRATEGY)

    def __call__(self, graph: NotationGraph) -> NotationGraph:
        return self.resolve_double_stemmed_noteheads(graph)
    
    def _error_or_warning(self, msg: str):
        if self._strategy.PERMISSIVE:
            logger.warning(msg)
        else:
            raise ValueError(msg)

    def _check_on_start(self):
        # check that all noteheads are linked to exactly one staff
        for node in self._graph.filter_vertices(class_filter=I.NONGRACE_NOTEHEAD_CLASS_NAMES):
            staffs = self._graph.children(node, class_filter=C.Staves.STAFF)
            if len(staffs) != 1:
                self._error_or_warning(
                    f"Symbol {node.class_name} {node.id} has to be connected to exactly one staff, "
                    f"actual number of staff connections is {len(staffs)}"
                )

    def _check_on_end(self):
        # if this triggers, somethings wrong with our algorithm
        assert len(self._find_multistem_in_graph()) == 0
    
    def resolve_double_stemmed_noteheads(self, graph: NotationGraph) -> NotationGraph:
        self._graph = graph
        self._check_on_start()

        nodes_to_resolve = self._find_double_stemmed_in_graph_and_sort()
        for node in nodes_to_resolve:
            self._separate_double_stemmed_to_two(node)
            logger.debug(f"Resolved double stemmed {node.class_name} {node.id}")

        self._check_on_end()
        t = self._graph
        self._graph = None # type: ignore
        return t

    def _find_multistem_in_graph(self) -> list[Node]:
        """
        Finds all noteheads that have multiple stems.
        """
        to_resolve = [
            node for node in
            self._graph.filter_vertices(I.NONGRACE_NOTEHEAD_CLASS_NAMES)
            if len(self._graph.children(node, C.NoteheadAttachments.STEM)) > 1
        ]
        return to_resolve

    def _find_double_stemmed_in_graph_and_sort(self) -> list[Node]:
        """
        Returns a topologically sorted list of noteheads
        that have exactly two stems.
        """
        multi_stem = self._find_multistem_in_graph()
        if len(multi_stem) > 0:
            logger.warning(f"Will resolve {len(multi_stem)} multistem noteheads: {multi_stem}")
        
        # filter
        double_stemmed: list[Node] = []
        for node in multi_stem:
            if len(self._graph.children(node, C.NoteheadAttachments.STEM)) > 2:
                raise ValueError(f"Notehead {node.id} cannot have more than two stems")
            else:
                double_stemmed.append(node)
        
        # sort
        logger.debug("Multistem resolver, double stems:")
        logger.debug(f"Before sort: {[x.id for x in double_stemmed]}")
        double_stemmed = topological_sort(double_stemmed, lambda p, c: c.id in p.precedence_outlinks)
        logger.debug(f"After sort: {[x.id for x in double_stemmed]}")
        
        return double_stemmed
    
    def _ghost_node_from_node(self, node: Node) -> Node:
        ghost_node = Node(
            self._graph.next_node_id,
            node.class_name,
            node.top + self._strategy._GHOST_SHIFT,
            node.left,
            node.width,
            node.height,
            mask=node.mask.copy() if node.mask is not None else None,
            document=node.document,
            dataset=node.dataset
        )
        ghost_node.data[GHOST_NODE_TAG] = node.id

        return ghost_node
    
    def _relink_shared_objects(self, original: Node, ghost: Node):
        """
        Links all symbols, specified in strategy as shared, that are linked
        to the original notehead to the ghost notehead.
        """
        assert ghost.data.get(GHOST_NODE_TAG, None) == original.id

        to_share = self._graph.children(original, class_filter=self._strategy.SHARED_OBJECTS)
        for node in to_share:
            self._graph.add_edge(ghost, node)
        logger.debug(f"Shared {len(to_share)} symbols "
                    f"between original node {original.id} and ghost node {ghost.id}")
    
    @staticmethod
    def _symbol_distance_from_mask(node: Node, masked_node: Node) -> int:
        assert masked_node.mask is not None
        return node.top - (masked_node.top + MaskAverageIndexWrapper(masked_node.mask)[node.left - masked_node.left])
    
    def _split_objects_between_noteheads(self, original: Node, ghost: Node):
        """
        Groups all symbols, specified in strategy as to divide, that are linked
        to the original notehead into two distinct groups.

        Each group is than assigned to the original notehead or the ghost one.
        """
        to_split = self._graph.children(original, class_filter=self._strategy.DIVIDED_OBJECTS)

        # remove all affected from the original notehead
        for node in to_split:
            self._graph.remove_edge(original, node)
        
        # separate to top and bottom group based on distance
        for node in to_split:
            distance_from_mask = self._symbol_distance_from_mask(original, node)
            if distance_from_mask > 0:
                self._graph.add_edge(original, node)
                logger.debug(f"Added {node.id} to original {ghost.id}")
            else:
                self._graph.add_edge(ghost, node)
                logger.debug(f"Added {node.id} to ghost {ghost.id}")
        
        logger.debug(f"Split {len(to_split)} symbols "
                    f"between original node {original.id} and ghost node {ghost.id}")
    
    def _resolve_incoming_precedence_edges(self, original: Node, ghost: Node) -> None:
        original_staff = self._graph.children(original, class_filter=C.Staves.STAFF)[0]
        preceding_same_staff = [
            n for n in self._graph.precedence_parents(original)
            if self._graph.children(n, class_filter=C.Staves.STAFF)[0].id == original_staff.id
        ]
        logger.debug(f"Preceding symbols on the same staff: {[x.id for x in preceding_same_staff]}")
        for node in preceding_same_staff:
            self._graph.add_precedence_edge(node, ghost)
    
    def _resolve_outgoing_precedence_edges(self, original: Node, ghost: Node) -> None:
        self._onset_engine.initialize_graph(self._graph)
        o_beats = self._onset_engine.beats(original)
        g_beats = self._onset_engine.beats(ghost)
        
        assert o_beats is not None and g_beats is not None
        # all links are already connected to the shorter note (the original)
        if o_beats <= g_beats:
            return
        # reconnect edges
        else:
            logger.info(f"Ghost {ghost.id} is shorter than original {original.id} ({g_beats} < {o_beats}), reconnecting outlinks")
            outlinks = original.precedence_outlinks.copy()
            for outlink in outlinks:
                self._graph.remove_precedence_edge(original, outlink)
                self._graph.add_precedence_edge(ghost, outlink)
        
    def _separate_double_stemmed_to_two(self, notehead: Node):
        assert notehead.class_name in I.NONGRACE_NOTEHEAD_CLASS_NAMES
        stems = self._graph.children(notehead, C.NoteheadAttachments.STEM)
        assert len(stems) == 2

        original_stem, ghost_stem = sorted(stems, key=lambda x: x.top)

        original_notehead = notehead
        ghost_notehead = self._ghost_node_from_node(original_notehead)
        self._graph = NotationGraph(self._graph.vertices + [ghost_notehead])

        self._relink_shared_objects(original_notehead, ghost_notehead)

        self._graph.remove_edge(original_notehead, ghost_stem)
        self._graph.add_edge(ghost_notehead, ghost_stem)

        self._split_objects_between_noteheads(original_notehead, ghost_notehead)

        self._resolve_incoming_precedence_edges(original_notehead, ghost_notehead)
        self._resolve_outgoing_precedence_edges(original_notehead, ghost_notehead)
        