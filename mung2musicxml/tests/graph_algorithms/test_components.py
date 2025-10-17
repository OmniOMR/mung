from unittest import TestCase, main

from mung2musicxml.utils import WrapperGraph, WrapperNode


class TestDAGComponents(TestCase):
    
    def build(self, edges):
        objs = set([u for u, _ in edges] + [v for _, v in edges])
        nodes = {o: WrapperNode(o) for o in objs}
        for u, v in edges:
            nodes[u].children.append(nodes[v])
        return WrapperGraph(list(nodes.values()))

    def test_single_component_chain(self):
        # A -> B -> C
        graph = self.build([("A", "B"), ("B", "C")])
        comps = graph.get_components()
        self.assertEqual(len(comps), 1)
        self.assertEqual({n.obj for n in comps[0]}, {"A", "B", "C"})

    def test_two_disconnected_components(self):
        # Component 1: A -> B
        # Component 2: C -> D
        graph = self.build([("A", "B"), ("C", "D")])
        comps = graph.get_components()
        comp_objs = [set(n.obj for n in comp) for comp in comps]
        self.assertCountEqual(comp_objs, [{"A", "B"}, {"C", "D"}])

    def test_single_node_component(self):
        # Just one node, no edges
        graph = WrapperGraph([WrapperNode("X")])
        comps = graph.get_components()
        self.assertEqual(len(comps), 1)
        self.assertEqual({n.obj for n in comps[0]}, {"X"})

    def test_mixed_graph(self):
        # Component 1: A -> B -> C
        # Component 2: D
        # Component 3: E -> F
        graph = self.build([("A", "B"), ("B", "C"), ("E", "F")])
        graph._nodes.append(WrapperNode("D"))
        comps = graph.get_components()
        comp_objs = [set(n.obj for n in comp) for comp in comps]
        self.assertCountEqual(comp_objs, [{"A", "B", "C"}, {"D"}, {"E", "F"}])

    def test_empty_graph(self):
        graph = WrapperGraph([])
        comps = graph.get_components()
        self.assertEqual(len(comps), 0)


if __name__ == "__main__":
    main()
