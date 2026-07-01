from fractions import Fraction
from dataclasses import dataclass, field
from itertools import chain
from collections import defaultdict
from typing import Optional

from mung import Node, NotationGraph
from mung.constants import ClassNameConstants as C, InferenceEngineConstants as I
from mung.graph import group_staffs_into_systems

from .utils import get_onset_beats
from ...graph import BarStyleToken, WingedToken, BackwardForwardToken
from ....logger import logger


@dataclass
class BarStruct:
    """
    Temporary structure for saving inferred information
    about barlines and repeats.
    """

    style: BarStyleToken
    is_repeat: bool
    bf: Optional[BackwardForwardToken] = None
    wing: Optional[WingedToken] = None
    onset: Optional[Fraction] = None

    def __post_init__(self) -> None:
        if self.is_repeat:
            assert self.bf is not None
            assert self.wing is not None

    @classmethod
    def default(cls) -> "BarStruct":
        return cls(BarStyleToken.NONE, False)


@dataclass
class SystemMeasureBarlineHandler:
    """
    Holds all temporal information about barlines
    and repeats for a single measure.
    """

    left: BarStruct
    right: BarStruct
    middle: list[BarStruct] = field(default_factory=lambda: [])


def _interpret_barline_list(barlines: list[Node]) -> BarStyleToken:
    """
    Interprets a list of barlines (MuNG nodes)
    as a BarStyleToken.

    Barlines are sorted from left to right
    and only at most the first two are considered.
    More than two lines at measure boundaries
    are not supported.

    If the no barlines are given, the BarStyleToken
    default is returned.

    :param barlines: List of MuNG barline nodes.
    :return: BarStyleToken.
    """

    if len(barlines) == 0:
        return BarStyleToken.default()

    barlines.sort(key=lambda b: b.top)

    groups: list[list[Node]] = []
    group: list[Node] = []
    for barline in barlines:
        if len(group) == 0 or group[-1].bottom > barline.top:
            group.append(barline)
        else:
            groups.append(group)
            group = [barline]
    if len(group) > 0:
        groups.append(group)

    assert len(group) > 0

    best_group = max(groups, key=lambda g: len(g))
    best_group.sort(key=lambda l: l.left)

    # edge case, mapping decorative barline final to heavy-heavy
    if any(l.class_name == C.Barlines.BARLINE_FINAL for l in best_group):
        return BarStyleToken.HEAVY_HEAVY

    if len(best_group) == 1:
        if best_group[0].class_name == C.Barlines.BARLINE_HEAVY:
            return BarStyleToken.HEAVY
        else:
            return BarStyleToken.REGULAR
    else:
        if best_group[0].class_name == C.Barlines.BARLINE_SINGLE:
            if best_group[1].class_name == C.Barlines.BARLINE_HEAVY:
                return BarStyleToken.LIGHT_HEAVY
            else:
                return BarStyleToken.LIGHT_LIGHT
        else:
            if best_group[1].class_name == C.Barlines.BARLINE_HEAVY:
                return BarStyleToken.HEAVY_HEAVY
            else:
                return BarStyleToken.HEAVY_LIGHT


def _get_barlines_from_parent(barline_parent: Node, graph: NotationGraph) -> list[Node]:
    """
    Finds all barlines that are children of the given parent.
    """

    return graph.children(barline_parent, class_filter=I.BARLINES)


def _interpret_barline_aggregation(
    barline_parent: Node, graph: NotationGraph
) -> tuple[BarStruct, BarStruct]:
    """
    Resolve possible left and right barline types.

    Possible outcomes:
    - regular barline, right repeat
    - left repeat, regular barline
    - left repeat, right repeat

    :param barline_parent: Measure separator or repeat MuNG object.
    :return: Left, right BarStruct.
    """
    # returns right, left
    # right for the previous one, left for the current one
    barlines = _get_barlines_from_parent(barline_parent, graph)

    # find repeats
    repeats = set(
        chain.from_iterable(
            graph.parents(
                barline, class_filter=[C.Repeat.REPEAT_LEFT, C.Repeat.REPEAT_RIGHT]
            )
            for barline in barlines
        )
    )

    if len(repeats) > 0:

        def _get_first(nodes: set[Node], name: str) -> Optional[Node]:
            for node in nodes:
                if node.class_name == name:
                    return node
            return None

        def _interpret_wing(repeat: Node, graph: NotationGraph) -> WingedToken:
            barlines = _get_barlines_from_parent(repeat, graph)
            if any(graph.has_children(b, C.Barlines.BARLINE_WING) for b in barlines):
                return WingedToken.STRAIGHT
            return WingedToken.NONE

        left = _get_first(repeats, C.Repeat.REPEAT_LEFT)
        right = _get_first(repeats, C.Repeat.REPEAT_RIGHT)
        assert left is not None or right is not None

        def _construct_potential_repeat(
            mung_repeat: Node | None,
            orientation: BackwardForwardToken,
            graph: NotationGraph,
        ) -> BarStruct:
            if mung_repeat is not None:
                barlines = _get_barlines_from_parent(mung_repeat, graph)

                if len(barlines) == 0:
                    logger.warning(
                        f"No barlines were given for {mung_repeat}, "
                        f"returning default: {BarStyleToken.default()}"
                    )

                style = _interpret_barline_list(barlines)
                return BarStruct(
                    style, True, orientation, _interpret_wing(mung_repeat, graph)
                )
            else:
                return BarStruct(BarStyleToken.default(), False)

        left = _construct_potential_repeat(left, BackwardForwardToken.FORWARD, graph)
        right = _construct_potential_repeat(right, BackwardForwardToken.BACKWARD, graph)

        return right, left

    # this is simple, both the previous and next are the same object
    else:
        style = _interpret_barline_list(barlines)

        return BarStruct(style, False), BarStruct(style, False)


def _get_system_repeats_without_separators(
    system: list[Node], graph: NotationGraph
) -> list[Node]:
    # get all repeats
    repeats = graph.filter_vertices([C.Repeat.REPEAT_LEFT, C.Repeat.REPEAT_RIGHT])
    # get repeats that overlap with given system
    repeats = [
        repeat for repeat in repeats if any(repeat.overlaps(staff) for staff in system)
    ]

    # filter out repeats that DO NOT have relation to measure separators
    output = []
    for repeat in repeats:
        barlines = graph.children(repeat, class_filter=I.BARLINES)
        if any(
            graph.has_parents(barline, class_filter=C.Barlines.MEASURE_SEPARATOR)
            for barline in barlines
        ):
            continue
        output.append(repeat)

    return output


def compute_bar_styles(
    graph: NotationGraph, measure_index_start: int
) -> defaultdict[int, defaultdict[int, SystemMeasureBarlineHandler]]:
    """
    Retrieves right bar styles for measure from a given graph.

    Returns a dictionary ordered as system_id -> measure_id -> bar_style.
    System index is zero based, measure indexing starts
    from number given by settings (default is 1).

    For each separator in measure, find vertically
    overlapping barlines - these are most probably located
    in the same instrument. Then, take the group with
    the most overlapping barlines, sort it left to right
    and map it to BarStyleTokens.
    """
    barline_types: defaultdict[int, defaultdict[int, SystemMeasureBarlineHandler]] = (
        defaultdict(
            lambda: defaultdict(
                lambda: SystemMeasureBarlineHandler(
                    BarStruct.default(), BarStruct.default()
                )
            )
        )
    )
    staff_systems = group_staffs_into_systems(graph.vertices)

    # dictionary structure:
    #   system_id : {
    #      measure_id : {
    #         left:
    #         right:
    #         middle:
    #   }
    # }
    # measure separator is on the right of each measure
    for system_index, ssy in enumerate(staff_systems):
        separators = sorted(
            set(
                chain.from_iterable(
                    graph.parents(staff, class_filter=C.Barlines.MEASURE_SEPARATOR)
                    for staff in ssy
                )
            ),
            key=lambda s: s.left,
        )
        middle_repeats = _get_system_repeats_without_separators(ssy, graph)
        if len(middle_repeats) > 0:
            logger.warning(
                f"Found repeats without relation to separators: {middle_repeats}"
            )

        # construct output, based on set measure index
        last_left = 0
        for measure_index, separator in enumerate(
            separators, start=measure_index_start
        ):
            right, left = _interpret_barline_aggregation(separator, graph)
            barline_types[system_index][measure_index].right = right
            barline_types[system_index][measure_index + 1].left = left

            # check if any of found middle repeats fits
            # between the previous and current separator
            # (it is in this measure)
            for m_rep in middle_repeats:
                if last_left < m_rep.left < separator.left:
                    o = _interpret_barline_aggregation(m_rep, graph)
                    for r in o:
                        if r is not None and r.is_repeat:
                            r.onset = get_onset_beats(m_rep)
                            barline_types[system_index][measure_index].middle.append(r)

            last_left = separator.left
    # retrieve barlines defined by groupings
    for system_index, ssy in enumerate(staff_systems):
        groupings = set(
            chain.from_iterable(
                graph.parents(
                    staff, class_filter=C.StaffGroupingBracketsAndBraces.STAFF_GROUPING
                )
                for staff in ssy
            )
        )
        # retrieve staff grouping only on the left of a system
        # (there might be grouping on the right also)
        groupings = [
            g for g in groupings if g.horizontal_center < ssy[0].horizontal_center
        ]

        if len(groupings) == 0:
            continue

        # find grouping with the most barlines
        best_grouping = max(
            groupings,
            key=lambda g: len(
                graph.children(
                    g,
                    class_filter=[C.Barlines.BARLINE_HEAVY, C.Barlines.BARLINE_SINGLE],
                )
            ),
        )
        measure_index = measure_index_start
        right, left = _interpret_barline_aggregation(best_grouping, graph)
        barline_types[system_index][measure_index - 1].right = right
        barline_types[system_index][measure_index].left = left

    return barline_types
