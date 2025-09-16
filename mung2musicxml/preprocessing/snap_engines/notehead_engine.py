from mung.constants import InferenceEngineConstants, ClassNamesConstants
from mung import NotationGraph, Node
from typing import Any, Optional, Callable
from itertools import chain

from .strategies import NoteheadSnapEngineStrategy
from .snap_constants import StaffDirectionFromNotehead, StaffAssignmentFallbackStrategy
from .utils import check_leger_line_assignments, count_ids_check_for_draw, log_total
from ..staff_wrapper import StaffWrapper
from ...logger import logger


class NoteheadSnapEngine:
    _CONST = InferenceEngineConstants()

    def __init__(self, strategy: Optional[NoteheadSnapEngineStrategy] = None):
        """
        Parameter ``staff_wrappers`` makes it possible to share
        created ``StaffWrapper``s between multiple other snap engines,
        to save some time creating new instances inside every engine.
        """
        self._strategy = strategy if strategy is not None else NoteheadSnapEngineStrategy()
        self._graph: NotationGraph = None #type: ignore
        self._staff_wrappers: list[StaffWrapper] = None #type: ignore
    
    def __call__(self, graph: NotationGraph, staff_wrappers: Optional[list[StaffWrapper]] = None) -> None:
        self.snap_noteheads_to_staffs(graph, staff_wrappers)
        self.reset()
    
    @classmethod
    def run(
        cls,
        graph: NotationGraph,
        staff_wrappers: Optional[list[StaffWrapper]] = None,
        strategy: Optional[NoteheadSnapEngineStrategy] = None
        ):
        cls(strategy)(graph, staff_wrappers)
    
    def _set_wrappers(self, staff_wrappers: list[StaffWrapper]) -> None:
        self._staff_wrappers = staff_wrappers
    
    def _set_graph(self, graph: NotationGraph) -> None:
        self._graph = graph
    
    def reset(self) -> None:
        self._graph = None #type: ignore
        self._staff_wrappers = None #type: ignore
    
    def snap_noteheads_to_staffs(self, graph: NotationGraph, staff_wrappers: Optional[list[StaffWrapper]] = None) -> None:
        """
        Snaps noteheads in the graph to staffs
        and optionally to staffpositions (stafflines, staffspaces).
        """
        self._set_wrappers(StaffWrapper.from_graph(graph) if staff_wrappers is None else staff_wrappers)
        self._set_graph(graph)

        noteheads = self._graph.filter_vertices(self._CONST.NONGRACE_NOTEHEAD_CLASS_NAMES)
        # Split noteheads to three categories based on the difficulty of their assignment to staff:
        # - No leger lines
        # - Two and more leger lines
        # - One leger line (most difficult)
        # This allows us to precompute staff assignment for noteheads which the more difficult
        # computations could refer to.
        def _process_noteheads(noteheads: list[Node]) -> int:
            total = 0
            for notehead in noteheads:
                if self._has_leger_line(notehead):
                    self.snap_notehead_with_leger_lines_to_staff(notehead)
                else:
                    self.snap_notehead_without_leger_lines_to_staff(notehead)
                total += 1
            return total

        no_lines = []
        one_line = []
        two_or_more_lines = []
        for notehead in noteheads:
            num_lines = len(self._graph.children(notehead, class_filter=ClassNamesConstants.LEGER_LINE))
            match num_lines:
                case 0:
                    no_lines.append(notehead)
                case 1:
                    one_line.append(notehead) 
                case _:
                    two_or_more_lines.append(notehead)

        total = 0

        assert len(no_lines) + len(one_line) + len(two_or_more_lines) == len(noteheads)
        
        total += _process_noteheads(no_lines)
        total += _process_noteheads(two_or_more_lines)
        total += _process_noteheads(one_line)
        
        log_total(total, self._CONST.NONGRACE_NOTEHEAD_CLASS_NAMES)

        snapped, total = self._snap_grace_notes_to_staff()
        logger.info(f"Snapped {snapped}/{total} {', '.join(InferenceEngineConstants.GRACE_NOTEHEAD_CLASS_NAMES)} to staffs.")
    
    def snap_notehead_with_leger_lines_to_staff(self, notehead: Node):
        """
        Snaps given notehead to a staff - creates an edge in the graph.

        The algorithm:

        - Find the direction in which to search for a staff based on leger lines direction.
        - If all staffs above/under, skip the complex algorithm.
        - Slight misalignment for a notehead with one leger line can lead to a greater error.
        - Rather than rely on "one on one" relations between notehead and a leger line,
          we compute the direction of the staff line using all the lines at once.
        
            - For noteheads with multiple leger lines:
                - Raise warning when there are lines above and also under at the same time
                    or the notehead is on multiple lines.
                - Sum up the distances between notehead and its leger lines,
                    return value based on its direction. (Slight misalignments of lines
                    directly around the notehead are overvoted by the direction of lines
                    further away from the notehead.)
        
            - For single-leger-line noteheads:
                - Try to find another notehead linked to the same leger line with at least two
                    leger lines and compute the direction for the other notehead (described above).
                - Fallback: 
                    - Heuristics, a warning will be given.
                    - Assign it to most common staff in a chord (if the notehead is part of any).
                    - Assign it to most common staff in a set of noteheads connected by beams
                        (if the notehead is part of any).
                    - Assign it to the closest staff.
                    - Optional implemented fallback: Compute the direction based on stem direction - up/down.
        """
        leger_lines = self._graph.children(notehead, ClassNamesConstants.LEGER_LINE)
        assert len(leger_lines) > 0
        distance_from_staffs = [(sw.vertical_distance_from_geometry(notehead), sw.parent_staff_id)
                                for sw in self._staff_wrappers]        
        all_above, all_under = self._all_above(distance_from_staffs), self._all_under(distance_from_staffs)

        # Filter out noteheads that are somewhere in the middle of two staffs
        if not (all_above or all_under):
            if len(leger_lines) == 1:
                leger_line = leger_lines[0]
                # If notehead is all above or all under the leger line,
                # the task is easy.
                if notehead.bottom <= leger_line.top:
                    staff_direction = StaffDirectionFromNotehead.UNDER
                elif notehead.top >= leger_line.bottom:
                    staff_direction = StaffDirectionFromNotehead.ABOVE
                else:
                    # If they intersect in anyway, small noise can cause great mistakes,
                    # try to find other notehead that shares the same leger line.
                    other_notehead = self._find_other_notehead_sharing_leger_line(notehead)
                    if other_notehead is not None:
                        staff_id = self._get_notehead_staff_id(other_notehead)
                        logger.info(f"Notehead {notehead.id} assigned to staff {staff_id} "
                                     f"based on shared leger line with notehead {other_notehead.id}.")
                        self._graph.add_edge(notehead.id, staff_id)
                        return
                    
                    # Fallback
                    # All of these approaches are heuristics, the user should be warned
                    else:
                        staff_id = self._single_leger_line_fallback(notehead, distance_from_staffs)
                        self._graph.add_edge(notehead.id, staff_id)
                        return
                    
            # Compute the direction based on multiple leger lines.
            else:
                check_leger_line_assignments(notehead, leger_lines)
                staff_direction = self.get_staff_direction_based_on_notehead_and_leger_lines_position(notehead, leger_lines)
        
        # Process notehead that is above or under all the staffs
        else:
            staff_direction = StaffDirectionFromNotehead.ABOVE if all_above else StaffDirectionFromNotehead.UNDER
       
        # -------------------

        # Interpret direction
        if staff_direction == StaffDirectionFromNotehead.UNDEFINED:
            absolute_distance_from_staffs = [(sw.absolute_vertical_distance_from_geometry(notehead), sw.parent_staff_id)
                                             for sw in self._staff_wrappers]
            distance, staff_id = min(absolute_distance_from_staffs)

        elif staff_direction == StaffDirectionFromNotehead.UNDER:
            distance, staff_id = self._find_first_staff_under(distance_from_staffs)

        elif staff_direction == StaffDirectionFromNotehead.ABOVE:
            distance, staff_id = self._find_fist_staff_above(distance_from_staffs)

        else:
            raise ValueError()
            
        self._graph.add_edge(notehead.id, staff_id)

        logger.debug(f"Closest staff for node {notehead.id} with leger lines "
                      f"is {staff_id}, distance is {abs(distance)}")
    
    
    def _single_leger_line_fallback(self, notehead: Node, distance_from_staffs: list[tuple[int, int]]) -> int:
        """
        Returns the chosen staff id.

        - Heuristics, a warning will be given.
        - Assign it to most common staff in a chord (if the notehead is part of any).
        - Assign it to most common staff in a set of noteheads connected by beams
            (if the notehead is part of any).
        - Compute the direction based on stem direction - up/down.
        - If all above fails, assign it to the closest staff.
        """
        strategy_map: dict[StaffAssignmentFallbackStrategy, Callable[[], Optional[int]]] = {
            StaffAssignmentFallbackStrategy.CHORD:
            lambda: self._fallback_chord(notehead),

            StaffAssignmentFallbackStrategy.BEAM:
            lambda: self._fallback_beam(notehead),

            StaffAssignmentFallbackStrategy.STEM:
            lambda: self._fallback_stem(notehead, distance_from_staffs),

            StaffAssignmentFallbackStrategy.CLOSEST:
            lambda: self._fallback_closest(distance_from_staffs)
        }

        for strategy in self._strategy.STAFF_ASSIGNMENT_FALLBACK_PRIORITY:
            fallback = strategy_map[strategy]
            staff_id = fallback()
            if staff_id is not None:
                logger.warning(f"Fallback '{strategy.name}' for notehead {notehead.id} found staff {staff_id}, "
                                "please check this assignment manually.")
                return staff_id
        
        raise ValueError()
    
    def snap_notehead_without_leger_lines_to_staff(self, notehead: Node):
        """
        Snaps given notehead to a staff positions and its staff
        - creates edges in the graph.

        The best staff position is found by minimizing the distance
        between the notehead and any staff position in the graph.
        The distances are computed based on masks of the positions.
        """
        distance, position_id = min(
            chain.from_iterable(
                sw.get_absolute_distances_from_staff_positions_with_ids(notehead)
                for sw in self._staff_wrappers
            ),
            key=lambda x: x[0]
        )
        staff_id = self._get_positions_parent_staff_id(position_id)
        
        self._graph.add_edge(notehead.id, staff_id)
        self._graph.add_edge(notehead.id, position_id)
        
        logger.debug(
            f"Closest staff position for {notehead.id} is {position_id} "
            f"belonging to staff {staff_id}, distance is {distance}")
        
    @staticmethod
    def get_staff_direction_based_on_notehead_and_leger_lines_position(notehead: Node, leger_lines: list[Node]) -> StaffDirectionFromNotehead:
        """
        Returns the assumed the direction of staff from the given notehead and its leger lines.
        Returns an instance of ``StaffDirectionFromNotehead``.
        """
        assert len(leger_lines) > 0
        distances_from_notehead = sum([leger_line.middle[0] - notehead.middle[0] for leger_line in leger_lines])
        return (StaffDirectionFromNotehead.UNDER
                if distances_from_notehead >= 0
                else StaffDirectionFromNotehead.ABOVE)

    def _has_leger_line(self, node: Node) -> bool:
        """
        Returns true, if given node has at least one leger line connected to it as a child.
        """
        return len(self._graph.children(node, ClassNamesConstants.LEGER_LINE)) > 0

    @staticmethod
    def _find_first_staff_under(staff_distances_with_ids: list[tuple[int,int]]) -> tuple[int,int]:
        """
        Assumes that given staff distances are sorted by distance from the top of the page.
        """
        for distance, staff_id in staff_distances_with_ids:
            if distance >= 0:
                return (distance, staff_id)
        raise ValueError()
    
    @staticmethod
    def _find_fist_staff_above(staff_distances_with_ids: list[tuple[int,int]]) -> tuple[int,int]:
        """
        Assumes that given staff distances are sorted by distance from the top of the page.
        """
        for distance, staff_id in staff_distances_with_ids[::-1]:
            if distance <= 0:
                return (distance, staff_id)
        raise ValueError()
    
    @staticmethod
    def _all_above(staff_distances_with_ids: list[tuple[int,int]]) -> bool:
        """
        Returns true, if all the given distances hint that the notehead is above all the stafflines.
        """
        return all(x[0] < 0 for x in staff_distances_with_ids)

    @staticmethod
    def _all_under(staff_distances_with_ids: list[tuple[int,int]]) -> bool:
        """
        Returns true, if all the given distances hint that the notehead is under all the stafflines.
        """
        return all(x[0] > 0 for x in staff_distances_with_ids)
    
    def _find_other_notehead_sharing_leger_line(self, notehead: Node) -> Optional[Node]:
        """
        Returns a notehead that shares a leger line with the given notehead
        and has two and more leger lines. If not found, returns ``None`` .
        """
        leger_lines = self._graph.children(notehead, class_filter=ClassNamesConstants.LEGER_LINE)
        assert len(leger_lines) == 1
        leger_line = leger_lines[0]

        # Get noteheads connected to the same leger line
        other_noteheads = self._graph.parents(leger_line, class_filter=NoteheadSnapEngine._CONST.NOTEHEAD_CLASS_NAMES)
        # Compute number of assigned leger lines to each found notehead, (Node, # leger lines)
        other_noteheads = [
            (x, len(self._graph.children(x, class_filter=ClassNamesConstants.LEGER_LINE)))
            for x in other_noteheads
        ]
        # Find notehead with the most leger lines - assume higher precision
        max_leger_lines_notehead, count = max(other_noteheads, key=lambda x: x[1])
        
        if max_leger_lines_notehead.id == notehead.id or count < 2:
            return None
        else:
            return max_leger_lines_notehead
    
    def _get_notehead_staff_id(self, notehead: Node) -> int:
        """
        Finds and returns ID of staff to which the given notehead is assigned.
        Crashes if staff is not found or there are more than one staffs connected.
        """
        staffs = self._graph.children(notehead, class_filter=ClassNamesConstants.STAFF)
        assert len(staffs) == 1
        return staffs[0].id
    
    def _get_positions_parent_staff_id(self, position_id: int) -> int:
        staffs = self._graph.parents(position_id, ClassNamesConstants.STAFF)
        if len(staffs) != 1:
            raise ValueError(f"Staffposition {position_id} has wrong number of staff parents: {len(staffs)}:")
        return staffs[0].id
    
    def _find_staff_id_of_other_noteheads_sharing_chord(self, notehead: Node) -> Optional[int]:
        """
        Returns id of a staff that is most common among noteheads
        that share the same chord with the given notehead and a staff is already assigned to them.

        The given notehead has to have exactly one leger line. 
        """
        stems = self._graph.children(notehead, class_filter=ClassNamesConstants.STEM)

        # Cannot resolve multistem chords
        if len(stems) != 1:
            return None
        stem = stems[0]
        
        noteheads_in_chord = [n for n in self._graph.parents(stem, class_filter=self._CONST.NONGRACE_NOTEHEAD_CLASS_NAMES)
            if len(self._graph.children(n, class_filter=ClassNamesConstants.LEGER_LINE)) != 1]
        
        assert notehead not in noteheads_in_chord

        if len(noteheads_in_chord) == 0:
            return None
        
        staff_ids = [self._get_notehead_staff_id(n) for n in noteheads_in_chord]
        return count_ids_check_for_draw(staff_ids)
    
    def _find_staff_id_of_other_noteheads_sharing_beams(self, notehead: Node) -> Optional[int]:
        """
        Returns id of a staff that is most common among noteheads
        that share beams with the given notehead and a staff is already assigned to them.

        The given notehead has to have exactly one leger line. 
        """
        beams = self._graph.children(notehead, class_filter=ClassNamesConstants.BEAM)
        if len(beams) == 0:
            return None
        
        # Filter out noteheads whose assignment to staff is "trivial":
        # - Has no leger lines
        # - Has two or more leger lines
        # -> Does not have exactly one leger line
        noteheads = [other_notehead for other_notehead in chain.from_iterable(
            self._graph.parents(beam, class_filter=self._CONST.NONGRACE_NOTEHEAD_CLASS_NAMES)
            for beam in beams
        ) if len(self._graph.children(other_notehead, class_filter=ClassNamesConstants.LEGER_LINE)) != 1]

        noteheads = list(set(noteheads))
        assert notehead not in noteheads
        
        if len(noteheads) == 0:
            return None
        
        staff_ids = [self._get_notehead_staff_id(n) for n in noteheads]
        return count_ids_check_for_draw(staff_ids)
    
    def _direction_based_on_stem(self, notehead: Node) -> Optional[StaffDirectionFromNotehead]:
        stems = self._graph.children(notehead, class_filter=ClassNamesConstants.STEM)

        # Cannot resolve multistem chords
        if len(stems) != 1:
            return None
        stem = stems[0]

        return (StaffDirectionFromNotehead.ABOVE
                if self._graph.is_stem_direction_above(notehead, stem)
                else StaffDirectionFromNotehead.UNDER)
    
    def _fallback_chord(self, notehead: Node) -> Optional[int]:
        # Assign staff based on noteheads connected to by chord
        return self._find_staff_id_of_other_noteheads_sharing_chord(notehead)
    
    def _fallback_beam(self, notehead: Node) -> Optional[int]:
        # Assign staff based on noteheads connected to by beams
        return self._find_staff_id_of_other_noteheads_sharing_beams(notehead)
    def _fallback_stem(self, notehead: Node, distance_from_staffs: list[tuple[int, int]]) -> Optional[int]:
        # Get staff direction based on stem direction
        direction = self._direction_based_on_stem(notehead)
        if direction is not None:
            if direction == StaffDirectionFromNotehead.UNDER:
                _, staff_id = self._find_first_staff_under(distance_from_staffs)
            elif direction == StaffDirectionFromNotehead.ABOVE:
                _, staff_id = self._find_fist_staff_above(distance_from_staffs)
            else:
                raise ValueError()
            return staff_id
        
        return None
    
    def _fallback_closest(self, distance_from_staffs: list[tuple[int, int]]) -> int:
        _, staff_id = min(distance_from_staffs, key=lambda x: abs(x[0]))
        return staff_id
    
    def _snap_grace_note_without_leger_lines_to_staff(self, grace: Node, staff_id: int):
        """
        Snaps given notehead to a staff positions and its staff
        - creates edges in the graph.

        The best staff position is found by minimizing the distance
        between the notehead and any staff position in the graph.
        The distances are computed based on masks of the positions.
        """
        sws = [sw for sw in self._staff_wrappers if sw.parent_staff_id == staff_id]
        assert len(sws) == 1
        sw = sws[0]

        distance, position_id = min(
                sw.get_absolute_distances_from_staff_positions_with_ids(grace),
            key=lambda x: x[0]
        )
        self._graph.add_edge(grace.id, position_id)
        
        logger.debug(
            f"Closest staff position for {grace.id} is {position_id}, "
            f"distance is {distance}")
    
    def _snap_grace_notes_to_staff(self) -> tuple[int, int]:
        total = 0
        grace_notes = self._graph.filter_vertices(InferenceEngineConstants.GRACE_NOTEHEAD_CLASS_NAMES)
        for grace_note in grace_notes:
            total += self._process_grace_note(grace_note)
        return total, len(grace_notes)

    def _process_grace_note(self, grace: Node) -> int:
        """
        Snaps grace note to staff based on its parent notehead.

        In MusicXML, the grace note exists only in connection to another note.
        So we snap it based on the regular notehead to which it is assigned,
        if no such notehead is found, we skip the grace notes, as we are
        unable to add it into the final output.

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/examples/grace-element/
        """
        parents = self._graph.parents(
            grace, InferenceEngineConstants.NOTEHEAD_CLASS_NAMES
            )
        
        if len(parents) != 1:
            logger.warning(f"{grace.class_name} {grace.id} has wrong number of parents: "
                           f"{len(parents)}, {[x.id for x in parents]}")
            if len(parents) == 0:
                return 0
        
        parent = parents[0]

        parent_staffs = self._graph.children(parent, ClassNamesConstants.STAFF)
        if len(parent_staffs) != 1:
            logger.warning(f"{parent.class_name} {parent.id} should be linked to exactly one staff")
            if len(parent_staffs) == 0:
                return 0
        
        parent_staff = parent_staffs[0]
        self._graph.add_edge(grace.id, parent_staff.id)

        # Grace notes with leger lines should be snapped to staff only,
        # if there are no leger lines connections, the grace note has to be linked
        # to a staff position.
        self._snap_grace_note_without_leger_lines_to_staff(grace, parent_staff.id)
        return 1




