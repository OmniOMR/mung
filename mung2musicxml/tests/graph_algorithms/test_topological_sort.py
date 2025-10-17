from unittest import TestCase, main

from mung2musicxml.utils import topological_sort


class TestTopologicalSort(TestCase):
    def test_single_node(self):
        nodes = ["A"]
        def is_predecessor(u, v):
            return False

        result = topological_sort(nodes, is_predecessor)

        self.assertEqual(result, ["A"])

    def test_two_nodes_linear(self):
        nodes = ["A", "B"]
        def is_predecessor(u, v):
            return (u, v) in [("A", "B")]
        
        result = topological_sort(nodes, is_predecessor)

        self.assertEqual(result, ["A", "B"])

    def test_two_nodes_reverse(self):
        nodes = ["A", "B"]
        def is_predecessor(u, v):
            return (u, v) in [("B", "A")]
        
        result = topological_sort(nodes, is_predecessor)

        self.assertEqual(result, ["B", "A"])

    def test_three_nodes_chain(self):
        nodes = ["A", "B", "C"]
        def is_predecessor(u, v):
            return (u, v) in [
                ("A", "B"),
                ("B", "C")
            ]
        
        result = topological_sort(nodes, is_predecessor)

        self.assertEqual(result, ["A", "B", "C"])

    def test_three_nodes_branching(self):
        nodes = ["A", "B", "C"]
        def is_predecessor(u, v): 
            return (u, v) in [
                ("A", "B"),
                ("A", "C")
            ]
        
        result = topological_sort(nodes, is_predecessor)

        # A must come first, but B and C can be in any order
        self.assertEqual(result[0], "A")
        self.assertCountEqual(result[1:], ["B", "C"])

    def test_diamond_shape(self):
        # DAG: A -> B, A -> C, B -> D, C -> D
        nodes = ["A", "B", "C", "D"]
        def is_predecessor(u, v):
            return (u, v) in [
                ("A", "B"),
                ("A", "C"),
                ("B", "D"),
                ("C", "D")
            ]
        
        result = topological_sort(nodes, is_predecessor)

        self.assertEqual(result[0], "A")
        self.assertEqual(result[-1], "D")
        # Ensure B and C come before D
        self.assertLess(result.index("B"), result.index("D"))
        self.assertLess(result.index("C"), result.index("D"))

    def test_multiple_independent_chains(self):
        # Chains: A -> B and C -> D
        nodes = ["A", "B", "C", "D"]
        def is_predecessor(u, v):
            return (u, v) in [("A", "B"), ("C", "D")]
        
        result = topological_sort(nodes, is_predecessor)

        # A before B, and C before D
        self.assertLess(result.index("A"), result.index("B"))
        self.assertLess(result.index("C"), result.index("D"))

    def test_cycle_raises(self):
        # Cycle: A -> B -> A
        nodes = ["A", "B"]
        def is_predecessor(u, v): 
            return (u, v) in [("A", "B"), ("B", "A")]
        
        with self.assertRaises(ValueError):
            topological_sort(nodes, is_predecessor)

    def test_disconnected_nodes(self):
        nodes = ["A", "B", "C"]
        def is_predecessor(u, v):
            return False
        
        result = topological_sort(nodes, is_predecessor)

        # All nodes appear, order doesn't matter
        self.assertCountEqual(result, nodes)


if __name__ == "__main__":
    main()
