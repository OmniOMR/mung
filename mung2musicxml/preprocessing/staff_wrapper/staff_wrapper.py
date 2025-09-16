from mung import NotationGraph, Node
from typing import Self
import numpy as np
from fractions import Fraction
from mung.constants import ClassNamesConstants, OnsetDataConstants, WESTERN_NOTATION_STAFFLINE_COUNT, InferenceEngineConstants
from mung.graph import group_by_chord

from .mask_wrapper import MaskAverageIndexWrapper
from ..errors import StafflineCountNotMultipleError, StaffspaceCountNotMultipleError
from ...logger import logger


class StaffWrapper:
    def __init__(self, graph: NotationGraph, staff: Node):
        self._CONST = InferenceEngineConstants()
        self._graph = graph

        stafflines = graph.children(staff, ClassNamesConstants.STAFFLINE)
        staffspaces = graph.children(staff, ClassNamesConstants.STAFFSPACE)

        if len(stafflines) % WESTERN_NOTATION_STAFFLINE_COUNT != 0:
            raise StafflineCountNotMultipleError()
        if len(staffspaces) % (WESTERN_NOTATION_STAFFLINE_COUNT + 1) != 0:
            raise StaffspaceCountNotMultipleError()

        if not staff.class_name == ClassNamesConstants.STAFF:
            raise ValueError(f"Mismatched class name in {staff}")
        if not all(x.class_name == ClassNamesConstants.STAFFLINE for x in stafflines):
            raise ValueError(f"Mismatched class names in {stafflines}")
        if not all(x.class_name == ClassNamesConstants.STAFFSPACE for x in staffspaces):
            raise ValueError(f"Mismatched class names in {stafflines}")

        self.staff = staff
        self.stafflines = sorted(stafflines, key=lambda x: x.top)
        self.__staffline_masks = {line : MaskAverageIndexWrapper(line.mask) for line in self.stafflines} # type: ignore
        self.staffspaces = sorted(staffspaces, key=lambda x: x.top)

    @property
    def mean_staffline_distance(self) -> int:
        return int(np.diff([x.top for x in self.stafflines]).mean())

    @property
    def parent_staff_id(self) -> int:
        """
        Returns the id of the parent staff ``Node`` instance.
        """
        return self.staff.id

    @property
    def top(self) -> int:
        return self.staff.top

    @classmethod
    def from_graph(cls, graph: NotationGraph) -> list[Self]:
        staffs = sorted(graph.filter_vertices(ClassNamesConstants.STAFF), key=lambda x: x.top)
        output = []
        for staff in staffs:
            output.append(cls(graph, staff))
        return output

    def vertical_distance(self, node: Node) -> int:
        return abs(node.middle[0] - self.staff.middle[0])
    
    def get_contained_nodes_bearing_duration(self) -> list[Node]:
        return self._graph.parents(self.staff, self._CONST.classes_bearing_duration)
        
    def get_end_onset(self) -> Fraction:
        """
        Returns the maximal onset that the staff spans to.
        Maxima from symbol onset + symbol duration.
        Denotes the onset on which the subsequent staff would start.
        """
        nodes = self.get_contained_nodes_bearing_duration()

        if len(nodes) == 0:
            return Fraction(0)
        # Max next onset is node onset + its duration (the onset of the next potential symbol)
        max_next_onset = max([n.data[OnsetDataConstants.ONSET_BEATS] + n.data[OnsetDataConstants.DURATION_BEATS]
                              for n in nodes])
        return max_next_onset

    def get_start_onset(self) -> Fraction:
        """
        Returns the minimal onset of the staff.
        Denotes the onset on which the staff starts.
        """
        nodes = self.get_contained_nodes_bearing_duration()
        if len(nodes) == 0:
            return Fraction(0)
        min_onset = min([n.data[OnsetDataConstants.ONSET_BEATS]
                         for n in nodes])
        return min_onset

    def get_duration(self) -> Fraction:
        """
        Returns the total number of beats that the staff takes up.
        """
        return self.get_end_onset() - self.get_start_onset()
    
    def offset_onset(self, value: Fraction):
        """
        Changes the onset of duration-bearing symbols on this staff simultaneously,
        effectively postponing the onset of the staff in the global context.

        :param value: Value to offset all related offsets by.
        """
        length_before = self.get_duration()
        nodes = self.get_contained_nodes_bearing_duration()
        logger.info(f"Offsetting onset for {len(nodes)} nodes by {value}")
        for node in nodes:
            node.data[OnsetDataConstants.ONSET_BEATS] += value
        # Total staff duration should not change
        assert length_before == self.get_duration()


    def vertical_position_of_staffline_geometry(self, staffline: Node, left_offset: int) -> int:
        """
        Finds the column of mask directly at the ``left_offset`` (left-right coordinate)
        and computes the vertical coordinate of a point in ``staffline``
        that is constructed by averaging the pixel height of 1s inside
        the retrieved column.

        If averaging of points inside the line mask or indexing fail,
        the average line height is returned (``staffline.height``).

        :param staffline: Staffline to compute vertical distance to.
        :param left_offset: Left offset to compute vertical position at.
        :return: Vertical position of ``staffline`` geometry.

        Example:
            Say that the ``left_offset`` corresponds to this column of the
            ``staffline`` mask: ``[0,0,0,0,0,1,1,1,0,0].T``.

            Distance of the point on the line from the top of the mask
            is then computed as ``(5+6+7) / 3 = 6``.
            Its position from this point is computed as ``staffline.top + 6``.
        """        
        left_offset_in_mask = left_offset - staffline.left
        top_offset_from_mask = staffline.top
        mask_w = self.__staffline_masks[staffline]
        return top_offset_from_mask + mask_w[left_offset_in_mask]
    
    def vertical_overlap_geometry(self, node: Node) -> int:
        """
        Computes the vertical overlap (top to bottom) of a given node
        with this staff's geometry. Top and bottom positions of the staff
        are computed from the top and bottom staffs' geometry (masks).

        :param node: Instance of ``Node`` .
        :return: Overlap with staff as an ``int`` .
        """
        left_offset = node.middle[1]
        a_top = self.vertical_position_of_staffline_geometry(self.stafflines[0], left_offset)
        a_bottom = self.vertical_position_of_staffline_geometry(self.stafflines[-1], left_offset)
        
        top_overlap = max(a_top, node.top)
        bottom_overlap = min(a_bottom, node.bottom)
        return max(0, bottom_overlap - top_overlap)
    
    def vertical_overlap_geometry_normalized(self, node: Node) -> float:
        """
        Computes the vertical overlap (top to bottom) of a given node
        with this staff's geometry. Top and bottom positions of the staff
        are computed from the top and bottom staffs' geometry (masks).

        Normalizes it by the staff's height.

        :param node: Instance of ``Node`` .
        :return: Overlap with staff as an ``int`` .
        """
        left_offset = node.middle[1]
        a_top = self.vertical_position_of_staffline_geometry(self.stafflines[0], left_offset)
        a_bottom = self.vertical_position_of_staffline_geometry(self.stafflines[-1], left_offset)
        height = a_bottom - a_top
        
        top_overlap = max(a_top, node.top)
        bottom_overlap = min(a_bottom, node.bottom)
        overlap = max(0, bottom_overlap - top_overlap)

        return overlap / height

    def height_at_offset_geometry(self, left_offset: int) -> int:
        """
        Returns the vertical coordinate of staff's center
        at given offset from left.
        """
        top = self.vertical_position_of_staffline_geometry(self.stafflines[0], left_offset)
        bottom = self.vertical_position_of_staffline_geometry(self.stafflines[-1], left_offset)
        return bottom - top


    def vertical_distance_from_staffline_geometry(self, staffline: Node, other_node: Node) -> int:
        """
        Finds the column of mask directly under/above given ``other_node``
        and computes the vertical distance between the ``other_node`` and
        a point in ``staffline`` that is constructed by averaging the pixel height
        of 1s inside the retrieved column.

        If averaging of points inside the line mask or indexing fail,
        the average line height is returned (``staffline.height``).
        If the returned integer is negative, the ``other_node`` is **under** the ``staffline``,
        if it is positive, ``other_node`` is **above** the ``staffline``.

        :param staffline: Staffline to compute vertical distance to
        :param other_node: ``Node`` to compute vertical distance from
        :return: Vertical distance between ``staffline`` and ``other_node`` as integer.

        Example:
            Say that the centre of the ``other_node`` is above this column of the
            ``staffline`` mask: ``[0,0,0,0,0,1,1,1,0,0].T``.

            Distance of the point on the line is then computed as ``(5+6+7) / 3 = 6``.
            The total distance of the ``other_node`` from this point is computed as
            ``distance_from_mask_top + distance_of_point_from_mask_top = staffline.top - other_node.middle[0] + 6``.
        """
        return self.vertical_position_of_staffline_geometry(staffline, other_node.middle[1]) - other_node.middle[0]
    
    def vertical_distance_from_geometry(self, other_node: Node) -> int:
        """
        Returns the vertical distance of a given node's center
        from the geometrical center (denoted by mask) of this staff.
        Can be negative. If positive, the ``other_node`` is above,
        if negative, it is below.
        
        :param other_nodes: Node to compute the distance for.
        :return: Distance from the staff center as integer.
        """
        top_distance = self.vertical_distance_from_staffline_geometry(self.stafflines[0], other_node)
        bottom_distance = self.vertical_distance_from_staffline_geometry(self.stafflines[-1], other_node)
        return (top_distance + bottom_distance) // 2
    
    def absolute_vertical_distance_from_geometry(self, other_node: Node) -> int:
        return abs(self.vertical_distance_from_geometry(other_node))
    
    def get_absolute_distances_from_staff_positions_with_ids(self, other_node: Node) -> list[tuple[int,int]]:
        """
        Computes the absolute distance between the given node and all of this staff's positions
        - five stafflines and six staff spaces - in pixels.

        :param other_node:  Node to compute the distance for.
        :return: List of tuples formatted as ``(absolute_distance, position_id)`` .
        """
        distances = self.get_distances_from_staff_positions_with_ids(other_node)
        return [(abs(x[0]), x[1]) for x in distances]

    def get_distances_from_staff_positions_with_ids(self, other_node: Node) -> list[tuple[int, int]]:
        """
        Computes the distance between the given node and all of this staff's positions
        - five stafflines and six staff spaces - in pixels.
        The distances can assume negative values.

        :param other_node:  Node to compute the distance for.
        :return: List of tuples formatted as ``(distance, position_id)`` .
        """
        distance_from_stafflines = [self.vertical_distance_from_staffline_geometry(staffline, other_node)
                                    for staffline in self.stafflines]
        # For the staffspaces inside the staff neighboring with stafflines A, B,
        # we can compute the staffspace's distance from the symbol as (A + B) / 2
        distance_from_staffspaces = []
        for index in range(len(distance_from_stafflines) - 1):
            distance_from_staffspaces.append(
                (distance_from_stafflines[index] + distance_from_stafflines[index + 1]) // 2
            )
        # Compute distance from staffspaces outside of staff as distance from the most outer staffline
        # with the average space size / 2
        distance_from_staffspaces = (
            [distance_from_stafflines[0] - self.mean_staffline_distance // 2]
            + distance_from_staffspaces
            + [distance_from_stafflines[-1] + self.mean_staffline_distance // 2])
        
        assert len(distance_from_stafflines) == 5 and len(distance_from_staffspaces) == 6

        distance_from_stafflines_with_ids = list(zip(distance_from_stafflines, [x.id for x in self.stafflines]))
        distance_from_staffspaces_with_ids = list(zip(distance_from_staffspaces, [x.id for x in self.staffspaces]))
        # Merge the distances together: staffspace, staffline, ..., staffspace
        merged = [item for pair in zip(distance_from_staffspaces_with_ids, distance_from_stafflines_with_ids)
                  for item in pair] + [distance_from_staffspaces_with_ids[-1]]
        
        return merged

    def get_sinks(self) -> list[Node]:
        all_related_symbols = self._graph.parents(self.staff, self._CONST.classes_bearing_duration)
        return [x for x in all_related_symbols if x.is_precedence_sink]

    def get_sources(self) -> list[Node]:
        all_related_symbols = self._graph.parents(self.staff, self._CONST.classes_bearing_duration)
        return [x for x in all_related_symbols if x.is_precedence_source]
    
    def get_sink_closure(self) -> list[list[Node]]:
        """
        Returns a list of ``Node`` s that correspond to the sink closure.
        A sink can be a part of a chord, closure only contains this chord
        as a list of related nodes.

        If, for example, the staff's start would have two voices,
        then the closure will have exactly two closure sinks, as the voices
        cannot be merged together to from a single "subevent",
        unlike chords, which can.

        :return: List of lists if nodes that form the closure of sinks.
        """
        return group_by_chord(self._graph, self.get_sinks())
    
    def get_source_closure(self) -> list[list[Node]]:
        return group_by_chord(self._graph, self.get_sources())
        
        

