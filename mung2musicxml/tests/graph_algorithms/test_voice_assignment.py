from unittest import TestCase, main
from fractions import Fraction
from mung2musicxml.utils import WrapperGraph


def make_linear_graph(n: int) -> WrapperGraph:
    """
    Creates a simple chain graph A -> B -> C -> ...
    """
    objs = [f"N{i}" for i in range(n)]

    def get_neighbors(o):
        idx = objs.index(o)
        return [objs[idx + 1]] if idx + 1 < len(objs) else []

    return WrapperGraph.from_other_graph(
        objs,
        get_neighbors=get_neighbors,
        get_start=lambda o: Fraction(objs.index(o)),
        get_duration=lambda o: Fraction(1),
        get_priority=lambda o: objs.index(o),
    )


def make_parallel_graph() -> WrapperGraph:
    """
    Creates a graph with 3 nodes starting at the same time.
    """
    objs = ["A", "B", "C"]

    def get_neighbors(_):
        return []

    return WrapperGraph.from_other_graph(
        objs,
        get_neighbors,
        get_start=lambda _: Fraction(0),
        get_duration=lambda _: Fraction(2),
        get_priority=lambda o: ord(o),
    )


def make_branching_graph() -> WrapperGraph:
    """
    Create a graph like this::

        A -> B -> C
               ↘ D
    """
    objs = ["A", "B", "C", "D"]

    def get_neighbors(o):
        if o == "A":
            return ["B"]
        elif o == "B":
            return ["C", "D"]
        else:
            return []

    starts = {
        "A": 0, "B": 1, "C": 2, "D": 2
    }

    return WrapperGraph.from_other_graph(
        objs,
        get_neighbors=get_neighbors,
        get_start=lambda o: starts[o],
        get_duration=lambda _: 1,
        get_priority=lambda o: ord(o),
    )


class TestAssignVoicesGroups(TestCase):
    """
    Tests for the assign_voices function.
    """

    def test_assign_linear_voices_without_groups(self):
        """
        Linear nodes all have the same voice.
        """
        g = make_linear_graph(3)
        voices = g.assign_voices()

        self.assertEqual(len(voices), len(g))
        self.assertTrue(all(isinstance(v, int) for v in voices.values()))
        self.assertTrue(all(voices[g[0]] == voices[n] for n in g))

    def test_assign_parallel_voices_without_groups(self):
        """
        Parallel nodes all have different voice.
        """
        g = make_parallel_graph()
        a, b, c = g._nodes

        voices = g.assign_voices()

        self.assertEqual(len(voices), len(g))
        self.assertNotEqual(voices[a], voices[c])
        self.assertNotEqual(voices[a], voices[b])
        self.assertNotEqual(voices[b], voices[c])

    def test_assign_branching_voices_without_groups(self):
        """
        Test a graph that starts linear and then branches to two nodes::

            A -> B -> C
                   ↘ D
        """
        g = make_branching_graph()
        a, b, c, d = g._nodes

        voices = g.assign_voices()

        self.assertEqual(len(voices), len(g))

        self.assertNotEqual(voices[c], voices[d])
        self.assertEqual(voices[a], voices[b])

    def test_assign_branching_voices_with_groups(self):
        """
        Test a graph that starts linear and then branches to two nodes.
        The group simulates a potential beam (or any other beam-like object)
        that connects nodes B, C or B, D::

            A -> B -> C
                   ↘ D
        """
        # connected B and C
        g = make_branching_graph()
        print(g)
        a, b, c, d = g._nodes

        voices_bc = g.assign_voices(groups=[[b, c]])
        print(voices_bc)

        self.assertEqual(len(voices_bc), len(g))

        self.assertNotEqual(voices_bc[c], voices_bc[d])
        self.assertEqual(voices_bc[a], voices_bc[b])
        self.assertEqual(voices_bc[b], voices_bc[c])

        # connected B and D
        g = make_branching_graph()
        print(g)
        a, b, c, d = g._nodes
        voices_bd = g.assign_voices(groups=[[b, d]])

        self.assertEqual(len(voices_bd), len(g))

        self.assertNotEqual(voices_bd[c], voices_bd[d])
        self.assertEqual(voices_bd[a], voices_bd[b])
        self.assertEqual(voices_bd[b], voices_bd[d])


if __name__ == "__main__":
    main()
