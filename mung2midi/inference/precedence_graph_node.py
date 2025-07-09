from mung.node import Node
from typing import Optional
from fractions import Fraction


class PrecedenceGraphNode(object):
    """A helper plain-old-data class for onset extraction.
    The ``inlinks`` and ``outlinks`` attributes are lists
    of other ``PrecedenceGraphNode`` instances.
    """

    def __init__(
        self,
        objid=None,
        node: Optional[Node] = None,
        inlinks: Optional[list[int]] = None,
        outlinks: Optional[list[int]] = None,
        onset: Optional[Fraction] = None,
        duration: Fraction = Fraction(0),
    ):
        # Optional link to Nodes, or just a placeholder ID.
        self.obj = node
        if objid is None and node is not None:
            objid = node.id
        self.node_id = objid

        self.inlinks = []
        if inlinks:
            self.inlinks = inlinks
        self.outlinks = []
        if outlinks:
            self.outlinks = outlinks

        self.onset = onset
        """
        Counting from the start of the musical sequence, how many
        beat units pass before this object?
        """

        self.duration = duration
        """
        By how much musical time does the object delay the onsets
        of its descendants in the precedence graph?
        """

        self.data = node.data if node else {}
