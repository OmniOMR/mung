from mung import NotationGraph, Node
from mung.graph import group_staffs_into_systems, UnionFind
from mung.constants import ClassNamesConstants as C

from ..logger import logger
from ..utils import flatten


def get_instrument_groups_from_systems(graph: NotationGraph) -> list[list[list[Node]]]:
    """
    Returns systems separated into instruments.
    """
    instruments_in_systems: list[list[list[Node]]] = []
    systems = group_staffs_into_systems(graph.vertices)

    for i, system in enumerate(systems):
        logger.debug(f"Processing system {[x.id for x in system]}")
        current_instruments = []
        # find all groupings that are linked to the system
        groupings = set(flatten(graph.parents(staff, class_filter=C.STAFF_GROUPING) for staff in system))
        
        # no grouping, image a single large grouping spanning over all staffs in system
        if len(groupings) == 0:
            if len(system) == 2:
                current_instruments = [system]
            else: 
                current_instruments = [[staff] for staff in system]
        
        else:
            # try to find grandstaffs
            for g in groupings:
                staffs = graph.children(g, class_filter=C.STAFF)
                if len(staffs) == 2:
                    current_instruments.append(sorted(staffs, key=lambda s: s.top))
            
            for staff in system:
                if staff not in flatten(current_instruments):
                    current_instruments.append([staff])
            
            # if passed, there are no overlapping instruments
            assert len(current_instruments) == len(UnionFind.merge_groups(current_instruments)), "Overlapping instruments"

        assert all(staff in flatten(current_instruments) for staff in system)

        logger.debug(f"Found instruments in system {i}: "
                     f"{', '.join([str([s.id for s in i]) for i in current_instruments])}")

        instruments_in_systems.append(current_instruments)
    
    return instruments_in_systems

