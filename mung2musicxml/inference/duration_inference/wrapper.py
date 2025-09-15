from mung.constants import InferenceEngineConstants
from fractions import Fraction
from mung import NotationGraph, Node
from typing import Optional, Self, Any
from mung2midi.inference import BaseOnsetsInferenceStrategy, OnsetsInferenceEngine
from mung.graph import group_staffs_into_systems
from mung.constants import OnsetDataConstants
from dataclasses import dataclass

from ...logger import logger


class _OnsetStaffWrapper:
    """
    Holds reference to a single staff and all nodes that
    bear duration and are linked to this staff.
    """
    def __init__(self, nodes: list[Node], parent_staff: Node):
        self._nodes = nodes
        self._parent_staff = parent_staff
    
    @property
    def parent_staff_id(self) -> int:
        return self._parent_staff.id
    
    @property
    def top(self) -> int:
        return self._parent_staff.top
    
    @classmethod
    def from_staff(cls, graph: NotationGraph, staff: Node) -> Self:
        nodes = graph.parents(staff, InferenceEngineConstants().classes_bearing_duration)
        return cls(nodes, staff)
    
    def get_start_onset(self) -> Fraction:
        if len(self._nodes) == 0:
            return Fraction(0)
        
        return min(self._nodes, key=lambda x: x.data[OnsetDataConstants.ONSET_BEATS]).data[OnsetDataConstants.ONSET_BEATS]

    def get_end_onset(self) -> Fraction:
        if len(self._nodes) == 0:
            return Fraction(0)
        
        def node_end_onset(node: Node) -> Fraction:
            return node.data[OnsetDataConstants.ONSET_BEATS] + node.data[OnsetDataConstants.DURATION_BEATS]
        
        # Max next onset is node onset + its duration (the onset of the "next" potential symbol)
        return max(node_end_onset(node) for node in self._nodes)
        
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
            node.data[OnsetDataConstants.ONSET_BEATS] += value
        # Total staff duration should not change
        assert length_before == self.get_duration()


class _OnsetSystemWrapper:
    """
    Holds reference to multiple staffs that together
    form a system.
    """
    def __init__(self, staffs: list[_OnsetStaffWrapper]) -> None:
        assert len(staffs) > 0
        self._staffs = sorted(staffs, key=lambda x: x.top)
    
    @property
    def top(self) -> int:
        return min(x.top for x in self._staffs)

    @classmethod
    def from_graph(cls, graph: NotationGraph) -> list[Self]:
        systems = group_staffs_into_systems(graph.vertices)
        output: list[Self] = []
        for system in systems:
            output.append(
                cls([_OnsetStaffWrapper.from_staff(graph, staff) for staff in system])
            )
        return sorted(output, key=lambda x: x.top)
    
    def get_start_onset(self) -> Fraction:
        return min(s.get_start_onset() for s in self._staffs)
    
    def get_end_onset(self) -> Fraction:
        return max(s.get_end_onset() for s in self._staffs)
    
    def get_duration(self) -> Fraction:
        return self.get_end_onset() - self.get_start_onset()
    
    def offset_onset(self, value: Fraction):
        """
        Changes the onset of duration-bearing symbols simultaneously,
        effectively postponing the onset of the system in the global context.

        :param value: Value to offset all related offsets by
        """
        length_before = self.get_duration()
        for sw in self._staffs:
            sw.offset_onset(value)
        # Total system duration should not change
        assert length_before == self.get_duration()
    
    @staticmethod
    def _has_different_numbers(list_: list[Any]) -> bool:
        """
        Returns true if there are at last two different elements.
        """
        return any(x != list_[0] for x in list_[1:])
    
    def is_synchronized(self) -> bool:
        """
        Checks if all staffs within this system end and start on the same onset.
        Writes warnings to log with detailed information, if any discrepancy is found.

        :return: True if all staffs are synchronized
        """
        is_start_sync = not self._has_different_numbers(
            [x.get_start_onset() for x in self._staffs]
        )
        is_end_sync = not self._has_different_numbers(
            [x.get_end_onset() for x in self._staffs]
        )

        if not is_start_sync:
            logger.info("Staffs in system are not synchronized on start:")
            logger.info(
                "System contents '(staff_id, onset)': "
                f"{', '.join([f'({sw.parent_staff_id}, {str(sw.get_start_onset())})' for sw in self._staffs])}"
            )
        if not is_end_sync:
            logger.info("Staffs in system are not synchronized on end:")
            logger.info(
                "System contents '(staff_id, onset)': "
                f"{', '.join([f'({sw.parent_staff_id}, {str(sw.get_end_onset())})' for sw in self._staffs])}"
            )

        return is_start_sync and is_end_sync


def _add_onset_data_to_node(
    node: Node, onset: Fraction, duration: Fraction, duration_wo_m: Fraction
):
    node.data[OnsetDataConstants.ONSET_BEATS] = onset
    node.data[OnsetDataConstants.DURATION_BEATS] = duration
    node.data[OnsetDataConstants.DURATION_BEATS_WO_M] = duration_wo_m


class _GraceGroupWrapper:
    """
    Grace Group is an internal representation for groups
    of grace notes that are children of the same notehead.

    I resolves the ordering of the grace notes.
    Even though grace notes have no duration and no onset,
    internally they have:

    - onset, based on their order, integer from 0 to N-1
    - duration, 0
    - duration without modifiers, 0

    This graph component has to be a path.
    """        
    def __init__(self, notes: list[Node]) -> None:
        self._notes = notes
        self._valid = self._is_valid_graph()
        if not self._valid:
            logger.warning(f"Grace note graph not valid: {', '.join([str(x.id) for x in self._notes])}")
        else:
            logger.debug(f"Grace note graph is valid: {', '.join([str(x.id) for x in self._notes])}")
    
    @staticmethod
    def _sort_with_queue(nodes: list[Node]) -> list[Node]:
        output: list[Node] = []
        q = [x for x in nodes if len(x.precedence_inlinks) == 0 and len(x.precedence_outlinks) == 1]
        assert len(q) == 1
        current = q[0]
        mapping = {x.id: x for x in nodes}

        # traverse the path
        while len(current.precedence_outlinks) > 0:
            output.append(current)
            assert len(current.precedence_outlinks) == 1
            current = mapping[current.precedence_outlinks[0]]
        output.append(current)

        logger.debug(f"Sorted to: {[x.id for x in output]}")

        assert len(nodes) == len(output)
        return output
    
    @staticmethod
    def _sort_left_to_right(nodes: list[Node]) -> list[Node]:
        # There is no way to represent polyphonic grace notes in MusicXML,
        # in the end we are sorting them from left to right anyway.
        return sorted(nodes, key=lambda x: x.left)

    def _sort(self):
        """
        Sorts contained grace notes into order
        in which they should appear in an MusicXML outputs.

        If the graph is valid, defined by the notes,
        the notes are sorted based on precedence linkage,
        the graph is a path.
        If the graph is not valid, the notes are simply sorted
        from left to right based on their image coordinates.
        """
        if self._valid:
            self._notes = self._sort_with_queue(self._notes)
        else:
            self._notes = self._sort_left_to_right(self._notes)

    def compute(self) -> tuple[dict[int, Fraction], dict[int, Fraction], dict[int, Fraction]]:
        self._sort()
        onsets, durations, durations_wo_m = dict(), dict(), dict()
        for i, note in enumerate(self._notes):
            onsets[note.id] = Fraction(i)
            durations[note.id] = Fraction(0)
            durations_wo_m[note.id] = Fraction(0)
                
        for node in self._notes:
            _add_onset_data_to_node(
                node, onsets[node.id], durations[node.id], durations_wo_m[node.id]
            )
        
        return onsets, durations, durations_wo_m

    @classmethod
    def compute_multiple(cls, groups: list[Self]) -> tuple[dict[int, Fraction], dict[int, Fraction], dict[int, Fraction]]:
        onsets, durations, durations_wo_m = dict(), dict(), dict()
        for g in groups:
            o, d, w = g.compute()
            onsets |= o
            durations |= d
            durations_wo_m |= w
        
        return onsets, durations, durations_wo_m

    def _is_valid_graph(self) -> bool:
        # graph is a path
        # - one source,
        # - one sink,
        # - all other have to have one inlink a one outlink
        source, sink = 0, 0
        for note in self._notes:
            if len(note.precedence_inlinks) == 0 and len(note.precedence_outlinks) == 1:
                source += 1
                if source > 1:
                    return False
            elif len(note.precedence_inlinks) == 1 and len(note.precedence_outlinks) == 0:
                sink += 1
                if sink > 1:
                    return False
            elif len(note.precedence_inlinks) == 1 and len(note.precedence_outlinks) == 1:
                pass
            else:
                return False
        return True

    @classmethod
    def from_graph(cls, graph: NotationGraph) -> list[Self]:
        output: list[Self] = []
        for notehead in graph.filter_vertices(InferenceEngineConstants.NONGRACE_NOTEHEAD_CLASS_NAMES):
            grace = graph.children(notehead, class_filter=InferenceEngineConstants.GRACE_NOTEHEAD_CLASS_NAMES)
            if len(grace) > 0:
                output.append(cls(grace))
        return output

class _GraceOnsetInference:
    """
    Computes the ordering of grace notes within each group -
    grace notes that are linked to the same notehead.
    """
    _CONST = InferenceEngineConstants()

    def __init__(self, strategy: Optional[BaseOnsetsInferenceStrategy] = None):
        if strategy is None:
            strategy = BaseOnsetsInferenceStrategy()
        self._strategy = strategy
    
    def __call__(
            self,
            graph: NotationGraph
        ) -> tuple[dict[int, Fraction], dict[int, Fraction], dict[int, Fraction]]:
        ggw = _GraceGroupWrapper.from_graph(graph)
        logger.info(f"We have {len(ggw)} grace note groups")
        return _GraceGroupWrapper.compute_multiple(ggw)


@dataclass(frozen=True)
class OnsetsInferenceEngineWrapperStrategy(BaseOnsetsInferenceStrategy):
    link_sinks_to_sources_at_ends_and_starts_of_systems: bool = False
    with_grace_notes: bool = True


class OnsetInferenceEngineWrapper:
    _CONST = InferenceEngineConstants()

    def __init__(self, strategy: Optional[OnsetsInferenceEngineWrapperStrategy] = None):
        if strategy is None:
            strategy = OnsetsInferenceEngineWrapperStrategy()
        self._strategy = strategy
        self._engine = OnsetsInferenceEngine(self._strategy)
        self._grace_engine = _GraceOnsetInference(self._strategy)
        
    def __call__(
            self,
            graph: NotationGraph
        ) -> tuple[dict[int, Fraction], dict[int, Fraction], dict[int, Fraction]]:
        """
        Computes the onsets and durations for duration-related symbols,
        stores them inside the ``data`` of each affected notehead.

        For retrieval of particular data as a ``dict[node_id, data]``
        use ``NotationGraph`` function ``collect_data``.

        :param graph: ``NotationGraph`` instance to process

        :return: Tuple of onsets, durations, and duration without modifiers
        """
        onsets, durations, durations_wo_m = self._engine(graph)

        for node in graph.filter_vertices(self._CONST.classes_bearing_duration):
            _add_onset_data_to_node(
                node, onsets[node.id], durations[node.id], durations_wo_m[node.id]
            )
        
        # Every linkage and onsets has been handled by the old implementation.
        if self._strategy.link_sinks_to_sources_at_ends_and_starts_of_systems:
            return onsets, durations, durations_wo_m

        # If onsets we processed system by system ...
        # Now, all systems begin at onset 0.
        # Top sorted systems, we offset every system by the total current offset.
        sysws = _OnsetSystemWrapper.from_graph(graph)

        assert all(x.get_start_onset() == 0 for x in sysws)

        current_offset = sysws[0].get_duration()
        for index in range(1, len(sysws)):
            sysws[index].offset_onset(current_offset)
            current_offset += sysws[index].get_duration()

        for sysw in sysws:
            sysw.is_synchronized()

        if self._strategy.with_grace_notes:
            g_onsets, g_durations, g_durations_wo_m = self._grace_engine(graph)
            onsets |= g_onsets
            durations |= g_durations
            durations_wo_m |= g_durations_wo_m
        
        return onsets, durations, durations_wo_m
