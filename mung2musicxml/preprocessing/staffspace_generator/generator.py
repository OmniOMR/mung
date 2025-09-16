import numpy as np
from dataclasses import dataclass
from typing import Self, Optional
from mung import Node, NotationGraph
from mung.constants import WESTERN_NOTATION_STAFFLINE_COUNT, InferenceEngineConstants, ClassNamesConstants

from .utils import merge_and_interpolate_top_bottom_masks, crop_node_masks_to_horizontal_overlap
from .strategy import StaffspaceGeneratorStrategy
from ..errors import StafflineCountNotMultipleError, MaskIsNoneError
from ...logger import logger


@dataclass(frozen=True)
class _StaffspaceData:
    mask: np.ndarray | None
    top: int
    left: int
    width: int
    height: int


class _StaffWrapperForStaffspaceGenerator:
    def __init__(
            self,
            staff: Node,
            stafflines: list[Node]
            ):
        if len(stafflines) != WESTERN_NOTATION_STAFFLINE_COUNT:
            print(len(stafflines))
            raise StafflineCountNotMultipleError()
        if not all(x.class_name == ClassNamesConstants.STAFFLINE for x in stafflines):
            raise ValueError(f"Mismatched class names in {stafflines}")
        if not staff.class_name == ClassNamesConstants.STAFF:
            raise ValueError(f"Mismatched class name in {staff}")

        self.staff = staff
        self.stafflines = sorted(stafflines, key=lambda x: x.top)
    
    
    @classmethod
    def from_graph(cls, graph: NotationGraph) -> list[Self]:
        staffs = sorted(graph.filter_vertices(InferenceEngineConstants.STAFF), key=lambda x: x.top)
        output = []
        for staff in staffs:
            output.append(cls(staff, graph.children(staff, class_filter=InferenceEngineConstants.STAFFLINE)))
        return output
    
    @property
    def mean_staffline_distance(self) -> int:
        """
        The mean distance between stafflines, equivalent to
        mean staffspace height.
        """
        return int(np.diff([x.top for x in self.stafflines]).mean())

    @property
    def parent_id(self) -> int:
        """Returns the id of the parent staff ``Node`` instance"""
        return self.staff.id

    @property
    def top_staffline(self) -> Node:
        return self.stafflines[0]

    @property
    def bottom_staffline(self) -> Node:
        return self.stafflines[-1]


class StaffspaceGenerator:
    def __init__(self, strategy: Optional[StaffspaceGeneratorStrategy] = None):
        self._strategy = StaffspaceGeneratorStrategy() if strategy is None else strategy
    
    def __call__(self, graph: NotationGraph) -> NotationGraph:
        return self.build_staffspaces(graph)
    
    @classmethod
    def run(cls, graph: NotationGraph, strategy: Optional[StaffspaceGeneratorStrategy] = None) -> NotationGraph:
        return cls(strategy)(graph)

    def build_staffspaces(self, graph: NotationGraph) -> NotationGraph:
        wrappers = _StaffWrapperForStaffspaceGenerator.from_graph(graph)

        if len(wrappers) == 0:
            return graph
        
        dataset, document = graph.vertices[0].dataset, graph.vertices[1].document
        next_node_id = graph.next_node_id
        edges_to_add: list[tuple[int, int]] = []
        staffspaces: list[Node] = []

        # Create nodes based on generated masks
        for wrapper in wrappers:
            space_data = self.construct_staffspace_data(wrapper)
            for space in space_data:
                node = Node(
                    id_=next_node_id,
                    class_name=ClassNamesConstants.STAFFSPACE,
                    top=space.top,
                    left=space.left,
                    width=space.width,
                    height=space.height,
                    document=document,
                    dataset=dataset,
                    mask=space.mask
                )
                node.crop_to_mask()
                staffspaces.append(node)
                edges_to_add.append((wrapper.parent_id, next_node_id))
                next_node_id += 1
        
        # Complete the graph with new nodes and edges
        new_graph = NotationGraph(graph.vertices + staffspaces)
        for from_id, to_id in edges_to_add:
            new_graph.add_edge(from_id, to_id)
        
        logger.info(f"Added {len(staffspaces)} staffspaces to graph.")
        
        return new_graph
        
    def _construct_top_staffspace_data(self, staff_wrapper: _StaffWrapperForStaffspaceGenerator) -> _StaffspaceData:
        """
        Shift the top staffline by the mean staffspace distance
        and compute the staffspace as a space between these two lines.
        """
        top_staffline = staff_wrapper.top_staffline
        mask1 = top_staffline.mask

        if mask1 is None:
            raise MaskIsNoneError()
        
        top_y, bottom_y = top_staffline.top - staff_wrapper.mean_staffline_distance, top_staffline.top
        width, height = top_staffline.width, top_staffline.height + staff_wrapper.mean_staffline_distance
        
        if self._strategy.PRECISE_MASK:
            mask = merge_and_interpolate_top_bottom_masks(mask1, top_y, mask1, bottom_y)
        else:
            mask = np.ones((height, width), dtype=np.uint8)
        
        return _StaffspaceData(
            mask=mask,
            top=top_y,
            left=top_staffline.left,
            width=width,
            height=height
        )

    def _construct_bottom_staffspace_data(self, staff_wrapper: _StaffWrapperForStaffspaceGenerator) -> _StaffspaceData:
        """
        Shift the bottom staffline by the mean staffspace distance
        and compute the staffspace as a space between these two lines.
        """
        bottom_staffline = staff_wrapper.bottom_staffline
        mask1 = bottom_staffline.mask

        if mask1 is None:
            raise MaskIsNoneError()
        
        top_y, bottom_y = bottom_staffline.top, bottom_staffline.top + staff_wrapper.mean_staffline_distance
        width, height = bottom_staffline.width, bottom_staffline.height + staff_wrapper.mean_staffline_distance
 
        if self._strategy.PRECISE_MASK:
            mask = merge_and_interpolate_top_bottom_masks(mask1, top_y, mask1, bottom_y)
        else:
            mask = np.ones((height, width), dtype=np.uint8)
        
        return _StaffspaceData(
            mask=mask,
            top=bottom_staffline.top,
            left=bottom_staffline.left,
            width=width,
            height=height
        )

    def construct_staffspace_data(self, staff_wrapper: _StaffWrapperForStaffspaceGenerator) -> list[_StaffspaceData]:
        data: list[_StaffspaceData] = []
        # Construct top space
        data.append(self._construct_top_staffspace_data(staff_wrapper))
        # Construct space between two stafflines next to each other
        for index in range(len(staff_wrapper.stafflines) - 1):
            sl1, sl2 = staff_wrapper.stafflines[index], staff_wrapper.stafflines[index + 1]
            width, height = Node.horizontal_overlap(sl1, sl2), sl2.bottom - sl1.top
            
            if self._strategy.PRECISE_MASK:
                top_mask, bottom_mask = crop_node_masks_to_horizontal_overlap(sl1, sl2)
                mask = merge_and_interpolate_top_bottom_masks(top_mask, sl1.top, bottom_mask, sl2.top)
            else:
                mask = np.ones((height, width), dtype=np.uint8)
            
            data.append(_StaffspaceData(
                mask=mask,
                top=sl1.top,
                left=max(sl1.left, sl2.left),
                width=width,
                height=height
                ))
        
        # Construct bottom space
        data.append(self._construct_bottom_staffspace_data(staff_wrapper))

        return data