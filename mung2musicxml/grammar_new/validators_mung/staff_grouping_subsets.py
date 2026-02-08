from mung import NotationGraph, Node
from mung.constants import ClassNameConstants as C
from typing import TypeVar, Iterable, Optional

from ..violations import InvalidSetViolation, GrammarViolation, MissingRelationViolation
from ..parts import GrammarNode
from ..constants import LinkDirection


T = TypeVar("T")


class StaffGroupingSubsetValidator:
    def __init__(self):
        pass

    @staticmethod
    def missing_from_superset(sub: Iterable[T], sup: Iterable[T]) -> list[T]:
        """
        Return elements in `sub` that are not in `sup`.
        """
        return [x for x in sub if x not in sup]
    
    def _create_violation_report(self, first: Node, second: Node, missing_connections: list[Node]) -> InvalidSetViolation:
        return InvalidSetViolation.from_missing_connections(
                GrammarNode.from_mung(first),
                GrammarNode.from_mung(second),
                [GrammarNode.from_mung(x) for x in missing_connections],
                LinkDirection.OUTLINK
                )
    
    def _crosscheck_two_groupings(self, parent: Node, parent_staffs: list[Node], child: Node, graph: NotationGraph) -> Optional[GrammarViolation]:
        child_staff = graph.children(child, class_filter=C.Staves.STAFF)
        
        missing = self.missing_from_superset(child_staff, parent_staffs)
        if len(missing) > 0:
            return self._create_violation_report(parent, child, missing)
        return None

    def _check_single_grouping(self, grouping: Node, graph: NotationGraph) -> list[GrammarViolation]:
        parent_staffs = graph.children(grouping, class_filter=C.Staves.STAFF)
        children_groupings = graph.descendants(grouping, class_filter=C.StaffGroupingBracketsAndBraces.STAFF_GROUPING)
        output: list[GrammarViolation] = []

        for child_group in children_groupings:
            v = self._crosscheck_two_groupings(grouping, parent_staffs, child_group, graph)
            if v is not None:
                output.append(v)
        
        return output
    
    def _check_two_groupings_with_staff(self, first: Node, second: Node, graph: NotationGraph) -> Optional[MissingRelationViolation]:
        def is_descendant(first: Node, second: Node, graph: NotationGraph) -> bool:
            descendants = graph.descendants(first, class_filter=C.StaffGroupingBracketsAndBraces.STAFF_GROUPING)
            return second in descendants
        
        def share_staff(first: Node, second: Node, graph: NotationGraph) -> bool:
            first_staff = graph.children(first, class_filter=C.Staves.STAFF)
            second_staff = graph.children(second, class_filter=C.Staves.STAFF)
            return len(set(first_staff).intersection(set(second_staff))) > 0
        
        if share_staff(first, second, graph):
            if is_descendant(first, second, graph) or is_descendant(second, first, graph):
                return None
            
            return MissingRelationViolation.from_mung(first, second)

        return None
        
    def _check_grouping_hierarchy_based_on_staffs(self, graph: NotationGraph) -> list[GrammarViolation]:
        groupings = graph.filter_vertices(C.StaffGroupingBracketsAndBraces.STAFF_GROUPING)

        violations = []
        for index in range(len(groupings) - 1):
            first = groupings[index]
            for i in range(index + 1, len(groupings)):
                second = groupings[i]
                v = self._check_two_groupings_with_staff(first, second, graph)
                if v is not None:
                    violations.append(v)
        
        return violations
    
    def find_invalid(self, graph: NotationGraph) -> list[GrammarViolation]:
        """
        For all staff groupings inside the graph, finds all its descendants,
        and check whether all of the descendants' staffs are children
        of the staff grouping.

        Also, if two staff grouping have the same staff as their child
        and there is no relation between the two groupings,
        violation will be created.
        """
        groupings = graph.filter_vertices(C.StaffGroupingBracketsAndBraces.STAFF_GROUPING)
        violations = []
        for grouping in groupings:
            violations.extend(self._check_single_grouping(grouping, graph))

        violations.extend(self._check_grouping_hierarchy_based_on_staffs(graph))
        return violations
    