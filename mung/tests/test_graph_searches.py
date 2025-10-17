from unittest import TestCase, main
from parameterized import parameterized

from .utils import load_dot_graph
from pathlib import Path
from mung import NotationGraph
from typing import Iterable

GRAPH_PATH = Path(__file__).parent / "assets/dag.dot"

syntax_graph = load_dot_graph(GRAPH_PATH)
precedence_graph = load_dot_graph(GRAPH_PATH, load_edges_as_syntax=False)


class TestGraphSearches(TestCase):
    @parameterized.expand([
        (p + "_" + s, p, g, *rest) for (s, *rest) in 
        [
            # (name, start node id, class filter, expected ids)
            # graph instance will be added automatically
            ("simple", 1, None, [2, 3]),
            ("simple_empty", 10, None, []),
            ("filter", 6, ["C"], [9]),
            ("filter_empty", 6, ["A", "B"], []),
        ]
        for p, g in (("syntax", syntax_graph), ("precedence", precedence_graph))
    ])
    def test_children(
        self,
        name: str,
        mode: str,
        graph: NotationGraph,
        start_node_id: int,
        class_filter: Iterable[str] | str | None,
        expected_ids: list[int]
    ):
        founds_ids = [
            x.id for x in 
            getattr(
                graph,
                f"{'precedence_' if mode == 'precedence' else ''}children"
            )(start_node_id, class_filter=class_filter)]
        self.assertCountEqual(founds_ids, expected_ids)
    
    @parameterized.expand([
        (p + "_" + s, p, g, *rest) for (s, *rest) in 
        [
            # (name, start node id, class filter, expected ids)
            # graph instance will be added automatically
            ("simple", 9, None, [5, 6]),
            ("simple_empty", 1, None, []),
            ("filter", 8, ["A"], [4]),
            ("filter", 8, ["B"], [5]),
            ("filter_empty", 6, ["A", "B"], []),
        ]
        for p, g in (("syntax", syntax_graph), ("precedence", precedence_graph))
    ])
    def test_parents(
        self,
        name: str,
        mode: str,
        graph: NotationGraph,
        start_node_id: int,
        class_filter: Iterable[str] | str | None,
        expected_ids: list[int]
    ):
        founds_ids = [
            x.id for x in 
            getattr(
                graph,
                f"{'precedence_' if mode == 'precedence' else ''}parents"
            )(start_node_id, class_filter=class_filter)]
        self.assertCountEqual(founds_ids, expected_ids)

    @parameterized.expand([
        (p + "_" + s, p, g, *rest) for (s, *rest) in 
        [
            # (name, start node id, class filter, expected ids)
            # graph instance will be added automatically
            ("simple", 9, None, [11, 12]),
            ("simple_empty", 10, None, []),
            ("simple_deep", 2, None, [4, 5, 8, 9, 11, 12]),
            ("filter_simple", 8, ["B"], [11]),
            ("filter_simple_empty", 8, ["A"], []),
            ("filter_deep", 1, ["A", "B"], [2, 4, 5, 7, 8, 10, 11]),
        ]
        for p, g in (("syntax", syntax_graph), ("precedence", precedence_graph))
    ])
    def test_descendants(
        self,
        name: str,
        mode: str,
        graph: NotationGraph,
        start_node_id: int,
        class_filter: Iterable[str] | str | None,
        expected_ids: list[int]
    ):
        founds_ids = [
            x.id for x in 
            getattr(
                graph,
                f"{'precedence_' if mode == 'precedence' else ''}descendants"
            )(start_node_id, class_filter=class_filter)]
        self.assertCountEqual(founds_ids, expected_ids)

    @parameterized.expand([
        (p + "_" + s, p, g, *rest) for (s, *rest) in 
        [
            # (name, start node id, class filter, expected ids)
            # graph instance will be added automatically
            ("simple", 2, None, [1]),
            ("simple_empty", 1, None, []),
            ("simple_deep", 6, None, [3, 1]),
            ("filter_simple", 8, ["B"], [5, 2]),
            ("filter_deep", 9, ["A"], [1]),
            ("filter_deep", 10, ["A", "B"], [1, 7]),
        ]
        for p, g in (("syntax", syntax_graph), ("precedence", precedence_graph))
    ])
    def test_ancestors(
        self,
        name: str,
        mode: str,
        graph: NotationGraph,
        start_node_id: int,
        class_filter: Iterable[str] | str | None,
        expected_ids: list[int]
    ):
        founds_ids = [
            x.id for x in 
            getattr(
                graph,
                f"{'precedence_' if mode == 'precedence' else ''}ancestors"
            )(start_node_id, class_filter=class_filter)]
        self.assertCountEqual(founds_ids, expected_ids)

    @parameterized.expand([
        (p + "_" + s, p, g, *rest) for (s, *rest) in 
        [
            # (name, from node id, to node id, expected value)
            # graph instance will be added automatically
            ("simple", 2, 1, True),
            ("simple", 5, 1, False),
        ]
        for p, g in (("syntax", syntax_graph), ("precedence", precedence_graph))
    ])
    def test_is_child(
        self,
        name: str,
        mode: str,
        graph: NotationGraph,
        from_node_id: int,
        to_node_id: int,
        expected_value: bool
    ):
        value = getattr(
                graph,
                f"is_{'precedence_' if mode == 'precedence' else ''}child_of"
        )(from_node_id, to_node_id)
        self.assertEqual(value, expected_value)

    @parameterized.expand([
        (p + "_" + s, p, g, *rest) for (s, *rest) in 
        [
            # (name, from node id, to node id, expected value)
            # graph instance will be added automatically
            ("simple", 9, 12, True),
            ("simple", 8, 1, False),
        ]
        for p, g in (("syntax", syntax_graph), ("precedence", precedence_graph))
    ])
    def test_is_parent(
        self,
        name: str,
        mode: str,
        graph: NotationGraph,
        from_node_id: int,
        to_node_id: int,
        expected_value: bool
    ):
        value = getattr(
                graph,
                f"is_{'precedence_' if mode == 'precedence' else ''}parent_of"
        )(from_node_id, to_node_id)
        self.assertEqual(value, expected_value)

    @parameterized.expand([
        (p + "_" + s, p, g, *rest) for (s, *rest) in 
        [
            # (name, from node id, to node id, expected value)
            # graph instance will be added automatically
            ("simple", 2, 1, True),
            ("deep", 12, 1, True),
            ("deep", 11, 3, True),
            ("simple", 6, 10, False),
        ]
        for p, g in (("syntax", syntax_graph), ("precedence", precedence_graph))
    ])
    def test_is_descendant(
        self,
        name: str,
        mode: str,
        graph: NotationGraph,
        from_node_id: int,
        to_node_id: int,
        expected_value: bool
    ):
        value = getattr(
                graph,
                f"is_{'precedence_' if mode == 'precedence' else ''}descendant_of"
        )(from_node_id, to_node_id)
        self.assertEqual(value, expected_value)

    @parameterized.expand([
        (p + "_" + s, p, g, *rest) for (s, *rest) in 
        [
            # (name, from node id, to node id, expected value)
            # graph instance will be added automatically
            ("simple", 1, 2, True),
            ("deep", 1, 12, True),
            ("deep", 3, 11, True),
            ("simple", 10, 6, False),
        ]
        for p, g in (("syntax", syntax_graph), ("precedence", precedence_graph))
    ])
    def test_is_ancestor(
        self,
        name: str,
        mode: str,
        graph: NotationGraph,
        from_node_id: int,
        to_node_id: int,
        expected_value: bool
    ):
        value = getattr(
                graph,
                f"is_{'precedence_' if mode == 'precedence' else ''}ancestor_of"
        )(from_node_id, to_node_id)
        self.assertEqual(value, expected_value)


if __name__ == "__main__":
    main()