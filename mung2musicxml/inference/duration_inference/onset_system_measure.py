from fractions import Fraction
from mung import NotationGraph, Node
from typing import Optional, Self

from mung.constants import (
    ClassNameConstants as C,
    InferenceEngineConstants as I,
    OnsetDataConstants as O
)
from mung.graph import group_by_system_measure
from ...utils import topological_sort
from ...logger import logger


class _OnsetSystemMeasureWrapper:
    """
    Holds reference to a single staff and all nodes that
    bear duration and are linked to this staff.
    """
    def __init__(self, nodes: list[Node], parent_staffs: list[Node], graph: NotationGraph):
        self._nodes = nodes
        self._parent_staffs = parent_staffs
        self._graph = graph

    def __len__(self) -> int:
        return len(self._nodes)

    @staticmethod
    def _set_onset(node: Node, onset: Fraction) -> None:
        logger.debug(f"Caching onset for node {node.id}")
        node.data[O.ONSET_BEATS] = onset
        
    @staticmethod
    def _infer_onset_for_node(parents: list[Node], permissive: bool = True) -> Fraction:
        assert len(parents) > 0
        parent_ends = set(_OnsetSystemMeasureWrapper._node_end_onset(p) for p in parents)
        if len(parent_ends) > 1:
            msg = f"Ends of {[x.id for x in parents]} not synchronized"
            if permissive:
                logger.warning(msg)
            else:
                raise ValueError(msg)
        
        return max(parent_ends)
    
    def sources(self) -> list[Node]:
        ids = set(x.id for x in self._nodes)
        output: list[Node] = []
        for node in self._nodes:
            # empty inlinks -> source
            if len(node.precedence_inlinks) == 0:
                output.append(node)
            
            # inlink from current system measure exists -> not a source
            elif any((inlink in ids) for inlink in node.precedence_inlinks):

                pass
            # no inlink from current system measure exists -> source
            else:
                output.append(node)
        
        assert len(output) > 0
        return output
    
    def sinks(self) -> list[Node]:
        ids = set(x.id for x in self._nodes)
        output: list[Node] = []
        for node in self._nodes:
            # empty inlinks -> source
            if len(node.precedence_outlinks) == 0:
                output.append(node)
            
            # inlink from current system measure exists -> not a source
            elif any((inlink in ids) for inlink in node.precedence_outlinks):

                pass
            # no inlink from current system measure exists -> source
            else:
                output.append(node)
        
        # assert len(output) > 0
        return output

    def infer_onsets(self, start_onset: Optional[Fraction] = None, permissive: bool = True) -> None:
        """
        Infers symbols durations inside a single system measure (SM).

        Source symbols (they have no inlinks at this particular SM) are
        assigned the onset ``start_onset``. For every other symbol,
        its onset is the maximum of onsets assigned to its parents.
        """
        if start_onset is None:
            start_onset = Fraction(0)

        # Check edge case
        if len(self) == 0:
            logger.warning(f"Empty measure found on staffs {[x.id for x in self._parent_staffs]}")
            return
        
        # Get durables whose duration is time sig dependant
        # - they last full measure and should always be a sink and a source
        # -> we can extract them from topological sort with no harm done
        # - they start at the minimal onset and end at the maximal end onset
        time_sig_dep = [x for x in self._nodes if x.class_name in I.MEASURE_LASTING_CLASS_NAMES]
        if len(time_sig_dep) > 0:
            logger.warning(f"Found measure lasting symbols: {[str(x) for x in time_sig_dep]}")

        nodes = [x for x in self._nodes if x not in set(time_sig_dep)]
        
        # Sort nodes for easier inference
        topo_sort = topological_sort(nodes, lambda p, c: c.id in p.precedence_outlinks)
        logger.debug(f"Inferring onset for: {[x.id for x in topo_sort]}")

        # Get sources, set their onset to "start", and remove them 
        # from a list of nodes whose onset still needs to be determined
        sources = self.sources()
        logger.debug(f"Found sources: {[x.id for x in sources]}")
        assert len(sources) > 0

        for source in sources:
            self._set_onset(source, start_onset)
        
        not_sources = [x for x in topo_sort if x not in sources]

        def parents_in_measure(node: Node, nodes: list[Node]) -> list[Node]:
            return [n for _id in node.precedence_inlinks if (n := self._graph[_id]) in nodes]

        # For each node, look at its parents and choose the maximal onset
        for node in not_sources:
            logger.debug(f"Processing {node.class_name} {node.id}")
            onset = self._infer_onset_for_node(parents_in_measure(node, nodes), permissive=permissive)
            self._set_onset(node, onset)
        
        if len(time_sig_dep) > 0:
            sm_start_onset = start_onset
            if len(nodes) == 0:
                sm_duration = I.DEFAULT_MEASURE_DURATION
            else:
                sm_end_onset = max(node.data[O.ONSET_BEATS] + node.data[O.DURATION_BEATS] for node in nodes)
                sm_duration = sm_end_onset - sm_start_onset
            
            for node in time_sig_dep:
                logger.warning(f"Processed {node} as time signature dependant: onset={sm_start_onset}, duration={sm_duration}")
                node.data[O.ONSET_BEATS] = sm_start_onset
                node.data[O.DURATION_BEATS] = sm_duration
                node.data[O.DURATION_BEATS_WO_M] = sm_duration        
    
    def is_synchronized(self) -> bool:
        sinks = self.sinks()
        ends = set(self._node_end_onset(sink) for sink in sinks)
        # assert len(ends) > 0
        if len(self._nodes) == 0:
            return True
        return len(ends) == 1
        
    @classmethod
    def from_list_of_symbols(cls, graph: NotationGraph, symbols: list[Node]) -> Self:
        """
        ``symbols`` is a list of Nodes that belong to the same system measure.
        """
        staffs: set[Node] = set()
        for symbol in symbols:
            if symbol.class_name in I.CLASSES_BEARING_DURATIONS:
                s = graph.children(symbol, class_filter=C.Staves.STAFF)
                if len(s) != 1:
                    logger.warning(f"Unexpected number of staffs linked to symbol {symbol.class_name} {symbol.id}")
                staffs.update(s)
            else:
                logger.warning(f"Filtered out symbol that does not bear a duration {symbol.class_name} {symbol.id}")
        
        return cls(symbols, list(staffs), graph)
    
    @classmethod
    def from_graph(cls, graph: NotationGraph) -> list[Self]:
        return [cls.from_list_of_symbols(
                graph,
                [s for s in symbols if s.class_name in I.CLASSES_BEARING_DURATIONS]
            )
            for symbols in group_by_system_measure(graph)]

    def get_start_onset(self) -> Fraction:
        if len(self._nodes) == 0:
            return Fraction(0)
        return min(self._nodes, key=lambda x: x.data[O.ONSET_BEATS]).data[O.ONSET_BEATS]

    @staticmethod
    def _node_end_onset(node: Node) -> Fraction:
        return node.data[O.ONSET_BEATS] + node.data[O.DURATION_BEATS]
    
    def get_end_onset(self) -> Fraction:
        if len(self._nodes) == 0:
            return Fraction(0)
        
        # Max next onset is node onset + its duration (the onset of the "next" potential symbol)
        return max(self._node_end_onset(node) for node in self._nodes)
        
    def get_duration(self) -> Fraction:
        return self.get_end_onset() - self.get_start_onset()
    
    def offset_onset(self, value: Fraction):
        """
        Changes the onset of duration-bearing symbols on this staff simultaneously,
        effectively postponing the onset of the staff in the global context.

        :param value: Value to offset all related offsets by.
        """
        length_before = self.get_duration()
        logger.info(f"Offsetting onset for {len(self._nodes)} nodes by {value}")
        for node in self._nodes:
            node.data[O.ONSET_BEATS] += value
        # Total staff duration should not change
        assert length_before == self.get_duration()

