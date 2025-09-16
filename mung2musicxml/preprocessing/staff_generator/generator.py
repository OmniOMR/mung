from typing import Optional
from mung.constants import ClassNamesConstants, WESTERN_NOTATION_STAFFLINE_COUNT
from mung import NotationGraph
from mung.stafflines import build_staff_nodes
from mung.io import validate_nodes_graph_structure

from .strategy import StaffGeneratorStrategy
from ..errors import StafflineCountNotMultipleError
from ...logger import logger


class StaffGenerator:
    """
    Generates staff nodes from stafflines, if needed,
    and connects stafflines to staffs.
    """
    def __init__(self, strategy: Optional[StaffGeneratorStrategy] = None):
        self._strategy = strategy if strategy is not None else StaffGeneratorStrategy()
    
    def __call__(self, graph: NotationGraph) -> NotationGraph:
        return self.build_or_check_staffs_and_link_stafflines(graph)
    
    @classmethod
    def run(cls, graph: NotationGraph, strategy: Optional[StaffGeneratorStrategy] = None) -> NotationGraph:
        return cls(strategy)(graph)
    
    @staticmethod
    def _build_or_check_existing_staff_to_staffline_links(graph: NotationGraph):
        """
        Checks existing connections between staffs and stafflines. Graph is modified in place.

        If a connection exists:
        - There should be only one.
        - It should match the computed connection.

        If it does not exist, stafflines are grouped into groups of five from top to bottom
        and assigned to their respective staff.
        """
        staffs = sorted(graph.filter_vertices(ClassNamesConstants.STAFF), key=lambda x: x.top)
        stafflines = sorted(graph.filter_vertices(ClassNamesConstants.STAFFLINE), key=lambda x: x.top)

        assert len(stafflines) % len(staffs) == 0

        for i, staffline in enumerate(stafflines):
            # Staff index relative from top to bottom (index of upper staff is 0)
            relative_staff_index = i // WESTERN_NOTATION_STAFFLINE_COUNT
            assigned_staffs = graph.parents(staffline.id, class_filter=[ClassNamesConstants.STAFF])

            if len(assigned_staffs) > 1:
                raise ValueError(f"Staffline {staffline.id} has multiple assigned staffs")

            proposed_staff_id = staffs[relative_staff_index].id

            # is assigned to something, just check that it is correct
            if len(assigned_staffs) == 1:
                current_staff_id = assigned_staffs[0].id
                if current_staff_id != proposed_staff_id:
                    logger.warning(
                        f"Staffline {staffline.id} is assigned to staff {current_staff_id} which differs from computed {proposed_staff_id}")
            # is not assigned to anything, assign it by sort
            else:
                graph.add_edge(proposed_staff_id, staffline.id)
                logger.debug(f"Creating edge from staff {proposed_staff_id} to staffline {staffline.id}")
    
    @staticmethod
    def _rebuild_staffs_from_existing(graph: NotationGraph) -> NotationGraph:
        old_staffs = graph.filter_vertices(ClassNamesConstants.STAFF)
        new_staffs = build_staff_nodes(graph.vertices, build_links=False)
        
        assert len(old_staffs) == len(new_staffs)
        # Match old and new staff together and move out/inlinks
        old_staffs = sorted(old_staffs, key=lambda x: x.top)
        new_staffs = sorted(new_staffs, key=lambda x: x.top)

        # This is super illegal,
        # updates the "unavailable" values and keeps the old instances of the objects.
        for old, new in zip(old_staffs, new_staffs):
            old._Node__top = new.top # type: ignore
            old._Node__left = new.left # type: ignore
            old._Node__height = new.height # type: ignore
            old._Node__width = new.width # type: ignore
            old.set_mask(new.mask)
        
        logger.info(f"Rebuild {len(new_staffs)} from existing staffs")

        return graph

    def build_or_check_staffs_and_link_stafflines(self, graph: NotationGraph) -> NotationGraph:
        """
        Builds a new instance of ``NotationGraph`` with links from stafflines to staffs
        and optionally fills in missing staffs or rebuilds them based on stafflines.

        :param graph: Graph to which the staffs and links will be added.
        :param strategy: StaffGenerator strategy.
        :return: new instance of ``NotationGraph``
        """
        staffline_c = len(graph.filter_vertices(ClassNamesConstants.STAFFLINE))
        staff_c = len(graph.filter_vertices(ClassNamesConstants.STAFF))
        logger.debug(f"{staffline_c=}, {staff_c=}")

        # Check staffline counts
        if staffline_c % WESTERN_NOTATION_STAFFLINE_COUNT != 0:
            raise StafflineCountNotMultipleError()

        # Some staffs were provided, counts do not match
        if staff_c > 0 and WESTERN_NOTATION_STAFFLINE_COUNT * staff_c != staffline_c:
            raise ValueError(
                f"{staff_c} staffs were given, expected staffline count {WESTERN_NOTATION_STAFFLINE_COUNT * staff_c} does not match with staffline count given {staffline_c}"
            )

        logger.debug("Staff and staffline checks passed")

        if self._strategy.FORCE_STAFF_REBUILD and staff_c > 0:
            new_graph = StaffGenerator._rebuild_staffs_from_existing(graph)
            StaffGenerator._build_or_check_existing_staff_to_staffline_links(new_graph)
        
        elif staff_c > 0:
            logger.info("Graph contains some staffs, checking connections.")
            StaffGenerator._build_or_check_existing_staff_to_staffline_links(graph)
            new_graph = graph
        
        else:
            staffs = build_staff_nodes(graph.vertices)
            logger.info(f"Added {len(staffs)} staffs")
            new_graph = NotationGraph(graph.vertices + staffs)

        assert validate_nodes_graph_structure(new_graph.vertices)
        return new_graph
