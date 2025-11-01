import unittest
from fractions import Fraction
from mung2musicxml.utils import WrapperGraph
from typing import TypeVar

T = TypeVar("T")


class TestWrapperGraphScheduling(unittest.TestCase):
    def build_graph(
        self,
        edges: list[tuple[T, T]],
        durations: dict[T, tuple[int | Fraction, int | Fraction]],
    ):
        """
        edges: list of (u, v) tuples meaning u -> v
        durations: dict of node -> duration
        """
        objects = list(durations.keys())

        def get_neighbors(x):
            return [v for u, v in edges if u == x]

        def get_start(x: T) -> int | Fraction:
            return durations[x][0]
        
        def get_duration(x: T) -> int | Fraction:
            return durations[x][1]

        return WrapperGraph.build_graph(objects, get_neighbors, get_start, get_duration)

    def test_single_node(self):
        nodes = self.build_graph([], {"A": (0, 3)})
        g = WrapperGraph(nodes)
        active = g.schedule_and_find_width()
        width = len(active)
        self.assertEqual(width, 1)
        self.assertEqual([n.obj for n in active], ["A"])

    def test_two_parallel_nodes(self):
        nodes = self.build_graph([], {"A": (0, 3), "B": (0, 2)})
        g = WrapperGraph(nodes)
        active = g.schedule_and_find_width()
        width = len(active)
        self.assertEqual(width, 2)
        # Both should start at 0
        self.assertCountEqual([n.obj for n in active], ["A", "B"])

    def test_chain(self):
        nodes = self.build_graph(
            [("A", "B"), ("B", "C")], {"A": (0, 2), "B": (2, 3), "C": (5, 1)}
        )
        g = WrapperGraph(nodes)
        active = g.schedule_and_find_width()
        width = len(active)
        # All sequential, width = 1
        self.assertEqual(width, 1)

    def test_branching_and_join(self):
        # A → C, B → C
        nodes = self.build_graph(
            [("A", "C"), ("B", "C")], {"A": (0, 3), "B": (0, 2), "C": (3, 4)}
        )
        g = WrapperGraph(nodes)
        active = g.schedule_and_find_width()
        width = len(active)
        # A and B overlap
        self.assertEqual(width, 2)
        self.assertCountEqual([n.obj for n in active], ["A", "B"])

    def test_fractional_durations(self):
        nodes = self.build_graph(
            [], {"A": (0, Fraction(1, 2)), "B": (0, Fraction(3, 2))}
        )
        g = WrapperGraph(nodes)
        active = g.schedule_and_find_width()
        width = len(active)
        self.assertEqual(width, 2)

    def test_parallel_components(self):
        # A -> B -> C ->
        # D ----> F ----->
        nodes = self.build_graph(
            [("A", "B"), ("B", "C"), ("D", "E")],
            {"A": (0, 1), "B": (1, 1), "C": (2, 2), "D": (0, 3), "E": (3, 3)},
        )
        g = WrapperGraph(nodes)
        active = g.schedule_and_find_width()
        width = len(active)
        self.assertEqual(width, 2)


if __name__ == "__main__":
    unittest.main()
