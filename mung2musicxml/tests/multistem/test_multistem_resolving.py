from unittest import TestCase, main
from parameterized import parameterized
from itertools import product
import numpy as np

from mung import Node, NotationGraph
from mung.constants import ClassNamesConstants as C
from mung2musicxml.preprocessing.multistem import MultistemResolver
from ..utils import DummyNode


class TestDoubleStemResolving(TestCase):
    resolver = MultistemResolver()
    @parameterized.expand([
        (C.NOTEHEAD_FULL), (C.NOTEHEAD_HALF)
    ])
    def test_simple_single_no_precedence(self, name: str):
        """
        Single voice, single double stemmed notehead::

             |
            o
           |
        """
        _id = 0
        staff = DummyNode(_id, C.STAFF) # 0
        _id += 1
        original_note = DummyNode(_id, name) # 1
        _id += 1
        stem_up = DummyNode(_id, C.STEM, top=0) # 2
        _id += 1
        stem_down = DummyNode(_id, C.STEM, top=5) # 3
        
        graph = NotationGraph([staff, original_note, stem_up, stem_down])
        graph.add_edge(original_note, stem_up)
        graph.add_edge(original_note, stem_down)
        graph.add_edge(original_note, staff)
        ghost_node_id = 4

        graph = self.resolver(graph)

        self.assertEqual(original_note.class_name, graph[ghost_node_id].class_name)
        self.assertEqual(len(graph.vertices), ghost_node_id + 1)
        self.assertSetEqual(graph.edges, {
            (1, 0), (ghost_node_id, 0), (1, 2), (ghost_node_id, 3)
        })
    
    @parameterized.expand(
            product([C.NOTEHEAD_FULL, C.NOTEHEAD_HALF],
                    [C.NOTEHEAD_FULL, C.NOTEHEAD_HALF, C.NOTEHEAD_WHOLE])
    )
    def test_simple_incoming_single_precedence(self, original_name: str, other_name: str):
        """
        Single voice, single double stemmed notehead
        and a single preceding note::

                    |
            o  ->  o
                  |
        """
        _id = 0
        staff = DummyNode(_id, C.STAFF) # 0
        _id += 1
        original_note = DummyNode(_id, original_name) # 1
        _id += 1
        stem_up = DummyNode(_id, C.STEM, top=0) # 2
        _id += 1
        stem_down = DummyNode(_id, C.STEM, top=5) # 3
        _id += 1
        other_note = DummyNode(_id, other_name) # 4 (leaving out stem)
        
        graph = NotationGraph([staff, original_note, stem_up, stem_down, other_note])
        graph.add_edge(original_note, stem_up)
        graph.add_edge(original_note, stem_down)
        graph.add_edge(original_note, staff)
        graph.add_edge(other_note, staff)
        graph.add_precedence_edge(other_note, original_note)
        ghost_node_id = graph.next_node_id
        graph = self.resolver(graph)

        self.assertEqual(original_note.class_name, graph[ghost_node_id].class_name)
        self.assertEqual(len(graph.vertices), ghost_node_id + 1)
        self.assertSetEqual(graph.edges, {
            (1, 0), (4, 0), (ghost_node_id, 0), (1, 2), (ghost_node_id, 3)
        })
        self.assertSetEqual(graph.precedence_edges, {
            (other_note.id, original_note.id), (other_note.id, ghost_node_id)
        })
    
    @parameterized.expand(
            product([C.NOTEHEAD_FULL, C.NOTEHEAD_HALF],
                    [C.NOTEHEAD_FULL, C.NOTEHEAD_HALF, C.NOTEHEAD_WHOLE],
                    [C.NOTEHEAD_FULL, C.NOTEHEAD_HALF, C.NOTEHEAD_WHOLE],)
    )
    def test_simple_incoming_double_precedence(self, original_name: str, other_name: str, other_name2: str):
        """
        Two voices, single double stemmed notehead
        and a two preceding half/full notes::

            o       |
               ->  o
            o     |
        """
        _id = 0
        staff = DummyNode(_id, C.STAFF) # 0
        _id += 1
        original_note = DummyNode(_id, original_name) # 1
        _id += 1
        stem_up = DummyNode(_id, C.STEM, top=0) # 2
        _id += 1
        stem_down = DummyNode(_id, C.STEM, top=5) # 3
        _id += 1
        other_note = DummyNode(_id, other_name, top=0) # 4 (leaving out stem)
        _id += 1
        other_note2 = DummyNode(_id, other_name2, top=5) # 5 (leaving out stem)
        
        graph = NotationGraph([staff, original_note, stem_up, stem_down, other_note, other_note2])
        graph.add_edge(original_note, stem_up)
        graph.add_edge(original_note, stem_down)
        graph.add_edge(original_note, staff)
        graph.add_edge(other_note, staff)
        graph.add_edge(other_note2, staff)
        graph.add_precedence_edge(other_note, original_note)
        graph.add_precedence_edge(other_note2, original_note)
        ghost_node_id = graph.next_node_id

        graph = self.resolver(graph)

        self.assertEqual(original_note.class_name, graph[ghost_node_id].class_name)
        self.assertEqual(len(graph.vertices), ghost_node_id + 1)
        self.assertSetEqual(graph.edges, {
            (1, 0), (4, 0), (5, 0), (ghost_node_id, 0), (1, 2), (ghost_node_id, 3)
        })
        
        expected_edges = {
            (other_note.id, original_note.id),
            (other_note2.id, ghost_node_id),
            (other_note.id, ghost_node_id),
            (other_note2.id, original_note.id)
        }
        
        self.assertSetEqual(graph.precedence_edges, expected_edges)

    @parameterized.expand(
            product([C.NOTEHEAD_FULL, C.NOTEHEAD_HALF],
                    [C.NOTEHEAD_FULL, C.NOTEHEAD_HALF, C.NOTEHEAD_WHOLE],
                    [C.NOTEHEAD_FULL, C.NOTEHEAD_HALF, C.NOTEHEAD_WHOLE],)
    )
    def test_simple_outgoing_double_precedence(self, original_name: str, other_name: str, other_name2: str):
        """
        Two voices, single double stemmed notehead
        and a two succeeding half/full notes::

              |      o
             o   -> 
            |        o
        """
        _id = 0
        staff = DummyNode(_id, C.STAFF) # 0
        _id += 1
        original_note = DummyNode(_id, original_name) # 1
        _id += 1
        stem_up = DummyNode(_id, C.STEM, top=0) # 2
        _id += 1
        stem_down = DummyNode(_id, C.STEM, top=5) # 3
        _id += 1
        other_note = DummyNode(_id, other_name, top=0) # 4 (leaving out stem)
        _id += 1
        other_note2 = DummyNode(_id, other_name2, top=5) # 5 (leaving out stem)
        
        graph = NotationGraph([staff, original_note, stem_up, stem_down, other_note, other_note2])
        graph.add_edge(original_note, stem_up)
        graph.add_edge(original_note, stem_down)
        graph.add_edge(original_note, staff)
        graph.add_edge(other_note, staff)
        graph.add_edge(other_note2, staff)
        graph.add_precedence_edge(original_note, other_note)
        graph.add_precedence_edge(original_note, other_note2)
        ghost_node_id = graph.next_node_id

        graph = self.resolver(graph)

        self.assertEqual(original_note.class_name, graph[ghost_node_id].class_name)
        self.assertEqual(len(graph.vertices), ghost_node_id + 1)
        self.assertSetEqual(graph.edges, {
            (1, 0), (4, 0), (5, 0), (ghost_node_id, 0), (1, 2), (ghost_node_id, 3)
        })
        
        expected_edges = {
            (original_note.id, other_note.id),
            (original_note.id, other_note2.id)
        }
        
        self.assertSetEqual(graph.precedence_edges, expected_edges)

    @parameterized.expand(
            product([C.NOTEHEAD_FULL],
                    [C.NOTEHEAD_FULL, C.NOTEHEAD_HALF, C.NOTEHEAD_WHOLE],
                    [C.NOTEHEAD_FULL, C.NOTEHEAD_HALF, C.NOTEHEAD_WHOLE],
                    [-5, 5],
                    [C.FLAG_8TH_UP, C.BEAM]
                    )
    )
    def test_different_length_outgoing_double_precedence(
        self,
        original_name: str,
        other_name: str,
        other_name2: str,
        modifier_orientation: int,
        modifier_name: str
    ):
        """
        Two voices, single double stemmed notehead
        and a two succeeding half/full notes,
        the original note or the ghost will have
        precedence outlinks to notes on the right::

              |\     o
             o   -> 
            |        o
        """
        _id = 0
        staff = DummyNode(_id, C.STAFF) # 0
        _id += 1
        original_note = DummyNode(_id, original_name) # 1
        _id += 1
        stem_up = DummyNode(_id, C.STEM, top=-5) # 2
        _id += 1
        stem_down = DummyNode(_id, C.STEM, top=5) # 3
        _id += 1
        other_note = DummyNode(_id, other_name, top=0) # 4 (leaving out stem)
        _id += 1
        other_note2 = DummyNode(_id, other_name2, top=5) # 5 (leaving out stem)
        _id += 1
        flag = DummyNode(_id, modifier_name, top=modifier_orientation, width=1, height=1, mask=np.array([[1]])) # 6 (orientation does not matter)
        
        graph = NotationGraph([staff, original_note, stem_up, stem_down, other_note, other_note2, flag])
        graph.add_edge(original_note, stem_up)
        graph.add_edge(original_note, stem_down)
        graph.add_edge(original_note, staff)
        graph.add_edge(other_note, staff)
        graph.add_edge(other_note2, staff)
        graph.add_edge(original_note, flag)
        graph.add_precedence_edge(original_note, other_note)
        graph.add_precedence_edge(original_note, other_note2)
        ghost_node_id = graph.next_node_id

        graph = self.resolver(graph)

        self.assertEqual(original_note.class_name, graph[ghost_node_id].class_name)
        self.assertEqual(len(graph.vertices), ghost_node_id + 1)
        if modifier_orientation < 0:
            self.assertSetEqual(graph.edges, {
                (1, 0), (4, 0), (5, 0), (ghost_node_id, 0), (1, 2), (ghost_node_id, 3), (original_note.id, flag.id)
            })
        else:
            self.assertSetEqual(graph.edges, {
                (1, 0), (4, 0), (5, 0), (ghost_node_id, 0), (1, 2), (ghost_node_id, 3), (ghost_node_id, flag.id)
            })
        
        if modifier_orientation < 0:
            expected_edges = {
                (original_note.id, other_note.id),
                (original_note.id, other_note2.id)
            }
        else:
            expected_edges = {
                (ghost_node_id, other_note.id),
                (ghost_node_id, other_note2.id)
            }
        
        self.assertSetEqual(graph.precedence_edges, expected_edges)


if __name__ == "__main__":
    main()