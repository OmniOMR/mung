from mung import NotationGraph, Node
from mung.constants import ClassNameConstants as C, InferenceEngineConstants as I

from ...logger import logger


class PrecedenceLinker:
    """
    Ensures that noteheads connected by the same stem share a common onset by filling in missing precedence edges.
    """
    def __init__(self):
        self._graph: NotationGraph = None #type: ignore

    def __call__(self, graph: NotationGraph) -> NotationGraph:
        self.complete_precedence_graph(graph)
        self.reset()
        return graph
    
    @classmethod
    def run(cls, graph: NotationGraph) -> NotationGraph:
        return cls()(graph)

    def _set_graph(self, graph: NotationGraph) -> None:
        self._graph = graph
    
    def reset(self) -> None:
        self._graph = None #type: ignore

    def _chord_from_stem(self, stem: Node) -> list[Node]:
        return self._graph.parents(stem, class_filter=I.NOTEHEAD_CLASS_NAMES)
    
    def _chord_from_notehead(self, notehead: Node) -> list[Node]:
            output = []

            stems = self._graph.children(notehead, class_filter=C.NoteheadAttachments.STEM)
            if len(stems) > 1:
                logger.warning("Notehead with multiple stems found, returning all connected noteheads")
            
            for stem in stems:
                output.extend(self._chord_from_stem(stem))
            
            return output
    
    def _get_succeeding_from_chord(self, chord: list[Node]) -> set[Node]:
            nodes = []
            for notehead in chord:
                for precedence_out_id in notehead.precedence_outlinks:
                    precedence_out = self._graph[precedence_out_id]
                    # If the succeeding symbol is a notehead,
                    # expand the list of succeeding symbols with all symbols that are with it in a chord.
                    if precedence_out.class_name in I.NOTEHEAD_CLASS_NAMES:
                        nodes.extend(self._chord_from_notehead(self._graph[precedence_out_id]))
                    else:
                        nodes.append(precedence_out)
            return set(nodes)
    
    def _get_preceding_from_chord(self, chord: list[Node]) -> set[Node]:
            nodes = []
            for notehead in chord:
                for precedence_in_id in notehead.precedence_inlinks:
                    precedence_in = self._graph[precedence_in_id]
                    # If the succeeding symbol is a notehead,
                    # expand the list of succeeding symbols with all symbols that are with it in a chord.
                    if precedence_in.class_name in I.NOTEHEAD_CLASS_NAMES:
                        nodes.extend(self._chord_from_notehead(self._graph[precedence_in_id]))
                    else:
                        nodes.append(precedence_in)
            return set(nodes)

    def complete_precedence_graph(self, graph: NotationGraph) -> None:
        """
        Ensures that noteheads connected by the same stem share a common onset by filling in missing precedence edges.

        After running this, in each group of noteheads connected to the same stem - forming a chord,
        all noteheads are connected to the same set of other symbols participating in the precedence
        graph.

        Runs a forward and backward pass - looks at preceding and succeeding symbols to the chord.

        Graph is modified in-place.
        """
        self._set_graph(graph)
        stems = self._graph.filter_vertices(C.NoteheadAttachments.STEM)
        total = 0
        for stem in stems:
            chord = self._chord_from_stem(stem)
            if len(chord) == 0:
                logger.warning(f"Stem {stem.id} has no noteheads assigned")
                continue

            if len(chord) == 1:
                continue

            succeeding = self._get_succeeding_from_chord(chord)
            preceding = self._get_preceding_from_chord(chord)
            for c in chord:
                for s in succeeding:
                    if c.id not in s.precedence_inlinks:
                        graph.add_precedence_edge(c.id, s.id)
                        total += 1
                for p in preceding:
                    if c.id not in p.precedence_outlinks:
                        graph.add_precedence_edge(p.id, c.id)
                        total += 1
        
        logger.info(f"Filled in {total} precedence edges")
