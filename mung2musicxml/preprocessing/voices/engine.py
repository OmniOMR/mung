
from typing import TypeVar, Optional
from collections import defaultdict
from enum import StrEnum
from mung import NotationGraph, Node
from mung.graph import group_by_system_measure, UnionFind
from mung.subevents_from_nodes import subevents_from_list_of_symbols
from mung.constants import (
    ClassNameConstants as C,
    InferenceEngineConstants as I,
    OnsetDataConstants as O
)
from .strategy import VoiceEngineStrategy
from .utils import find_all_durable_groups, find_staff_for_container, _VoiceNode
from .voice_subevent import _Subevent
from ..instruments import get_instrument_groups_from_systems
from ...logger import logger
from ...utils import WrapperGraph
from ...inference import Pitch


T = TypeVar("T")

class VoiceDataConstants(StrEnum):
    VOICE_ID = "voice"


class VoiceEngine:
    """
    When inferring voices, we first need to split the score into smaller pieces -
    system measures.

    ## Building the Voice Graph

    Inside each system measure, we find a staff for every durable
    to be snapped to temporarily.
    
    In score, there can be objects
    spanning across multiple staffs - beams, tremolos and tuples.
    Durables located inside these objects must all be part
    of the same voice.
    Durables inside these objects are assigned to staff
    that has the earliest durable (smallest onset).

    Chords (notes connected by a stem) are each one subevent,
    and are processed as a whole. If durables inside
    span across multiple staffs, the topmost one
    is chosen.

    Then the Voice Graph is build - for each staff,
    we collect all durables in the system measure
    and group them into subevents. Between two subevents
    an edge if created if:

    - They are connected by a precedence edge,
    - or the child subevent has no precedence inlinks and the parent subevent is the closest one preceding it.
    """
    def __init__(self, strategy: Optional[VoiceEngineStrategy] = None):
        self._strategy = strategy if strategy is not None else VoiceEngineStrategy()
        self._graph: NotationGraph = None
        self._beam_to_staff: dict[Node, Node] = None
        self._tremolo_to_staff: dict[Node, Node] = None
        self._tuple_to_staff: dict[Node, Node] = None
        self._staff_to_offset: dict[Node, int] = None

    def __call__(self, graph: NotationGraph) -> dict[Node, int]:
        self._initialize_computation(graph)
        output = self.infer_voices()
        self._reset_computation()
        return output
    
    def _initialize_computation(self, graph: NotationGraph) -> None:
        self._graph = graph
        self._compute_beams_to_staff()
        self._compute_tremolos_to_staff()
        self._compute_tuples_to_staff()
        self._compute_staffs_to_offset()
    
    def _reset_computation(self) -> None:
        self._graph = None
        self._beam_to_staff = None
        self._tremolo_to_staff = None
        self._tuple_to_staff = None
        self._staff_to_offset= None

    def _find_nested_beams(self) -> list[list[Node]]:
        """
        Finds all groups of beams that share at least one symbol
        (notehead full, half and rests).
        """
        groups = [
            self._graph.children(n, class_filter=C.NoteheadAttachments.BEAM)
            for n in self._graph.filter_vertices([C.Noteheads.NOTEHEAD_BLACK, C.Noteheads.NOTEHEAD_HALF] + I.REST_CLASS_NAMES)
        ]
        return UnionFind.merge_groups(groups)

    def _compute_beams_to_staff(self) -> None:
        """
        Finds all beams and fills in the ``beam_to_staff`` dictionary.
        """
        self._beam_to_staff = {}
        for group in self._find_nested_beams():
            # find topmost staff in group
            _, staff = min([find_staff_for_container(b, self._graph) for b in group], key=lambda n: (n[0], n[1].id))
            
            for beam in group:
                self._beam_to_staff[beam] = staff
    
    def _compute_tremolos_to_staff(self) -> None:
        """
        Finds all tremolos and fills in the ``tremolo_to_staff`` dictionary.
        """
        self._tremolo_to_staff = {}
        for tremolo in self._graph.filter_vertices(C.Tremolo.TREMOLO_BEAM):
            _, staff = find_staff_for_container(tremolo, self._graph)
            self._tremolo_to_staff[tremolo] = staff

    def _compute_tuples_to_staff(self) -> None:
        """
        Finds all tuples and fills in the ``tuple_to_staff`` dictionary.
        """
        self._tuple_to_staff = {}
        for tuple_ in self._graph.filter_vertices(C.Tuplets.TUPLET):
            _, staff = find_staff_for_container(tuple_, self._graph)
            self._tuple_to_staff[tuple_] = staff
    
    def _compute_staffs_to_offset(self) -> None:
        """
        Computes the offset for each staff inside a grand staff.
        `0` for the top staff, `1` for the bottom one.
        If staff is not part of a grand staff, its offset is `0`.
        """
        self._staff_to_offset: dict[Node, int] = {}
        instrument_groups = get_instrument_groups_from_systems(self._graph)
        for group in instrument_groups:
            for instrument in group:
                for offset, staff in enumerate(sorted(instrument, key=lambda s: s.top)):
                    self._staff_to_offset[staff] = offset
            
    def _link_subevents_to_staff(self, subevents: list[_Subevent]) -> defaultdict[Node, list[_Subevent]]:
        """
        Returns a dictionary of subevents to staff. Uses the retrieved staffs for beams, tremolos and tuples.
        Default to topmost staff, if event is not a part of any of these cross staff objects.
        """
        subevents_to_staff: defaultdict[Node, list[_Subevent]] = defaultdict(list)

        for subevent in subevents:
            beam = subevent.get_any(self._graph, C.NoteheadAttachments.BEAM)
            tremolo = subevent.get_any(self._graph, C.Tremolo.TREMOLO_BEAM)
            tuple_ = subevent.get_any(self._graph, C.Tuplets.TUPLET)

            if beam is not None:
                subevents_to_staff[self._beam_to_staff[beam]].append(subevent)
            elif tremolo is not None:
                subevents_to_staff[self._tremolo_to_staff[tremolo]].append(subevent)
            elif tuple_ is not None:
                subevents_to_staff[self._tuple_to_staff[tuple_]].append(subevent)
            else:
                subevents_to_staff[subevent.get_staff(self._graph)].append(subevent)
        
        return subevents_to_staff
    
    def _construct_voice_graph_for_measure(self, subevents: list[_Subevent]) -> WrapperGraph:
        """
        Constructs a Voice Graph from the given list of subevents.

        Fills in gaps, tries to link subevent with no parents to another,
        closest preceding subevent.
        """
        
        # create initial graph
        wg = WrapperGraph.from_other_graph(
            subevents,
            get_neighbors=lambda n: n.get_neighbors(subevents, self._graph),
            get_duration=lambda n: n.get_duration(),
            get_priority=lambda n: n.get_priority(),
            get_start=lambda n: n.get_start_onset(),
        )

        def get_candidate(child: _VoiceNode, others: list[_VoiceNode]) -> Optional[_VoiceNode]:
            """
            Finds the closest preceding Voice Node for a given Voice Node.
            """
            output = [o for o in others if o.obj.get_end_onset() <= child.obj.get_start_onset()]
            if len(output) == 0:
                return None
            return max(output, key=lambda vn: (vn.obj.get_end_onset(), vn.obj.get_priority()))
        
        # try to connect disconnected components nodes, fill in gaps
        for node in wg:
            if len(node.parents) == 0:
                potential_parent = get_candidate(node, wg._nodes)
                if potential_parent is None:
                    logger.debug(f"Unable to find any precedence ancestor in voice for {node}")
                else:
                    parent = potential_parent
                    logger.warning(f"Filling in gap for voice inference, connecting {parent} -> {node}")
                    wg.add_edge(parent, node)
        
        return wg
    
    @staticmethod
    def _add_voice_data_to_nodes(voice_data: dict[Node, int]) -> None:
        for node, voice_id in voice_data.items():
            node.data[VoiceDataConstants.VOICE_ID] = voice_id
    
    @staticmethod
    def _get_voice_data_from_node(node: Node) -> int:
        return node.data[VoiceDataConstants.VOICE_ID]
    
    def _infer_voices_for_grace_notes(self) -> dict[Node, int]:
        """
        Infers voice ids for grace notes by getting the voice id of their parents.
        """
        grace_notes_to_voices: dict[Node, int] = {}
        notes = self._graph.filter_vertices(I.GRACE_NOTEHEAD_CLASS_NAMES)
        for note in notes:
            parents = self._graph.parents(note, class_filter=I.NONGRACE_NOTEHEAD_CLASS_NAMES)
            
            if len(parents) == 0:
                logger.warning(f"No parent notehead found for {note.class_name} {note.id}, returning default 1")
                parent_voice_id = 1
            else:
                parent_voice_id = min(self._get_voice_data_from_node(p) for p in parents)
            
            grace_notes_to_voices[note] = parent_voice_id
        
        return grace_notes_to_voices
    
    def _durable_voice_with_grand_staff_offset(self, node: Node, current_staff: Node, computed_voice: int) -> int:
        """
        Maps inferred voice id `1-4` to grand staff voices. `1-4`
        for the top staff and `5-8` for the bottom staff,
        if `OFFSET_VOICES_IN_GRAND_STAFF` in strategy is true.
        """
        # return computed_voice
        if not self._strategy.OFFSET_VOICES_IN_GRAND_STAFF:
            return computed_voice
        
        offset = self._staff_to_offset[current_staff]
        
        return computed_voice + self._strategy.OFFSET_VALUE * offset
    
    def _sort_voices(self, voices: dict[_VoiceNode, int]) -> dict[_VoiceNode, int]:
        """
        Sorts voices inside a measure based on total length played by the voice
        and the average pitch inside the voice.
        """
        def get_average_pitch(subevents: list[_VoiceNode]) -> float:
            """
            Compute average pitch for a list of subevents.
            If no pitch is found, returns `-1`.
            """
            pitches: list[Pitch] = []
            for s in subevents:
                pitches.extend(s.obj.get_pitches())
            if len(pitches) == 0:
                return -1
            return sum(x.to_midi() for x in pitches) / len(pitches)
    
        voice_to_nodes: defaultdict[int, list[_VoiceNode]] = defaultdict(list)
        for subevent, voice_id in voices.items():
            voice_to_nodes[voice_id].append(subevent)
        voice_ids = set(voice_to_nodes.keys())
        voice_ids = sorted(
            voice_ids, key=lambda _id: (
                sum([x.obj.get_duration() for x in voice_to_nodes[_id]]),
                get_average_pitch(voice_to_nodes[_id])
            ), reverse=True
        )
        mapping = dict()
        for new_value, old_value in enumerate(voice_ids):
            mapping[old_value] = new_value + 1

        new_voices = dict()
        for node, voice_id in voices.items():
            new_voices[node] = mapping[voice_id] 
        return new_voices
        
    def infer_voices(self) -> dict[Node, int]:
        """
        Infers voice ids for all durables and grace notes.
        """
        durables_to_voices: dict[Node, int] = {}

        system_measures = group_by_system_measure(self._graph)

        for i, sm in enumerate(system_measures):
            logger.debug(f"Processing system measure {i}")

            nodes = [n for n in sm if n.class_name in I.CLASSES_BEARING_DURATIONS]
            assert all((O.ONSET_BEATS in n.data) for n in nodes)

            subevents = [_Subevent(v) for v in subevents_from_list_of_symbols(nodes, self._graph)]

            # link large constructions - cross staff spanning tremolos and beams - to one staff
            subevents_to_staff = self._link_subevents_to_staff(subevents)
            
            for index, (current_staff, current_staff_subevents) in enumerate(subevents_to_staff.items()):
                current_staff_subevents: list[_Subevent]
                logger.debug(f"Staff {current_staff.id}: {', '.join(str(m) for m in current_staff_subevents)}")

                wg = self._construct_voice_graph_for_measure(current_staff_subevents)
                
                groups = find_all_durable_groups(wg._nodes, self._graph)
                if len(groups) > 0:
                    groups = UnionFind.merge_groups(groups)
                voices = wg.assign_voices(groups=groups)
                voices = self._sort_voices(voices)

                for subevent_node, voice_id in voices.items():
                    for durable in subevent_node.obj:
                        durable: Node
                        final_voice_id = self._durable_voice_with_grand_staff_offset(durable, current_staff, voice_id)
                        durables_to_voices[durable] = final_voice_id
                        durable.data[VoiceDataConstants.VOICE_ID] = final_voice_id
                    
                    logger.debug(f"Inferred voice for: {subevent_node}, {voice_id}")

        durables_to_voices.update(self._infer_voices_for_grace_notes())

        return durables_to_voices
    