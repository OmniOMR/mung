from mung import NotationGraph, Node
from mung.graph import group_staffs_into_systems, UnionFind
from mung.constants import ClassNameConstants as C
from typing import TypeVar, Callable, Optional

from ..logger import logger
from ..utils import flatten

T = TypeVar("T")
U = TypeVar("U")


def get_instrument_groups_from_systems(graph: NotationGraph) -> list[list[list[Node]]]:
    """
    Returns systems separated into instruments.

    Format: score -> systems -> instruments -> staffs.
    """
    instruments_in_systems: list[list[list[Node]]] = []
    systems = group_staffs_into_systems(graph.vertices)

    for i, system in enumerate(systems):
        logger.debug(f"Processing system {[x.id for x in system]}")
        current_instruments = []
        # find all groupings that are linked to the system
        groupings = set(flatten(graph.parents(staff, class_filter=C.StaffGroupingBracketsAndBraces.STAFF_GROUPING) for staff in system))
        
        # no grouping, image a single large grouping spanning over all staffs in system
        if len(groupings) == 0:
            if len(system) == 2:
                current_instruments = [system]
            else: 
                current_instruments = [[staff] for staff in system]
        
        else:
            # try to find grandstaffs
            for g in groupings:
                staffs = graph.children(g, class_filter=C.Staves.STAFF)
                if len(staffs) == 2:
                    current_instruments.append(sorted(staffs, key=lambda s: s.top))
            
            for staff in system:
                if staff not in flatten(current_instruments):
                    current_instruments.append([staff])
            
            def _drop_duplicates(lists: list[list[Node]]) -> list[list[Node]]:
                result = []
                for lst in lists:
                    if lst not in result:
                        result.append(lst)
                return result
            
            current_instruments = _drop_duplicates(current_instruments)
            # if passed, there are no overlapping instruments
            assert len(current_instruments) == len(UnionFind.merge_groups(current_instruments)), "Overlapping instruments"

        assert all(staff in flatten(current_instruments) for staff in system)

        logger.debug(f"Found instruments in system {i}: "
                     f"{', '.join([str([s.id for s in i]) for i in current_instruments])}")

        instruments_in_systems.append(current_instruments)
    
    return instruments_in_systems


def link_instruments(
        instrument_groups: list[list[list[Node]]]
    ) -> list[list[list[Node]]]:
    """
    Instruments groups: score -> system -> instrument staffs.

    Output: instruments -> single instrument -> its staffs::

        [
            [
                [Staff(1), Staff(2)], [Staff(3), Staff(4)], ...
            ],
            [
                [Staff(10)], [Staff(11)], [Staff(12)], ...
            ],
        ]

    This means that the first instrument consists of staffs 1, 2, 3, 4, ...
    and it is a grand staff. And the second instrument consists of staffs
    10, 11, 12, ... and is a single staff instrument.
    """
    if len(instrument_groups) == 0:
        return [[]]
    
    # sort - system measure with the most instruments visibly playing are at the start
    instrument_groups = sorted(instrument_groups, key=lambda l: len(l), reverse=True)
    
    output = [[staffs] for staffs in instrument_groups[0]]
    for system in instrument_groups[1:]:
        output = _add_system_to_output(output, system, lambda l: len(l[0]))

    return output


def _add_system_to_output(
        output: list[list[T]],
        system: list[T],
        get_type: Callable[[list[T]], U]
    ) -> list[list[T]]:
    index1 = 0
    # tries to add value to the closest possible bin
    for i, value in enumerate(system):
        # print(output)
        # print(f"Will try to add {value} to {index1}")
        if index1 >= len(output):
            output.append([value])
        elif get_type(output[index1]) != get_type([value]):
            # index1 += 1
            while index1 < len(output) and get_type(output[index1]) != get_type([value]):
                # print(i, value, index1)
                index1 += 1
            # print(i, value, index1)
            if index1 < len(output):
                # print(f"Inserting to {index1} value {value}")
                output[index1].append(value)
            else:
                output.append([value])
        else:
            output[index1].append(value)
        index1 += 1

    return output


def graph_to_instruments(graph: NotationGraph) -> list[list[list[Node]]]:
    """
    Output: instruments -> single instrument -> its staffs::

        [
            [
                [Staff(1), Staff(2)], [Staff(3), Staff(4)], ...
            ],
            [
                [Staff(10)], [Staff(11)], [Staff(12)], ...
            ],
        ]

    This means that the first instrument consists of staffs 1, 2, 3, 4, ...
    and it is a grand staff. And the second instrument consists of staffs
    10, 11, 12, ... and is a single staff instrument.
    """
    groups = get_instrument_groups_from_systems(graph)
    instruments = link_instruments(groups)
    instruments.sort(key=lambda instr: instr[0][0].top)
    return instruments