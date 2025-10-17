"""This module implements an abstraction over a notation graph, and
functions for manipulating notation graphs."""
import copy
from pathlib import Path
from queue import Queue
from typing import Iterable, Optional, Self, Any, TypeVar, Callable, Generator
from collections import defaultdict

from .node import Node
from .constants import (
    InferenceEngineConstants as I,
    PrecedenceLinksConstants as P,
    ClassNamesConstants as C
)
from .io import read_nodes_from_file, write_nodes_to_file
from .logger import logger


T = TypeVar("T")


class NotationGraphError(ValueError):
    pass


class NotationGraphUnsupportedError(NotImplementedError):
    pass


class NotationGraph(object):
    """The NotationGraph class is the abstraction for a notation graph."""

    def __init__(self, nodes: list[Node]):
        """Initialize the notation graph with a list of Nodes."""
        self.__nodes = nodes
        self.__id_to_node_mapping = {node.id: node for node in self.__nodes}  # type: dict[int, Node]

    @classmethod
    def from_file(cls, filename: str | Path) -> Self:
        """
        Initialize the notation graph from a file.

        :param filename: The path to the file containing the notation graph
        """
        return cls(read_nodes_from_file(filename))

    def save_to_file(self, file_path: str | Path, document: Optional[str] = None, dataset: Optional[str] = None) -> None:
        """
        Save the notation graph to a file.

        :param file_path: The path to the file where the notation graph should be saved.
        :param document: The document ID.
        :param dataset: The dataset ID.
        """
        if len(self.__nodes) > 0:
            if document is None:
                document = self.__nodes[0].document
                dataset = self.__nodes[0].dataset
        
        write_nodes_to_file(self.__nodes, file_path, document, dataset)

    def __len__(self):
        return len(self.__nodes)

    @staticmethod
    def __to_id(node_or_id: Node | int) -> int:
        if isinstance(node_or_id, Node):
            return node_or_id.id
        else:
            return node_or_id

    def __to_node(self, node_or_id: Node | int) -> Node:
        if isinstance(node_or_id, int):
            return self.__id_to_node_mapping[node_or_id]
        else:
            return node_or_id

    @staticmethod
    def __to_iterable(node_or_id: Iterable[T] | Any | None) -> list[T] | None:
        if node_or_id is None:
            return None
        if isinstance(node_or_id, (str, bytes)):
            return [node_or_id] # type: ignore
        if isinstance(node_or_id, Iterable):
            return list(node_or_id)
        return [node_or_id]

    @property
    def next_node_id(self) -> int:
        """
        Returns the next node ID.
        """
        return max([c.id for c in self.vertices]) + 1

    @property
    def edges(self) -> set[tuple[int, int]]:
        """
        Returns all edges in the notation graph.
        """
        edges = set()
        for node in self.__nodes:
            for t in node.outlinks:
                if (node.id, t) not in edges:
                    edges.add((node.id, t))
        return edges

    @property
    def precedence_edges(self) -> set[tuple[int, int]]:
        """
        Returns all precedence edges in the notation graph.
        """
        edges = set()
        for node in self.__nodes:
            for t in node.precedence_outlinks:
                edges.add((node.id, t))
        return edges

    @property
    def vertices(self) -> list[Node]:
        return self.__nodes

    def filter_vertices(self, class_filter: Iterable[str] | str) -> list[Node]:
        """
        Returns all vertices inside the graph that have the given class name.

        :param class_filter: Filter to only get nodes of given class name or names.
        :return: The vertices inside the graph that have the given class name.
        """
        class_filter = self.__to_iterable(class_filter) # type: ignore
        return [x for x in self.vertices if x.class_name in class_filter]
    
    def collect_data(
            self,
            key: Any,
            class_filter: Optional[Iterable[str] | str] = None,
            log_level: int = 1
        ) -> dict[int, Any]:
        """
        Retrieves values from the ``Node`` 's data field
        as a dictionary ``{ID: values}``.

        :param key: Key to retrieves values from.
        :param class_filter: Optional class filter.
        :param log_level: Raise ``KeyError``, if the level is set to 2,
            warning if 1 and suppress it, if 0.
        :return: Dictionary of node IDs to values.
        """
        if class_filter is None:
            nodes = self.vertices
        else:
            nodes = self.filter_vertices(class_filter)

        output: dict[int, Any] = {}
        for node in nodes:
            if key not in node.data:
                msg = f"Unknown key {key} for node {node.id}."
                match log_level:
                    case 0:
                        pass
                    case 1:
                        logger.warning(msg)
                    case _:
                        KeyError(msg)
            else:
                output[node.id] = node.data[key]
        
        return output

    def __getitem__(self, node_id: int) -> Node:
        """
        Returns a ``Node`` instance based on its id.
        """
        return self.__id_to_node_mapping[node_id]
    
    def _template_node_search_not_recursive_single_lookahead(
            self,
            node_or_id: Node | int,
            next_node_from_node: Callable[[Node], Iterable[Node]]
    ) -> list[Node]:
        """
        Returns a list of nodes that are one layer from the given node,
        based on the `next_node_from_node` function.
        """
        node_id = self.__to_id(node_or_id)

        if node_id not in self.__id_to_node_mapping:
            raise ValueError(f"Node {self.__id_to_node_mapping[node_id].id} not in graph!")

        source = self[node_id]
        children = []
        for child in next_node_from_node(source):
            if child.id in self.__id_to_node_mapping:
                children.append(child)
            else:
                logger.warning(f"Node {child.id} not in graph, skipping")
        return children
    
    def _template_filtered_node_search_not_recursive_single_lookahead(
            self,
            node_or_id: Node | int,
            class_filter: Optional[Iterable[str] | str],
            next_node_from_node: Callable[[Node], Iterable[Node]]
    ) -> list[Node]:
        """
        Adds class filter to the template function above.
        """
        class_filter = self.__to_iterable(class_filter)
        return self._template_node_search_not_recursive_single_lookahead(
            node_or_id,
            lambda n: (x for x in next_node_from_node(n) if class_filter is None or x.class_name in class_filter)
        )

    def children(self, node_or_id: Node | int, class_filter: Optional[Iterable[str] | str] = None) -> list[Node]:
        """
        Find all children of the given node. ``class_filter`` can be used to only get children of a particular class.

        :param node_or_id: The root ``Node`` ID or instance to search from.
        :param class_filter: Filter to only get nodes of given class name or names.
        :return: A list of ``Node`` objects.
        """
        return self._template_filtered_node_search_not_recursive_single_lookahead(
            node_or_id,
            class_filter,
            lambda n: (self[x] for x in n.outlinks)
        )
    
    def precedence_children(self, node_or_id: Node | int, class_filter: Optional[Iterable[str] | str] = None) -> list[Node]:
        """
        Find all precedence children of the given node. ``class_filter`` can be used to only get children of a particular class.

        :param node_or_id: The root ``Node`` ID or instance to search from.
        :param class_filter: Filter to only get nodes of given class name or names.
        :return: A list of ``Node`` objects.
        """
        return self._template_filtered_node_search_not_recursive_single_lookahead(
            node_or_id,
            class_filter,
            lambda n: (self[x] for x in n.precedence_outlinks)
        )

    def parents(self, node_or_id: Node | int, class_filter: Optional[Iterable[str] | str] = None) -> list[Node]:
        """
        Find all parents of the given node. ``class_filter`` can be used to only get children of a particular class.

        :param node_or_id: The root ``Node`` ID or instance to search from.
        :param class_filter: Filter to only get nodes of given class name or names.
        :return: A list of ``Node`` objects.
        """
        return self._template_filtered_node_search_not_recursive_single_lookahead(
            node_or_id,
            class_filter,
            lambda n: (self[x] for x in n.inlinks)
        )
    
    def precedence_parents(self, node_or_id: Node | int, class_filter: Optional[Iterable[str] | str] = None) -> list[Node]:
        """
        Find all precedence parents of the given node. ``class_filter`` can be used to only get children of a particular class.

        :param node_or_id: The root ``Node`` ID or instance to search from.
        :param class_filter: Filter to only get nodes of given class name or names.
        :return: A list of ``Node`` objects.
        """
        return self._template_filtered_node_search_not_recursive_single_lookahead(
            node_or_id,
            class_filter,
            lambda n: (self[x] for x in n.precedence_inlinks)
        )
    
    def _template_node_search_recursive_bfs(
            self,
            node_or_id: Node | int,
            get_next: Callable[[Node], Iterable[Node]]
    ) -> Generator[Node, None, None]:
        """
        Searches through nodes using BFS.
        Gets neighbors with ```get_next``.
        Returns a generator off nodes.
        """
        node_id = self.__to_id(node_or_id)
        node = self[node_id]
        
        # descendants: list[Node] = []
        visited: set[Node] = set([node])
        queue: Queue[Node] = Queue()
        queue.put(node)

        while not queue.empty():
            current_node = queue.get()
            if current_node != node:
                # descendants.append(current_node)
                yield current_node

            for child in get_next(current_node):
                if child not in visited:
                    visited.add(child)
                    queue.put(child)

        # return descendants
    
    def _template_filtered_node_search_recursive_bfs(
            self,
            node_or_id: Node | int,
            class_filter: Optional[Iterable[str] | str],
            get_next: Callable[[Node], Iterable[Node]]
    ) -> list[Node]:
        """
        Adds class filter over the found set.
        The search will pass through all nodes, even through
        those that are not included in the filter, but it will
        not output them.
        """
        class_filter = self.__to_iterable(class_filter)
        return [x for x in self._template_node_search_recursive_bfs(
            node_or_id,
            get_next)
            if class_filter is None or x.class_name in class_filter
        ]

    def descendants(self, node_or_id: Node | int, class_filter: Optional[Iterable[str] | str] = None) -> list[Node]:
        """
        Find all descendants of the given node. ``class_filter`` can be used to only get nodes of a particular class.

        :param node_or_id: The root ``Node`` ID or instance to search from.
        :param class_filter: Filter to only get nodes of given class name or names.
        :return: A list of ``Node`` objects.
        """
        return self._template_filtered_node_search_recursive_bfs(
            node_or_id,
            class_filter,
            self.children
        )
    
    def precedence_descendants(self, node_or_id: Node | int, class_filter: Optional[Iterable[str] | str] = None) -> list[Node]:
        """
        Find all precedence descendants of the given node. ``class_filter`` can be used to only get nodes of a particular class.

        :param node_or_id: The root ``Node`` ID or instance to search from.
        :param class_filter: Filter to only get nodes of given class name or names.
        :return: A list of ``Node`` objects.
        """
        return self._template_filtered_node_search_recursive_bfs(
            node_or_id,
            class_filter,
            self.precedence_children
        )

    def ancestors(self, node_or_id: Node | int, class_filter: Optional[Iterable[str] | str] = None) -> list[Node]:
        """
        Find all ancestors of the given node. ``class_filter`` can be used to only get nodes of a particular class.

        :param node_or_id: The root ``Node`` ID or instance to search from.
        :param class_filter: Filter to only get nodes of given class name or names.
        :return: A list of ``Node`` objects.
        """
        return self._template_filtered_node_search_recursive_bfs(
            node_or_id,
            class_filter,
            lambda n: self.parents(n)
        )
    
    def precedence_ancestors(self, node_or_id: Node | int, class_filter: Optional[Iterable[str] | str] = None) -> list[Node]:
        """
        Find all precedence ancestors of the given node. ``class_filter`` can be used to only get nodes of a particular class.

        :param node_or_id: The root ``Node`` ID or instance to search from.
        :param class_filter: Filter to only get nodes of given class name or names.
        :return: A list of ``Node`` objects.
        """
        return self._template_filtered_node_search_recursive_bfs(
            node_or_id,
            class_filter,
            lambda n: self.precedence_parents(n)
        )
    
    def has_children(self, node_or_id: Node | int, class_filter: Optional[Iterable[str] | str] = None) -> bool:
        """
        Returns true if given ``Node`` has at least one child.
        ``class_filter`` can be used to only count nodes of a particular class.

        :param node_or_id: The root ``Node`` ID or instance to search from.
        :param class_filter: Filter to only get nodes of given class name or names.
        :return: True if ``node_or_id`` has at least one child with specified ``class_filter``.
        """
        children = self.children(node_or_id, class_filter=class_filter)
        return len(children) > 0

    def has_parents(self, node_or_id: Node | int, class_filter: Optional[Iterable[str] | str] = None) -> bool:
        """
        Returns true if given ``Node`` has at least one parent.
        ``class_filter`` can be used to only count nodes of a particular class.

        :param node_or_id: The root ``Node`` ID or instance to search from.
        :param class_filter: Filter to only get nodes of given class name or names.
        :return: True if ``node_or_id`` has at least one parent with specified ``class_filter``.
        """
        parents = self.parents(node_or_id, class_filter=class_filter)
        return len(parents) > 0
    
    def has_precedence_children(self, node_or_id: Node | int, class_filter: Optional[Iterable[str] | str] = None) -> bool:
        children = self.precedence_children(node_or_id, class_filter)
        return len(children) > 0
    
    def has_precedence_parents(self, node_or_id: Node | int, class_filter: Optional[Iterable[str] | str] = None) -> bool:
        parents = self.precedence_parents(node_or_id, class_filter)
        return len(parents) > 0

    def is_child_of(self, child_node_or_id: Node | int, parent_node_or_id: Node | int) -> bool:
        """
        Check whether the first ``Node`` is a child of the second ``Node``.

        :param child_node_or_id: The child ``Node`` ID or instance.
        :param parent_node_or_id: The parent ``Node`` ID or instance.
        :return: True if ``child_node_or_id`` is a child of ``parent_node_or_id``.
        """
        child_id = self.__to_id(child_node_or_id)
        parent_id = self.__to_id(parent_node_or_id)

        parent = self.__id_to_node_mapping[parent_id]
        if child_id in parent.outlinks:
            return True

        return False

    def is_parent_of(self, parent_node_or_id: Node | int, child_node_or_id: Node | int) -> bool:
        """
        Check whether the first ``Node`` is a parent of the second ``Node``.

        :param parent_node_or_id: The parent ``Node`` ID or instance.
        :param child_node_or_id: The child ``Node`` ID or instance.
        :return: True if ``parent_node_or_id`` is a parent of ``child_node_or_id``
        """
        return self.is_child_of(child_node_or_id, parent_node_or_id)
    
    def is_precedence_child_of(self, child_node_or_id: Node | int, parent_node_or_id: Node | int) -> bool:
        """
        Check whether the first ``Node`` is a precedence child of the second ``Node``.

        :param child_node_or_id: The child ``Node`` ID or instance.
        :param parent_node_or_id: The parent ``Node`` ID or instance.
        :return: True if ``child_node_or_id`` is a precedence child of ``parent_node_or_id``.
        """
        child_id = self.__to_id(child_node_or_id)
        parent = self.__to_node(parent_node_or_id)

        if child_id in parent.precedence_outlinks:
            return True
        
        return False
    
    def is_precedence_parent_of(self, parent_node_or_id: Node | int, child_node_or_id: Node | int) -> bool:
        """
        Check whether the first ``Node`` is a precedence parent of the second ``Node``.

        :param parent_node_or_id: The parent ``Node`` ID or instance.
        :param child_node_or_id: The child ``Node`` ID or instance.
        :return: True if ``parent_node_or_id`` is a precedence parent of ``child_node_or_id``
        """
        return self.is_precedence_child_of(child_node_or_id, parent_node_or_id)

    def _template_is_relation_node_search(
            self,
            search_from: Node | int,
            search_for: Node | int,
            get_next: Callable[[Node], Iterable[Node]]
        ) -> bool:
        search_from = self.__to_node(search_from)
        search_for = self.__to_node(search_for)

        return search_for in self._template_node_search_recursive_bfs(
            search_from,
            get_next
        )
    
    def is_descendant_of(self, child_node_or_id: Node | int, parent_node_or_id: Node | int) -> bool:
        """
        Check whether the there exists a directed syntax path
        from the second ``Node`` to the first ``Node``.

        :param parent_node_or_id: The parent ``Node`` ID or instance.
        :param child_node_or_id: The child ``Node`` ID or instance.
        :return: True if ``child_node_or_id`` is syntax descendant of ``parent_node_or_id``.
        """
        return self._template_is_relation_node_search(
            parent_node_or_id, child_node_or_id,
            self.children
        )
    
    def is_ancestor_of(self, parent_node_or_id: Node | int, child_node_or_id: Node | int) -> bool:
        """
        Check whether the there exists a directed syntax path
        from the first ``Node`` to the second ``Node``.

        :param parent_node_or_id: The parent ``Node`` ID or instance.
        :param child_node_or_id: The child ``Node`` ID or instance.
        :return: True if ``parent_node_or_id`` is syntax ancestor of ``child_node_or_id``.
        """
        return self.is_descendant_of(child_node_or_id, parent_node_or_id)
    
    def is_precedence_descendant_of(self, child_node_or_id: Node | int, parent_node_or_id: Node | int) -> bool:
        """
        Check whether the there exists a directed precedence path
        from the second ``Node`` to the first ``Node``.

        :param parent_node_or_id: The parent ``Node`` ID or instance.
        :param child_node_or_id: The child ``Node`` ID or instance.
        :return: True if ``child_node_or_id`` is precedence descendant of ``parent_node_or_id``.
        """
        return self._template_is_relation_node_search(
            parent_node_or_id, child_node_or_id,
            self.precedence_children
        )
    
    def is_precedence_ancestor_of(self, parent_node_or_id: Node | int, child_node_or_id: Node | int) -> bool:
        """
        Check whether the there exists a directed precedence path
        from the first ``Node`` to the second ``Node``.

        :param parent_node_or_id: The parent ``Node`` ID or instance.
        :param child_node_or_id: The child ``Node`` ID or instance.
        :return: True if ``parent_node_or_id`` is precedence ancestor of ``child_node_or_id``.
        """
        return self.is_precedence_descendant_of(child_node_or_id, parent_node_or_id)

    def is_stem_direction_above(self, notehead: Node, stem: Node) -> bool:
        """Determines whether the given stem of the given notehead
        is above it or below. This is not trivial due to chords.
        """
        if notehead.id not in self.__id_to_node_mapping:
            raise NotationGraphError('Asking for notehead which is not in graph: {0}'.format(notehead.id))

        # This works even if there is just one. There should always be one.
        sibling_noteheads = self.parents(stem, class_filter=I.NOTEHEAD_CLASS_NAMES)
        if notehead not in sibling_noteheads:
            raise ValueError('Asked for stem direction, but notehead {0} is'
                             ' unrelated to given stem {1}!'
                             ''.format(notehead.id, stem.id))

        topmost_notehead = min(sibling_noteheads, key=lambda x: x.top)
        bottom_notehead = max(sibling_noteheads, key=lambda x: x.bottom)

        d_top = topmost_notehead.top - stem.top
        d_bottom = stem.bottom - bottom_notehead.bottom

        return d_top > d_bottom

    def is_symbol_above_notehead(self, notehead: Node, other: Node,
                                 compare_on_intersect: bool = False) -> bool:
        """Determines whether the given other symbol is above
        the given notehead.

        This is non-trivial because the other may reach above *and* below
        the given notehead, if it is long and slanted (beam, slur, ...).
        A horizontally intersecting subset of the mask of the other symbol
        is used to determine its vertical bounds relevant to the given object.
        """
        if other.mask is None:
            raise ValueError("Mask is None")
        
        if notehead.right <= other.left:
            # No horizontal overlap, notehead to the left
            beam_submask = other.mask[:, :1]
        elif notehead.left >= other.right:
            # No horizontal overlap, notehead to the right
            beam_submask = other.mask[:, -1:]
        else:
            h_bounds = (max(notehead.left, other.left),
                        min(notehead.right, other.right))

            beam_submask = other.mask[:, (h_bounds[0] - other.left):(h_bounds[1] - other.left)]

        # Get vertical bounds of beam submask
        other_submask_hsum = beam_submask.sum(axis=1)
        other_submask_top = min([i for i in range(beam_submask.shape[0])
                                 if other_submask_hsum[i] != 0]) + other.top
        other_submask_bottom = max([i for i in range(beam_submask.shape[0])
                                    if other_submask_hsum[i] != 0]) + other.top
        if (notehead.top <= other_submask_top <= notehead.bottom) \
                or (other_submask_bottom <= notehead.top <= other_submask_bottom):
            if compare_on_intersect:
                logger.warning('Notehead {0} intersecting other. Returning false.'.format(notehead.id))
                return False

        if notehead.bottom < other_submask_top:
            return False

        elif notehead.top > other_submask_bottom:
            return True

        else:
            raise NotationGraphError('Weird relative position of notehead'
                                     ' {0} and other {1}.'.format(notehead.id, other.id))

    def remove_vertex(self, node_or_id: Node | int):
        node = self.__to_node(node_or_id)
        self.remove_edges_for_vertex(node)
        self.__nodes.remove(node)
        del self.__id_to_node_mapping[node.id]

    def remove_edge(self, from_node_or_id: Node | int, to_node_or_id: Node | int, suppress_not_in_list_error: bool = False):
        from_node = self.__to_node(from_node_or_id)
        to_node = self.__to_node(to_node_or_id)
        from_id = self.__to_id(from_node_or_id)
        to_id = self.__to_id(to_node_or_id)

        if from_id not in self.__id_to_node_mapping:
            raise ValueError('Cannot remove edge from id {0}: not in graph!'
                             ''.format(from_node_or_id))
        if to_id not in self.__id_to_node_mapping:
            raise ValueError('Cannot remove edge to id {0}: not in graph!'
                             ''.format(to_node_or_id))
        
        if suppress_not_in_list_error:
            if to_node_or_id not in from_node.outlinks:
                logger.warning(f"Suppressing \"not in list\" error, {to_node_or_id} not in outlinks of {from_node_or_id}")
                return
            if from_node_or_id not in to_node.inlinks:
                logger.warning(f"Suppressing \"not in list\" error, {from_node_or_id} not in inlinks of {to_node_or_id}")
                return

        from_node.outlinks.remove(to_id)
        to_node.inlinks.remove(from_id)

    def remove_edges_for_vertex(self, node_or_id: Node | int):
        node = self.__to_node(node_or_id)

        if node.id not in self.__id_to_node_mapping:
            raise ValueError('Cannot remove node with id {0}: not in graph!'
                             ''.format(node.id))

        # Remove from inlinks and outlinks:
        for inlink in copy.deepcopy(node.inlinks):
            self.remove_edge(inlink, node)
        for outlink in copy.deepcopy(node.outlinks):
            self.remove_edge(node, outlink)

    def remove_classes(self, class_names: Iterable[str]):
        """Remove all vertices with these class names."""
        to_remove = [node.id for node in self.__nodes if node.class_name in class_names]
        for node_id in to_remove:
            self.remove_vertex(node_id)

    def remove_from_precedence(self, node_or_id: Node | int):
        """Bridge the precedence edges of the given object: each of its
        predecessors is linked to all of its descendants.
        If there are no predecessors or no descendants, the precedence
        edges are simply removed."""
        node_id = self.__to_id(node_or_id)
        node = self.__id_to_node_mapping[node_id]

        predecessors, descendants = [], []

        # Check if the node has at least some predecessors or descendants
        _has_predecessors = False
        if P.PRECEDENCE_INLINKS in node.data:
            _has_predecessors = (len(node.data[P.PRECEDENCE_INLINKS]) > 0)
        if _has_predecessors:
            predecessors = copy.deepcopy(
                node.data[P.PRECEDENCE_INLINKS])  # That damn iterator modification

        _has_descendants = False
        if P.PRECEDENCE_OUTLINKS in node.data:
            _has_descendants = (len(node.data[P.PRECEDENCE_OUTLINKS]) > 0)
        if _has_descendants:
            descendants = copy.deepcopy(node.data[P.PRECEDENCE_OUTLINKS])

        if (not _has_predecessors) and (not _has_descendants):
            return

        # Remove inlinks
        for predecessor_id in predecessors:
            predecessor = self.__id_to_node_mapping[predecessor_id]
            if P.PRECEDENCE_OUTLINKS not in predecessor.data:
                raise ValueError(
                    'Predecessor {} of Node {} does not have precedence outlinks!'
                    ''.format(predecessor_id, node.id))
            if node.id not in predecessor.data[P.PRECEDENCE_OUTLINKS]:
                raise ValueError('Predecessor {} of Node {} does not have reciprocal outlink!'
                                 ''.format(predecessor_id, node.id))
            predecessor.data[P.PRECEDENCE_OUTLINKS].remove(node.id)
            node.data[P.PRECEDENCE_INLINKS].remove(predecessor_id)

        # Remove outlinks
        for descendant_id in descendants:
            descendant = self.__id_to_node_mapping[descendant_id]
            if P.PRECEDENCE_INLINKS not in descendant.data:
                raise ValueError('Descendant {} of node {} does not have precedence inlinks!'
                                 ''.format(descendant_id, node.id))
            if node.id not in descendant.data[P.PRECEDENCE_INLINKS]:
                raise ValueError('Descendant {} of node {} does not have reciprocal inlink!'
                                 ''.format(descendant_id, node.id))
            descendant.data[P.PRECEDENCE_INLINKS].remove(node.id)
            node.data[P.PRECEDENCE_OUTLINKS].remove(descendant_id)

        # Bridge removed element
        for predecessor_id in predecessors:
            predecessor = self.__id_to_node_mapping[predecessor_id]
            for descendant_id in descendants:
                descendant = self.__id_to_node_mapping[descendant_id]
                if descendant_id not in predecessor.data[P.PRECEDENCE_OUTLINKS]:
                    predecessor.data[P.PRECEDENCE_OUTLINKS].append(descendant_id)
                if predecessor_id not in descendant.data[P.PRECEDENCE_INLINKS]:
                    descendant.data[P.PRECEDENCE_INLINKS].append(predecessor_id)

    def has_edge(self, from_id: int, to_id: int) -> bool:
        if from_id not in self.__id_to_node_mapping:
            logger.warning('Asking for object {}, which is not in graph.'.format(from_id))
        if to_id not in self.__id_to_node_mapping:
            logger.warning('Asking for object {}, which is not in graph.'.format(to_id))

        if to_id in self.__id_to_node_mapping[from_id].outlinks:
            if from_id in self.__id_to_node_mapping[to_id].inlinks:
                return True
            else:
                raise NotationGraphError('has_edge({}, {}): found {} in outlinks'
                                         ' of {}, but not {} in inlinks of {}!'
                                         ''.format(from_id, to_id, to_id, from_id, from_id, to_id))
        elif from_id in self.__id_to_node_mapping[to_id].inlinks:
            raise NotationGraphError('has_edge({}, {}): found {} in inlinks'
                                     ' of {}, but not {} in outlinks of {}!'
                                     ''.format(from_id, to_id, from_id, to_id, to_id, from_id))
        else:
            return False

    def add_edge(self, from_node_or_id: Node | int, to_node_or_id: Node | int):
        """Add an edge between the MuNGOs with ids ``from --> to``.
        If the edge is already in the graph, warns and does nothing."""
        from_id = self.__to_id(from_node_or_id)
        to_id = self.__to_id(to_node_or_id)

        if from_id not in self.__id_to_node_mapping:
            raise NotationGraphError('Cannot add edge from id {0}: not in graph!'.format(from_id))
        if to_id not in self.__id_to_node_mapping:
            raise NotationGraphError('Cannot add edge to id {0}: not in graph!'.format(to_id))
        
        from_node = self.__id_to_node_mapping[from_id]
        to_node = self.__id_to_node_mapping[to_id]
        
        if to_id in from_node.outlinks:
            if from_id in to_node.inlinks:
                logger.info('Adding edge that is already in the graph: {} --> {}'
                             ' -- doing nothing'.format(from_id, to_id))
                return
            else:
                raise NotationGraphError('add_edge({}, {}): found {} in outlinks'
                                         ' of {}, but not {} in inlinks of {}!'
                                         ''.format(from_id, to_id, to_id, from_id, from_id, to_id))
        elif from_id in self.__id_to_node_mapping[to_id].inlinks:
            raise NotationGraphError('add_edge({}, {}): found {} in inlinks'
                                     ' of {}, but not {} in outlinks of {}!'
                                     ''.format(from_id, to_id, from_id, to_id, to_id, from_id))

        self.__id_to_node_mapping[from_id].outlinks.append(to_id)
        self.__id_to_node_mapping[to_id].inlinks.append(from_id)

    def add_precedence_edge(self, from_node_or_id: Node | int, to_node_or_id: Node | int):
        """
        Add a *precedence* edge between the MuNGOs with ids ``from --> to``.
        If the edge is already in the graph, warns and does nothing.
        """
        from_id = self.__to_id(from_node_or_id)
        to_id = self.__to_id(to_node_or_id)
        if from_id not in self.__id_to_node_mapping:
            raise NotationGraphError('Cannot remove edge from id {0}: not in graph!'.format(from_id))
        if to_id not in self.__id_to_node_mapping:
            raise NotationGraphError('Cannot remove edge to id {0}: not in graph!'.format(to_id))

        from_node = self.__id_to_node_mapping[from_id]
        to_node = self.__id_to_node_mapping[to_id]

        if to_id in from_node.precedence_outlinks:
            if from_id in to_node.precedence_inlinks:
                logger.info('Adding edge that is already in the graph: {} --> {}'
                             ' -- doing nothing'.format(from_id, to_id))
                return
            else:
                raise NotationGraphError('add_edge({}, {}): found {} in outlinks'
                                         ' of {}, but not {} in inlinks of {}!'
                                         ''.format(from_id, to_id, to_id, from_id, from_id, to_id))
        elif from_id in to_node.precedence_inlinks:
            raise NotationGraphError('add_edge({}, {}): found {} in inlinks'
                                     ' of {}, but not {} in outlinks of {}!'
                                     ''.format(from_id, to_id, from_id, to_id, to_id, from_id))

        from_node.add_precedence_outlinks(to_id)
        to_node.add_precedence_inlinks(from_id)

    def remove_precedence_edge(self, from_node_or_id: Node | int, to_node_or_id: Node | int, suppress_not_in_list_error: bool = False):
        """
        Removes precedence edge ``from -> to``, does **not** bridge the created gap.
        """
        from_id = self.__to_id(from_node_or_id)
        to_id = self.__to_id(to_node_or_id)
        if from_id not in self.__id_to_node_mapping:
            raise ValueError(f"Cannot remove edge from id {from_id}: not in graph!")
        if to_id not in self.__id_to_node_mapping:
            raise ValueError(f"Cannot remove edge to id {to_id}: not in graph!")

        from_node = self.__id_to_node_mapping[from_id]
        to_node = self.__id_to_node_mapping[to_id]
        if suppress_not_in_list_error:
            if to_id not in from_node.precedence_outlinks:
                logger.warning(f"Suppressing \"not in list\" error, {to_id} not in outlinks of {from_id}")
                return
            if from_id not in to_node.precedence_inlinks:
                logger.warning(f"Suppressing \"not in list\" error, {from_id} not in inlinks of {to_id}")
                return

        from_node.precedence_outlinks.remove(to_id)
        to_node.precedence_inlinks.remove(from_id)


##############################################################################


T = TypeVar("T")

class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x: T):
        # path compression
        if self.parent.setdefault(x, x) != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a: T, b: T):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra
    
    @classmethod
    def merge_groups(cls, groups: list[list[T]]) -> list[list[T]]:
        """
        Merges groups based on shared elements.

        Example:
            >>> UnionFind.merge_groups([["A", "B"], ["B", "C"], ["D", "E"], ["D", "E"]])
            [["A", "B", "C"], ["D", "E"]]
        """
        if len(groups) == 0:
            return [[]]
        
        uf = cls()

        # union elements within each group
        for group in groups:
            if not group:
                continue
            first = group[0]
            for elem in group[1:]:
                uf.union(first, elem)

        # group by root
        merged = defaultdict(list)
        for group in groups:
            for elem in group:
                merged[uf.find(elem)].append(elem)

        # remove duplicates inside each component
        return [list(set(members)) for members in merged.values()]


def group_staffs_into_systems(nodes: list[Node],
                              use_fallback_measure_separators: bool = True,
                              leftmost_measure_separators_only: bool = False) -> list[list[Node]]:
    """Returns a list of lists of ``staff`` Nodes
    grouped into systems. Uses the outer ``staff_grouping``
    symbols (or ``measure_separator``) symbols.

    Currently, cannot deal with a situation where a system consists of
    interlocking staff groupings and measure separators, and cannot deal
    with system separator markings.

    :param nodes: The complete list of Nodes in the current
        document.

    :param use_fallback_measure_separators: If set and no staff groupings
        are found, will use measure separators instead to group
        staffs. The algorithm is to find the leftmost measure
        separator for each staff and use this set instead of staff
        groupings: measure separators also have outlinks to all
        staffs that they are relevant for.

    :param leftmost_measure_separators_only:

    :returns: A list of systems, where each system is a list of ``staff`` Nodes.
    """
    graph = NotationGraph(nodes)
    staff_groups = graph.filter_vertices(C.STAFF_GROUPING)
    
    def is_empty_staff(staff: Node, graph: NotationGraph) -> bool:
        durables = graph.parents(staff, class_filter=I.CLASSES_BEARING_DURATIONS)
        return len(durables) == 0

    empty_staffs = [s for s in graph.filter_vertices(C.STAFF) if is_empty_staff(s, graph)]
    if len(empty_staffs) > 0:
        logger.info(f"Empty staffs: {', '.join([str(node.id) for node in empty_staffs])}")

    # For simplicity, add non-empty staffs as potential systems.
    staff_groups += [s for s in graph.filter_vertices(C.STAFF) if s not in empty_staffs]

    # There might also be non-empty staffs that are nevertheless
    # not covered by a staff grouping, only measure separators.
    if use_fallback_measure_separators:
        # Collect measure separators, sort them left to right
        measure_separators = graph.filter_vertices(I.MEASURE_SEPARATOR_CLASS_NAMES)
        measure_separators = sorted(measure_separators, key=lambda x: x.left)
        # Use only the leftmost measure separator for each staff.
        staffs = [c for c in nodes if c.class_name in [I.STAFF]]

        if leftmost_measure_separators_only:
            leftmost_measure_separators = set()
            for staff in staffs:
                if staff in empty_staffs:
                    continue
                for m in measure_separators:
                    if graph.is_child_of(staff, m):
                        leftmost_measure_separators.add(m)
                        break
            staff_groups += leftmost_measure_separators
        else:
            staff_groups += measure_separators

    if len(staff_groups) == 0:
        return [[]]
    
    staffs_per_group = {node.id: graph.children(node, class_filter=C.STAFF) for node in staff_groups}
    
    merged = UnionFind.merge_groups(list(staffs_per_group.values()))
    for group in merged:
        group.sort(key=lambda x: x.top)
    merged.sort(key=lambda x: x[0].top)
    return merged


def group_by_staff(nodes: list[Node]) -> dict[int, list[Node]]:
    """Returns one NotationGraph instance for each staff and its associated
    Nodes. "Associated" means:

    * the object is a descendant of the staff,
    * the object is an ancestor of the staff, or
    * the object is a descendant of an ancestor of the staff, *except*
      measure separators and staff groupings.
    """
    g = NotationGraph(nodes=nodes)

    staffs = [c for c in nodes if c.class_name == I.STAFF]
    objects_per_staff = dict()  # type: dict[int, list[Node]]
    for staff in staffs:
        descendants = g.descendants(staff)
        ancestors = g.ancestors(staff)
        a_descendants = []
        for ancestor in ancestors:
            if ancestor.class_name in I.SYSTEM_LEVEL_CLASS_NAMES:
                continue
            _ad = g.descendants(ancestor)
            a_descendants.extend(_ad)
        staff_related = set()
        for c in descendants + ancestors + a_descendants:
            staff_related.add(c)

        objects_per_staff[staff.id] = list(staff_related)

    return objects_per_staff


def group_by_chord(graph: NotationGraph, nodes: list[Node]) -> list[list[Node]]:
    """
    Returns a closure of given ``nodes`` over chords.
    Chord are defined as notehead connected by a stem.

    Cannot deal with multistem noteheads.

    If nodes belong together to a chord, they are grouped together into a sublist.
    If a node or a symbol is not part of any chord, it is outputted in its own sublist.

    :param graph: Relevant ``NotationGraph`` instance.
    :param nodes: List of nodes that will be separated into chords.
    :return: List of lists of chords.
    """
    closure = []
    chord_mapping: dict[int, list[Node]] = {}
    for node in nodes:
        stems = graph.children(node, C.STEM)
        if len(stems) == 0:
            closure.append([node])
        elif len(stems) == 1:
            if stems[0].id not in chord_mapping:
                chord_mapping[stems[0].id] = [node]
            else:
                chord_mapping[stems[0].id].append(node)
        else:
            logger.debug("Cannot deal with multistem noteheads.")
            closure.append([node])
    
    for chord in chord_mapping.values():
        closure.append(chord)
    
    return closure


##############################################################################
# Graph search utilities

def find_related_staffs(query_nodes: list[Node], all_nodes: NotationGraph | list[Node],
                        with_stafflines: bool = True) -> list[Node]:
    """Find all staffs that are related to any of the nodes
    in question. Ignores whether these staffs are already within
    the list of ``query_nodes`` passed to the function.

    Finds all staffs that are ancestors or descendants of at least
    one of the query Nodes, and if ``with_stafflines`` is requested,
    all stafflines and staffspaces that are descendants of at least one
    of the related staffs as well.

    :param query_nodes: A list of Nodes for which we want
        to find related staffs. Subset of ``all_nodes``.

    :param all_nodes: A list of all the Nodes in the document
        (or directly a NotationGraph object). Assumes that the query
        Nodes are a subset of ``all_nodes``.

    :param with_stafflines: If set, will also return all stafflines
        and staffspaces related to the discovered staffs.

    :returns: List of staff (and, if requested, staffline/staffspace)
        Nodes that are relate to the query Nodes.
    """
    if not isinstance(all_nodes, NotationGraph):
        graph = NotationGraph(all_nodes)
    else:
        graph = all_nodes

    related_staffs = set()
    for c in query_nodes:
        desc_staffs = graph.descendants(c, class_filter=[I.STAFF])
        anc_staffs = graph.ancestors(c, class_filter=[I.STAFF])
        current_staffs = set(desc_staffs + anc_staffs)
        related_staffs = related_staffs.union(current_staffs)

    if with_stafflines:
        related_stafflines = set()
        for s in related_staffs:
            staffline_objs = graph.descendants(s, I.STAFFLINE_CLASS_NAMES)
            related_stafflines = related_stafflines.union(set(staffline_objs))
        related_staffs = related_staffs.union(related_stafflines)

    return list(related_staffs)


##############################################################################
# Graph validation/fixing.
# An invariant of these methods should be that they never remove a correct
# edge. There is a known problem in this if a second stem is marked across
# staves: the beam orientation misfires.


def find_beams_incoherent_with_stems(nodes: list[Node]) -> list[list[Node]]:
    """Searches the graph for edges where a notehead is connected to a stem
    in one direction, but is connected to beams that are in the
    other direction.

    If a notehead has zero or more than one stem, it is ignored.

    :returns: A list of (notehead, beam) pairs such that the beam
        is not coherent with the stem direction for the notehead.
    """
    graph = NotationGraph(nodes)
    noteheads = [c for c in nodes if c.class_name in I.NOTEHEAD_CLASS_NAMES]

    incoherent_pairs = []
    for notehead in noteheads:
        stems = graph.children(notehead, class_filter=['stem'])
        if len(stems) != 1:
            continue
        stem = stems[0]

        beams = graph.children(notehead, class_filter=['beam'])
        if len(beams) == 0:
            continue

        # Is the stem above the notehead, or not?
        # This is not trivial because of chords.
        is_stem_above = graph.is_stem_direction_above(notehead, stem)
        logger.info('IncoherentBeams: stem of {0} is above'.format(notehead.id))

        for beam in beams:
            try:
                is_beam_above = graph.is_symbol_above_notehead(notehead, beam)
            except NotationGraphError:
                logger.warning('IncoherentBeams: something is wrong in beam-notehead pair'
                                ' {0}, {1}'.format(beam.id, notehead.id))
                continue

            logger.info('IncoherentBeams: beam {0} of {1} is above'.format(beam.id, notehead.id))
            if is_stem_above != is_beam_above:
                incoherent_pairs.append([notehead, beam])

    return incoherent_pairs


# Leger lines often cause problems with autoparser.
# They should be always linked from noteheads in a consistent
# direction (from outside inwards to the staff).
# Also, no notehead should be connected to both a staffline/staffspace
# *AND* a leger line.

def find_leger_lines_with_noteheads_from_both_directions(nodes: list[Node]) -> list[Node]:
    """Looks for leger lines that have inlinks from noteheads
    on both sides. Returns a list of leger line Nodes."""
    graph = NotationGraph(nodes)

    problem_leger_lines = []

    for node in nodes:
        if node.class_name != I.LEGER_LINE:
            continue

        noteheads = graph.parents(node, class_filter=I.NOTEHEAD_CLASS_NAMES)

        if len(noteheads) < 2:
            continue

        positions = [resolve_notehead_wrt_staffline(notehead, node) for notehead in noteheads]
        positions_not_on_staffline = [p for p in positions if p != 0]
        unique_positions = set(positions_not_on_staffline)
        if len(unique_positions) > 1:
            problem_leger_lines.append(node)

    return problem_leger_lines


def find_noteheads_with_leger_line_and_staff_conflict(nodes: list[Node]) -> list[Node]:
    """Find all noteheads that have a relationship both to a staffline
    or staffspace and to a leger line.

    Assumes (obviously) that staffline relationships have already been
    resolved. Useful in a workflow where autoparsing is applied *after*
    staff inference.
    """
    graph = NotationGraph(nodes)

    problem_noteheads = []

    for node in nodes:
        if node.class_name not in I.NOTEHEAD_CLASS_NAMES:
            continue

        lls = graph.children(node, [I.LEGER_LINE])
        staff_objs = graph.children(node, I.STAFFLINE_CLASS_NAMES)
        if lls and staff_objs:
            problem_noteheads.append(node)

    return problem_noteheads


def find_noteheads_on_staff_linked_to_leger_line(nodes: list[Node]) -> list[Node]:
    """Find all noteheads that are linked to a leger line,
    but at the same time intersect a staffline or lie
    entirely within a staffspace. These should be fixed
    by linking them to the corresponding staffline/staffspace,
    but the fixing operation should be in infer_staffline_relationships.

    This is the opposite of what ``resolve_leger_line_or_staffline_object()`` is doing.
    """
    graph = NotationGraph(nodes)
    problem_noteheads = []

    stafflines = sorted([c for c in nodes if c.class_name == 'staff_line'],
                        key=lambda x: x.top)
    staffspaces = sorted([c for c in nodes if c.class_name == 'staff_space'],
                         key=lambda x: x.top)

    for node in nodes:
        if node.class_name not in I.NOTEHEAD_CLASS_NAMES:
            continue

        lls = graph.children(node, [I.LEGER_LINE])
        if len(lls) == 0:
            continue

        # Intersecting stafflines
        overlapped_stafflines = []
        for sl in stafflines:
            if node.overlaps(sl):
                overlapped_stafflines.append(sl)

        container_staffspaces = []
        for ss in staffspaces:
            if ss.contains(node):
                container_staffspaces.append(ss)

        if (len(overlapped_stafflines) + len(container_staffspaces)) > 0:
            problem_noteheads.append(node)

    return problem_noteheads


def find_misdirected_leger_line_edges(nodes: list[Node], retain_ll_for_disconnected_noteheads: bool = True) -> \
        list[list[Node]]:
    """Finds all edges that connect to leger lines, but do not
    lead in the direction of the staff.

    Silently assumes that all noteheads are connected to the correct staff.

    :param retain_ll_for_disconnected_noteheads:
        If the notehead would be left disconnected from all stafflines
        and staffspaces, retain its edges to its LLs -- it is better
        to get imperfect inference rather than for the PLAY button to fail.
    """
    graph = NotationGraph(nodes)

    misdirected_object_pairs = []

    for node in nodes:
        if node.class_name not in I.NOTEHEAD_CLASS_NAMES:
            continue

        lls = graph.children(node, [I.LEGER_LINE])
        if not lls:
            continue

        staffs = graph.children(node, [I.STAFF])
        if not staffs:
            logger.warning('Notehead {0} not connected to any staff!'.format(node.id))
            continue
        staff = staffs[0]

        # Determine whether notehead is above or below staff.
        # Because of mistakes in notehead-ll edges, can actually be
        # *on* the staff. (If it is on a staffline, then the edge is
        # definitely wrong.)
        stafflines = sorted(graph.children(staff, [I.STAFFLINE]),
                            key=lambda x: x.top)
        p_top = resolve_notehead_wrt_staffline(node, stafflines[0])
        p_bottom = resolve_notehead_wrt_staffline(node, stafflines[-1])
        # Notehead actually located on the staff somewhere:
        # all the LL RELs. are false.
        if (p_top != p_bottom) or (p_top == 0) or (p_bottom == 0):
            for ll in lls:
                misdirected_object_pairs.append([node, ll])
            continue

        notehead_staff_direction = 1
        if p_bottom == -1:
            notehead_staff_direction = -1

        _current_misdirected_object_pairs = []
        for ll in lls:
            ll_direction = resolve_notehead_wrt_staffline(node, ll)
            if (ll_direction != 0) and (ll_direction != notehead_staff_direction):
                misdirected_object_pairs.append([node, ll])
                _current_misdirected_object_pairs.append([node, ll])

        if retain_ll_for_disconnected_noteheads:
            staffline_like_children = graph.children(node, class_filter=[I.STAFFLINE,
                                                                         I.STAFFSPACE,
                                                                         I.LEGER_LINE])
            # If all the notehead's links to staffline-like objects are scheduled to be discarded:
            if len(staffline_like_children) == len(_current_misdirected_object_pairs):
                # Remove them from the schedule
                misdirected_object_pairs = misdirected_object_pairs[:-len(_current_misdirected_object_pairs)]

    return misdirected_object_pairs


def resolve_leger_line_or_staffline_object(nodes: list[Node]):
    """If staff relationships are created before notehead to leger line
    relationships, then there will be noteheads on leger lines that
    are nevertheless connected to staffspaces. This function should be
    applied after both staffspace and leger line relationships have been
    inferred, to guess whether the notehead's relationship to the staff
    object should be discarded.

    Has no dependence on misdirected edge detection (handles this as a part
    of the conflict resolution).
    """
    graph = NotationGraph(nodes)

    for node in nodes:
        if node.class_name not in I.NOTEHEAD_CLASS_NAMES:
            continue

        lls = graph.children(node, [I.LEGER_LINE])
        stafflines = graph.children(node, I.STAFFLINE_CLASS_NAMES)
        staff = graph.children(node, I.STAFF)

        if len(lls) == 0:
            continue
        if len(stafflines) == 0:
            continue

        if len(staff) == 0:
            logger.warning('Notehead {0} not connected to any staff!'
                            ' Unable to resolve ll/staffline.'.format(node.id))
            continue

        # Multiple LLs: must check direction
        # Multiple stafflines: ???
        if len(stafflines) > 1:
            logger.warning('Notehead {0} is connected to multiple staffline'
                            ' objects!'.format(node.id))


##############################################################################

def _nodes_or_graph_to_graph(nodes_or_graph: Iterable[Node] | NotationGraph) -> NotationGraph:
    if isinstance(nodes_or_graph, NotationGraph):
        return nodes_or_graph
    return NotationGraph(list(nodes_or_graph))


def group_by_system_measure(nodes_or_graph: list[Node] | NotationGraph) -> list[list[Node]]:
    """
    Groups the objects into system measures.

    If no measure separators are found, assumes everything belongs
    to one measure.

    :returns: A list of lists of nodes that belong to the same system measure,
        sorted from top left to bottom right.
    """
    graph = _nodes_or_graph_to_graph(nodes_or_graph)
    
    systems = group_staffs_into_systems(graph.vertices)

    def get_all_separators_from_system(staffs: list[Node], graph: NotationGraph) -> set[Node]:
        """
        Finds all measure separators inside a system defined by a list of staffs.
        """
        output: set[Node] = set()
        for staff in staffs:
            output.update(graph.parents(staff, class_filter=C.MEASURE_SEPARATOR))
        
        return output
    
    def get_all_in_measure_symbols_from_system(staffs: list[Node], graph: NotationGraph) -> list[Node]:
        output: list[Node] = []
        for staff in staffs:
            for symbol in graph.parents(staff, class_filter=I.IN_MEASURE):
                if symbol in output:
                    logger.warning(f"Symbol {symbol.class_name} {symbol.id} assigned to multiple staffs in the same system")
                else:
                    output.append(symbol)
        return output

    measures: list[list[Node]] = []
    for system in systems:
        separators = sorted(get_all_separators_from_system(system, graph), key=lambda n: n.horizontal_center)
        symbols = get_all_in_measure_symbols_from_system(system, graph)

        bins = [[] for _ in range(len(separators) + 1)]

        for x in symbols:
            for i, upper in enumerate(separators):
                if x.horizontal_center <= upper.horizontal_center:
                    bins[i].append(x)
                    break
            else:
                bins[-1].append(x)

        # remove last bin, if it is empty
        # (there might be an unclosed measure)
        if len(bins[-1]) == 0:
            bins = bins[:-1]
        
        measures.extend(bins)
    
    # debug prints
    for i, measure in enumerate(measures):
        logger.debug(f"Found system measure {i}: {[x.id for x in measure]}")
    
    return measures


def group_by_measure(nodes_or_graph: list[Node] | NotationGraph) -> list[list[Node]]:
    """Groups the objects into measures.
    Assumes the measures are consistent across staffs: no polytempi.

    :returns: A list of Node lists corresponding to measures. The list
        is ordered left-to-right.
    """
    # TODO:
    raise NotImplementedError
    graph = _nodes_or_graph_to_graph(nodes_or_graph)
    system_measures = group_by_system_measure(graph)
    output: list[list[Node]] = []

    for sm in system_measures:
        
        measures: defaultdict[Node, list[Node]] = defaultdict(list)
        # split symbols inside a single system measure to measure based on their linkage to staffs
        for symbol in sm:
            staffs = sorted(graph.children(symbol, class_filter=C.STAFF), key=lambda x: x.id)
            if len(staffs) == 0:
                raise ValueError(f"Symbol {symbol.class_name} {symbol.id} is not linked to any staff")
            if len(staffs) > 1:
                logger.warning(f"Symbol {symbol.class_name} {symbol.id} is linked to multiple staffs, choosing the one with smallest id")
            staff = staffs[0]
            measures[staff].append(symbol)

        # append found measures to the output and 
        output.extend([measures[staff] for staff in measures.keys()])

    raise NotImplementedError()


##############################################################################
# Searching for MuNGOs that are contained within other MuNGOs
# and removing them safely from the MuNG.

def find_contained_nodes(nodes: list[Node], mask_threshold: float = 0.95):
    """Find all nodes that are contained within other nodes
    and not connected by an edge from container to contained.

    Does *NOT* check for transitive edges!"""
    graph = NotationGraph(nodes)

    # We should have some smarter indexing structure here, but since
    # we are just checking bounding boxes for candidates first,
    # it does not matter too much.

    nonstaff_nodes = [node for node in nodes if node.class_name not in I.STAFF_CLASSES]

    contained_nodes = []
    for c1 in nonstaff_nodes:
        for c2 in nonstaff_nodes:
            if c1.id == c2.id:
                continue
            if c1.contains(c2):
                # Check mask overlap
                r, p, f = c1.compute_recall_precision_fscore_on_mask(c2)
                if r < mask_threshold:
                    continue
                if c2.id in c1.outlinks:
                    continue
                contained_nodes.append(c2)

    # Make unique
    return [c for c in set(contained_nodes)]


def remove_contained_nodes(nodes: list[Node], contained: list[Node]) -> list[Node]:
    """Removes ``contained`` Nodes from ``nodes`` so that the
    graph takes minimum damage.

    * Attachment edges of contained objects are removed.
    * For precedence edges, we link all precedence ancestors of a removed node
      to all its descendants.
    """
    # Operating on a copy. Inefficient, but safe.
    output_nodes = [copy.deepcopy(c) for c in nodes]

    # The nodes are then edited in-place by manipulating
    # the graph; hence we can then just return output_nodes.
    graph = NotationGraph(output_nodes)
    for c in contained:
        graph.remove_from_precedence(c.id)
    for c in contained:
        graph.remove_vertex(c.id)

    return graph.vertices


def resolve_notehead_wrt_staffline(notehead: Node, staffline_or_leger_line: Node) -> int:
    """Resolves the relative vertical position of the notehead with respect
    to the given staff_line or legerLine object. Returns -1 if notehead
    is *below* staffline, 0 if notehead is *on* staffline, and 1 if notehead
    is *above* staffline."""
    ll = staffline_or_leger_line

    # Determining whether the notehead is on a leger
    # line or in the adjacent temp staffspace.
    # This uses a magic number, ON_STAFFLINE_RATIO_THRESHOLD.
    output_position = 0

    # Weird situation with notehead vertically *inside* bbox
    # of leger line (could happen with slanted LLs and very small
    # noteheads).
    if ll.top <= notehead.top <= notehead.bottom <= ll.bottom:
        output_position = 0

    # No vertical overlap between LL and notehead
    elif ll.top > notehead.bottom:
        output_position = 1
    elif notehead.top > ll.bottom:
        output_position = -1

    # Complicated situations: overlap
    else:
        # Notehead "around" leger line.
        if notehead.top < ll.top <= ll.bottom < notehead.bottom:
            dtop = ll.top - notehead.top
            dbottom = notehead.bottom - ll.bottom

            if min(dtop, dbottom) / max(dtop, dbottom) \
                    < I.ON_STAFFLINE_RATIO_THRESHOLD:
                if dtop > dbottom:
                    output_position = 1
                else:
                    output_position = -1

        # Notehead interlaced with leger line, notehead on top
        elif notehead.top < ll.top <= notehead.bottom <= ll.bottom:
            output_position = 1

        # Notehead interlaced with leger line, leger line on top
        elif ll.top <= notehead.top <= ll.bottom < notehead.bottom:
            output_position = -1

        else:
            logger.warning('Strange notehead {0} vs. leger line {1}'
                            ' situation: bbox notehead {2}, LL {3}.'
                            ' Note that the output position is unusable;'
                            ' pleasre re-do this attachment manually.'
                            ''.format(notehead.id, ll.id,
                                      notehead.bounding_box,
                                      ll.bounding_box))
    return output_position


def is_notehead_on_line(notehead: Node, line: Node) -> bool:
    """Check whether given notehead is positioned on the line object."""
    if line.class_name not in I.STAFFLINE_LIKE_CLASS_NAMES:
        raise ValueError('Cannot resolve relative position of notehead'
                         ' {0} to non-staffline-like object {1}'
                         ''.format(notehead.id, line.id))

    position = resolve_notehead_wrt_staffline(notehead, line)
    return position == 0
