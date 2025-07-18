import collections
import copy
import inspect
import logging
import operator
import warnings
from fractions import Fraction
from typing import Optional, Iterable

from mung.constants import InferenceEngineConstants, ClassNamesConstants, PrecedenceLinksConstants
from mung.graph import group_staffs_into_systems, NotationGraph, NotationGraphError
from mung.node import bounding_box_dice_coefficient, Node
from .precedence_graph_node import PrecedenceGraphNode
from dataclasses import dataclass

@dataclass(frozen=True)
class BaseOnsetsInferenceStrategy(object):
    permissive_desynchronization: bool = True
    precedence_only_for_objects_connected_to_staff: bool = True
    permissive: bool = True
    link_sinks_to_sources_at_ends_and_starts_of_systems: bool = True


class OnsetsInferenceEngine(object):
    _CONST = InferenceEngineConstants()
    _DEFAULT_FRACTIONAL_VERTICAL_IOU_THRESHOLD = 0.8

    def __init__(
            self,
            strategy: Optional[BaseOnsetsInferenceStrategy] = None,
            nodes_or_graph: Optional[list[Node] | NotationGraph] = None
    ):
        """Initialize the onset inference engine with the full Node
        list in a document."""
        if strategy is None:
            strategy = BaseOnsetsInferenceStrategy()
        self.__strategy = strategy
        # self.id_to_node_mapping = {c.id: c for c in nodes}
        self.strategy = strategy

        if nodes_or_graph is not None:
            if isinstance(nodes_or_graph, NotationGraph):
                self.__graph: NotationGraph = nodes_or_graph
            else:
                self.__graph: NotationGraph = NotationGraph(nodes_or_graph)
        else:
            self.__graph: NotationGraph = None

    def durations(self, nodes: list[Node], ignore_modifiers: bool = False) -> dict[int, Fraction]:
        """Returns a dict that contains the durations (in beats)
        of all Nodes that should be associated with a duration.
        The dict keys are ``id``.

        :param ignore_modifiers: If set, will ignore duration dots,
            tuples, and other potential duration modifiers when computing
            the durations. Effectively, this gives you classes that
            correspond to note(head) type: whole (4.0), half (2.0),
            quarter (1.0), eighth (0.5), etc.
        """
        # Generate & return the durations dictionary.
        _relevant_clsnames = self._CONST.classes_bearing_duration
        duration_nodes = [c for c in nodes
                          if c.class_name in _relevant_clsnames]

        durations = {c.id: self.beats(c, ignore_modifiers=ignore_modifiers)
                     for c in duration_nodes}
        return durations

    def beats(self, node: Node, ignore_modifiers=False):
        if node.class_name in self._CONST.NOTEHEAD_CLASS_NAMES:
            return self.notehead_beats(node,
                                       ignore_modifiers=ignore_modifiers)
        elif node.class_name in self._CONST.REST_CLASS_NAMES:
            return self.rest_beats(node,
                                   ignore_modifiers=ignore_modifiers)
        else:
            raise ValueError('Cannot compute beats for object {0} of class {1};'
                             ' beats only available for notes and rests.'
                             ''.format(node.id, node.class_name))

    def notehead_beats(self, notehead: Node, ignore_modifiers=False) -> Fraction:
        """Retrieves the duration for the given notehead, in beats.

        It is possible that the notehead has two stems.
        In that case, we return all the possible durations:
        usually at most two, but if there is a duration dot, then
        there can be up to 4 possibilities.

        Grace notes currently return 0 beats.

        :param notehead: Notehead to infer beats for.
        :param ignore_modifiers: If given, will ignore all duration
            modifiers: Duration dots, tuples, and other potential duration
            modifiers when computing the durations. Effectively, this
            gives you classes that correspond to note(head) type:
            whole (4.0), half (2.0), quarter (1.0), eighth (0.5), etc.
        :returns: A single possible durations for the given notehead.
            Mostly its length is just 1; for multi-stem noteheads,
            the output is reduced to just the first one.
            TODO: This might lead to problems later.
        """
        beat = [Fraction(0)]

        stems = self.children(notehead, [self._CONST.STEM])
        flags_and_beams = self.children(
            notehead,
            self._CONST.FLAGS_AND_BEAMS)

        if notehead.class_name in self._CONST.GRACE_NOTEHEAD_CLASS_NAMES:
            logging.warning('Notehead {0}: Grace notes get zero duration!'
                            ''.format(notehead.id))
            beat = [Fraction(0)]

        elif len(stems) > 1:
            logging.warning('Inferring duration for multi-stem notehead: {0}'
                            ''.format(notehead.id))
            beat = self.process_multistem_notehead(notehead)
            if len(beat) > 1:
                self.__warning_or_error('Cannot deal with multi-stem notehead'
                                        ' where multiple durations apply.')
                beat = [max(beat)]

        elif notehead.class_name == self._CONST.NOTEHEAD_HALF or notehead.class_name == self._CONST.NOTEHEAD_WHOLE:
            if len(flags_and_beams) != 0:
                raise ValueError(
                    'Notehead {0} is empty, but has {1} flags and beams!'.format(notehead.id, len(flags_and_beams)))

            if len(stems) == 0:
                beat = [Fraction(4)]
            else:
                beat = [Fraction(2)]

        elif notehead.class_name == self._CONST.NOTEHEAD_FULL:
            if len(stems) == 0:
                self.__warning_or_error('Full notehead {0} has no stem!'.format(notehead.id))

            beat = [Fraction(1, 2) ** len(flags_and_beams)]

        else:
            raise ValueError('Notehead {0}: unknown class_name {1}'
                             ''.format(notehead.id, notehead.class_name))

        if not ignore_modifiers:
            duration_modifier = self._compute_duration_modifier(notehead)
            beat = [b * duration_modifier for b in beat]

        if len(beat) > 1:
            logging.warning('Notehead {0}: more than 1 duration: {1}, choosing first'
                            ''.format(notehead.id, beat))
        return beat[0]

    def _check_graph_init(self):
        if self.__graph is None:
            raise ValueError("Initialize the graph first")

    def initialize_graph(self, nodes_or_graph: list[Node] | NotationGraph):
        if isinstance(nodes_or_graph, NotationGraph):
            self.__graph: NotationGraph = nodes_or_graph
        else:
            self.__graph: NotationGraph = NotationGraph(nodes_or_graph)

    def _compute_duration_modifier(self, notehead: Node) -> Fraction:
        """Computes the duration modifier (multiplicative, in beats)
        for the given notehead (or rest) from the tuples and duration dots.

        Can handle duration dots within tuples.

        Cannot handle nested/multiple tuples.
        """
        self._check_graph_init()

        duration_modifier = 1
        # Dealing with tuples:
        tuples = self.children(notehead, [self._CONST.TUPLE])
        if len(tuples) > 1:
            raise ValueError('Notehead {0}: Cannot deal with more than one tuple'
                             ' simultaneously.'.format(notehead.id))
        if len(tuples) == 1:
            tuple_ = tuples[0]

            # Find the number in the tuple.
            numerals = self.children(tuple_, InferenceEngineConstants.NUMERALS)

            if len(numerals) == 0:
                logging.warning(f"Tuple {tuple_.id} has no numerals!")
            elif len(numerals) > 3:
                logging.warning(f"Tuple {tuple_.id} has more than 3 numerals!")

            tuple_number = self.interpret_numerals(sorted(numerals, key=lambda x: x.left))

            # Fallback, the list of numbers was empty or corrupted in some way,
            # Count noteheads attached to that tuple
            if tuple_number is None:
                tuple_number = len(self.__parents(tuple_, InferenceEngineConstants.NOTEHEAD_CLASS_NAMES))

            # Last note in tuple should get complementary duration
            # to sum to a whole. Otherwise, playing brings slight trouble.

            if tuple_number == 2:
                # Duola makes notes *longer*
                duration_modifier = Fraction(3, 2)
            elif tuple_number == 3:
                duration_modifier = Fraction(2, 3)
            elif tuple_number == 4:
                # This one also makes notes longer
                duration_modifier = Fraction(4, 3)
            elif tuple_number == 5:
                duration_modifier = Fraction(4, 5)
            elif tuple_number == 6:
                # Most often done for two consecutive triolas,
                # e.g. 16ths with a 6-tuple filling one beat
                duration_modifier = Fraction(2, 3)
            elif tuple_number == 7:
                # Here we get into trouble, because this one
                # can be both 4 / 7 (7 16th in a beat)
                # or 8 / 7 (7 32nds in a beat).
                # In the same vein, we cannot resolve higher
                # tuples unless we establish precedence/simultaneity.
                logging.warning('Cannot really deal with higher tuples than 6.')
                # For MUSCIMA++ specifically, we can cheat: there is only one
                # septuple, which consists of 7 x 32rd in 1 beat, so they
                # get 8 / 7.
                logging.warning('MUSCIMA++ cheat: we know there is only 7 x 32rd in 1 beat in page 14.')
                duration_modifier = Fraction(8, 7)
            elif tuple_number == 10:
                logging.warning('MUSCIMA++ cheat: we know there is only 10 x 32rd in 1 beat in page 04.')
                duration_modifier = Fraction(4, 5)
            else:
                raise NotImplementedError(f"Notehead {notehead.id}: Cannot deal with tuple number {tuple_number}")

        # Duration dots
        ddots = self.children(notehead, ClassNamesConstants.AUGMENTATION_DOT)
        dot_duration_modifier = Fraction(1)
        for i, d in enumerate(ddots):
            dot_duration_modifier += Fraction(1, 2) ** (i + 1)
        duration_modifier *= dot_duration_modifier

        return duration_modifier

    def rest_beats(self, rest: Node, ignore_modifiers=False) -> Fraction:
        """Compute the duration of the given rest in beats.

        :param rest: Rest node.
        :param ignore_modifiers: If given, will ignore all duration
            modifiers: Duration dots, tuples, and other potential duration
            modifiers when computing the durations. Effectively, this
            gives you classes that correspond to note(head) type:
            whole (4.0), half (2.0), quarter (1.0), eighth (0.5), etc.
            Also ignores deriving duration from the time signature
            for whole rests.
        """
        base_rest_duration = ClassNamesConstants.rest_name_to_duration(rest.class_name)
        # Process the whole rest:
        #  - if it is the only symbol in the measure, it should take on
        #    the duration of the current time signature.
        #  - if it is not the only symbol in the measure, it takes 4 beats
        #  - Theoretically, it could perhaps take e.g. 6 beats in weird situations
        #    in a 6/2 time signature, but we don't care about this for now.
        #
        # If there is no leftward time signature, we need to infer the time
        # sig from the other symbols. This necessitates two-pass processing:
        # first get all available durations, then guess the time signatures
        # (technically this might also be needed for each measure).
        if (rest.class_name in self._CONST.MEASURE_LASTING_CLASS_NAMES) and not ignore_modifiers:
            base_rest_duration = self.measure_lasting_beats(rest)
            if rest.class_name == ClassNamesConstants.REST_BREVE:
                beat = [base_rest_duration * 2]
            elif rest.class_name == ClassNamesConstants.REST_LONGA:
                beat = [base_rest_duration * 4]
            else:
                beat = [base_rest_duration]  # Measure duration should never be ambiguous.

        elif not ignore_modifiers:
            duration_modifier = self._compute_duration_modifier(rest)
            beat = [base_rest_duration * duration_modifier]

        else:
            beat = [base_rest_duration]

        if len(beat) > 1:
            logging.warning('Rest {0}: more than 1 duration: {1}, choosing first'
                            ''.format(rest.id, beat))
        return beat[0]

    def measure_lasting_beats(self, node: Node) -> Fraction:
        """Find the duration of an object that lasts for an entire measure
        by interpreting the time signature valid for the given point in
        the score.

        If any assumption is broken, will return the default measure duration:
        4 beats."""
        # Find rightmost preceding time signature on the staff.
        # graph = NotationGraph(list(self.id_to_node_mapping.values()))

        # Find current time signature
        staffs = self.__graph.children(node, class_filter=[self._CONST.STAFF])

        if len(staffs) == 0:
            logging.warning('Interpreting object {0} as measure-lasting, but'
                            ' it is not attached to any staff! Returning default: 4'
                            ''.format(node.id))
            return Fraction(4)

        if len(staffs) > 1:
            logging.warning('Interpreting object {0} as measure-lasting, but'
                            ' it is connected to more than 1 staff: {1}'
                            ' Returning default: 4'
                            ''.format(node.id, [s.id for s in staffs]))
            return Fraction(4)

        logging.info('Found staffs: {0}'.format([s.id for s in staffs]))

        staff = staffs[0]
        time_signatures = self.__graph.ancestors(staff, class_filter=self._CONST.TIME_SIGNATURES)

        logging.info('Time signatures: {0}'.format([t.id for t in time_signatures]))

        applicable_time_signatures = sorted([t for t in time_signatures
                                             if t.left < node.left],
                                            key=operator.attrgetter('left'))
        logging.info('Applicable time signatures: {0}'.format([t.id for t in time_signatures]))

        if len(applicable_time_signatures) == 0:
            logging.warning('Interpreting object {0} as measure-lasting, but'
                            ' there is no applicable time signature. Returnig'
                            ' default: 4'.format(node.id))
            return Fraction(4)

        valid_time_signature = applicable_time_signatures[-1]
        beats = self.interpret_time_signature(valid_time_signature)
        return beats

    def process_multistem_notehead(self, notehead: Node) -> list[Fraction]:
        """Attempts to recover the duration options of a multi-stem note."""
        stems = self.children(notehead, ClassNamesConstants.STEM)
        flags_and_beams = self.children(
            notehead,
            InferenceEngineConstants.FLAGS_AND_BEAMS
        )

        if len(flags_and_beams) == 0:
            if notehead.class_name == ClassNamesConstants.NOTEHEAD_FULL:
                return [Fraction(1)]
            elif notehead.class_name in InferenceEngineConstants.NOTEHEADS_EMPTY:
                return [Fraction(2)]

        if notehead.class_name in InferenceEngineConstants.NOTEHEADS_EMPTY:
            raise NotationGraphError('Empty notehead with flags and beams: {0}'
                                     ''.format(notehead.id))

        n_avg_x = notehead.top + (notehead.bottom - notehead.top) / 2.0
        print('Notehead {0}: avg_x = {1}'.format(notehead.id, n_avg_x))
        f_and_b_above = []
        f_and_b_below = []
        for c in flags_and_beams:
            c_avg_x = c.top + (c.bottom - c.top) / 2.0
            print('Beam/flag {0}: avg_x = {1}'.format(c.id, c_avg_x))
            if c_avg_x < n_avg_x:
                f_and_b_above.append(c)
                print('Appending above')
            else:
                f_and_b_below.append(c)
                print('Appending below')

        beat_above = Fraction(1, 2) ** len(f_and_b_above)
        beat_below = Fraction(1, 2) ** len(f_and_b_below)

        if beat_above != beat_below:
            raise NotImplementedError('Cannot deal with multi-stem note'
                                      ' that has different pre-modification'
                                      ' durations: {0} vs {1}'
                                      '{2}'.format(beat_above, beat_below, notehead.id))

        beat = [beat_above]

        tuples = self.children(notehead, [self._CONST.TUPLE])
        if len(tuples) % 2 != 0:
            raise NotImplementedError('Cannot deal with multi-stem note'
                                      ' that has an uneven number of tuples:'
                                      ' {0}'.format(notehead.id))

        duration_modifier = self._compute_duration_modifier(notehead)
        beat = [b * duration_modifier for b in beat]

        return beat

    ##########################################################################
    # Onsets inference
    def _infer_precedence_from_annotations(self, nodes: list[Node]):
        """Infer precedence graph based solely on the "green lines"
        in MUSCIMA++ annotation: precedence edges. These are encoded
        in the data as inlink/outlink lists
        in ``Node.data['precedence_inlinks']``,
        and ``Node.data['precedence_outlinks']``.

        :param nodes: A list of Nodes, not necessarily
            only those that participate in the precedence graph.

        :return: The list of source nodes of the precedence graph.
        """
        self._check_graph_init()

        _relevant_class_names = self._CONST.classes_bearing_duration
        # precedence_nodes = [c for c in nodes
        #                     if c.class_name in _relevant_clsnames]
        precedence_nodes = self.__graph.filter_vertices(_relevant_class_names)

        if self.strategy.precedence_only_for_objects_connected_to_staff:
            precedence_nodes = [c for c in precedence_nodes
                                if len(self.children(c, [self._CONST.STAFF])) > 0]

        durations = {c.id: self.beats(c) for c in precedence_nodes}

        p_nodes = {}
        for c in precedence_nodes:
            p_node = PrecedenceGraphNode(
                objid=c.id,
                node=c,
                inlinks=[],
                outlinks=[],
                duration=durations[c.id],
            )
            p_nodes[c.id] = p_node

        for c in p_nodes.values():
            inlinks = []
            outlinks = []
            if PrecedenceLinksConstants.PrecedenceInlinks in c.data:
                inlinks = c.data[PrecedenceLinksConstants.PrecedenceInlinks]
            if PrecedenceLinksConstants.PrecedenceOutlinks in c.data:
                outlinks = c.data[PrecedenceLinksConstants.PrecedenceOutlinks]
            p_node = p_nodes[c.node_id]
            p_node.outlinks = [p_nodes[o] for o in outlinks]
            p_node.inlinks = [p_nodes[i] for i in inlinks]

        # Join staves/systems!

        # ...systems:
        systems = group_staffs_into_systems(nodes,
                                            use_fallback_measure_separators=True)

        if len(systems) == 1:
            logging.info('Single-system score, no staff chaining needed.')
            source_nodes = [n for n in list(p_nodes.values()) if len(n.inlinks) == 0]
            return source_nodes

        if not self.strategy.link_sinks_to_sources_at_ends_and_starts_of_systems:
            logging.info("Strategy to not connect sinks and sources applied")
            source_nodes = [n for n in list(p_nodes.values()) if len(n.inlinks) == 0]
            return source_nodes

        # Check all systems same no. of staffs
        _system_lengths = [len(s) for s in systems]
        if len(set(_system_lengths)) > 1:
            raise ValueError('Cannot deal with variable number of staffs'
                             ' w.r.t. systems! Systems: {0}'.format(systems))

        staff_chains = [[] for _ in systems[0]]
        for system in systems:
            for i, staff in enumerate(system):
                staff_chains[i].append(staff)

        # Now, join the last --> first nodes within chains.
        # - Assign objects to staffs
        objid2staff = {}
        for c in nodes:
            staffs = self.children(c, [InferenceEngineConstants.STAFF])
            if len(staffs) == 1:
                objid2staff[c.id] = staffs[0].id

        # - Assign staffs to sink nodes
        sink_nodes2staff = {}
        staff2sink_nodes = collections.defaultdict(list)
        for node in list(p_nodes.values()):
            if len(node.outlinks) == 0:
                try:
                    staff = self.children(node.obj, [InferenceEngineConstants.STAFF])[0]
                except IndexError:
                    logging.error('Object {0} is a sink node in the precedence graph, but has no staff!'
                                  ''.format(node.obj.id))
                    raise
                sink_nodes2staff[node.obj.id] = staff.id
                staff2sink_nodes[staff.id].append(node)

        # Note that this means you should never have a sink node
        # unless it's at the end of the staff. All notes have to lead
        # somewhere. This is suboptimal; we should filter out non-maximal
        # sink nodes. But since we do not know whether the sink nodes
        # are maximal until we are done inferring onsets, we have to stick
        # with this.
        # The alternative is to only connect to the next staff the *rightmost*
        # sink node. This risks *not* failing if the sink nodes of a staff
        # are not synchronized properly.

        # - Assign staffs to source nodes
        source_nodes2staff = {}
        staff2source_nodes = collections.defaultdict(list)
        for node in list(p_nodes.values()):
            if len(node.inlinks) == 0:
                staff = self.children(node.obj, [InferenceEngineConstants.STAFF])[0]
                source_nodes2staff[node.obj.id] = staff.id
                staff2source_nodes[staff.id].append(node)

        # - For each staff chain, link the sink nodes of the prev
        #   to the source nodes of the next staff.
        for staff_chain in staff_chains:
            staffs = sorted(staff_chain, key=lambda x: x.top)
            for (s1, s2) in zip(staffs[:-1], staffs[1:]):
                sinks = staff2sink_nodes[s1.id]
                sources = staff2source_nodes[s2.id]
                for sink in sinks:
                    for source in sources:
                        sink.outlinks.append(source)
                        source.inlinks.append(sink)

        # print(staff2sink_nodes)
        # print(staff2source_nodes)
        #
        # raise ValueError()

        source_nodes = [n for n in list(p_nodes.values()) if len(n.inlinks) == 0]
        return source_nodes

    def infer_precedence(self, nodes: list[Node]):
        """This is the most complex part of onset computation.

        The output of this method is a **precedence graph**. The precedence
        graph is a Directed Acyclic Graph (DAG) consisting of
        :class:`PrecedenceGraphNode` objects. Each node represents some
        musical concept that participates in establishing the onsets
        by having a *duration*. The invariant of the graph is that
        the onset of a node is the sum of the durations on each of its
        predecessor paths to a root node (which has onset 0).

        Not all nodes necessarily have nonzero duration (although these
        nodes can technically be factored out).

        Once the precedence graph is formed, then a breadth-first search
        (rather than DFS, to more easily spot/resolve conflicts at multi-source
        precedence graph nodes) simply accumulates durations.
        Conflicts can be resolved through failing (currently implemented),
        or looking up possible errors in assigning durations and attempting
        to fix them.

        Forming the precedence graph itself is difficult, because
        of polyphonic (and especially pianoform) music. Practically the only
        actual constraint followed throughout music is that *within a voice*
        notes are read left-to-right. The practice of aligning e.g. whole
        notes in an outer voice to the beginning of the bar rather than
        to the middle took over only cca. 1800 or later.

        An imperfect but overwhelmingly valid constraint is that notes taking
        up a certain proportion of the measure are not written to the *right*
        of the proportional horizontal span in the measure corresponding
        to their duration in time. However, this is *not* uniform across
        the measure: e.g., if the first voice is 2-8-8-8-8 and the second
        is 2-2, then the first half can be very narrow and the second
        quite wide, with the second lower-voice half-note in the middle
        of that part. However, the *first* lower-voice half-note will
        at least *not* be positioned in the horizontal span where
        the 8th notes in the upper voice are.

        Which Nodes participate in the precedence graph?
        ------------------------------------------------------

        We directly derive precedence graph nodes from the following
        Nodes:

        * Noteheads: empty, full, and grace noteheads of both kinds, which
          are assigned duration based on their type (e.g., quarter, 16th, etc.)
          and then may be further modified by duration dots and/or tuples.
        * Rests of all kinds, which get duration via a simple table based
          on the rest class and tuple/dot modification.
        * Measure separators, which get a duration of 0.

        The assumption of our symbol classes is that there are no rests
        shorter than 64th.

        Furthermore, we add synthetic nodes representing:

        * Root measure separator, with duration 0 **and** onset 0,
          which initializes the onset computations along the graph
        * Measure nodes, with durations derived from time signatures
          valid for the given measures.

        Constructing the precedence graph
        ---------------------------------

        We factor the precedence graph into measures, and then infer precedence
        for each measure separately, in order to keep the problem tractable
        and in order for errors not to propagate too far. The inference
        graph construction algorithm is therefore split into two steps:

        * Construct the "spine" of the precedence graph from measure nodes,
        * Construct the single-measure precedence subgraphs (further factored
          by staff).

        The difficulties lie primarily in step 2.

        (Note that ties are currently disregarded: the second note
        of the tie normally gets an onset. After all, conceptually,
        it is a separate note with an onset, it just does not get played.)

        Precedence graph spine
        ^^^^^^^^^^^^^^^^^^^^^^

        The **spine** of the precedence graph is a single path of alternating
        ``measure_separator`` and ``measure`` nodes. ``measure_separator``
        nodes are constructed from the Nodes, and ``measure`` nodes
        are created artificially between consecutive ``measure_separator``
        nodes. The measure separator nodes have a duration of 0, while
        the duration of the measure nodes is inferred from the time signature
        valid for that measure. An artificial root measure_separator node
        is created to serve as the source of the entire precedence graph.

        Thus, the first part of the algorithm is, at a high level:

        * Order measure separators,
        * Assign time signatures to measures and compute measure durations
          from time signatures.

        **Gory details:** In step 1, we assume that systems are ordered
        top-down in time, that all systems are properly grouped using
        ``staff_grouping`` symbols, that measure separators are strictly
        monotonous (i.e., the same subset of possible onsets belongs to
        the i-th measure on each staff, which is an assumption that does
        *not* hold for isorhythmic motets and basically anything pre-16th
        century).

        In step 2, we assume that time signatures are always written within
        the measure that *precedes* the first measure for which they are
        valid, with the exception of the first time signature on the system.

        We also currently assume that a given measure has the same number
        of beats across all staves within a system (so: no polytempi for now).

        Measure subgraphs
        ^^^^^^^^^^^^^^^^^

        There are again two high-level steps:

        * Assign other onset-carrying objects (noteheads and rests)
          to measures, to prepare the second phase that iterates over
          these groups per measure (and staff).
        * For each measure group, compute the subgraph and attach
          its sources to the preceding measure separator node.

        The first one can be resolved easily by looking at (a) staff
        assignment, (b) horizontal position with respect to measure
        separators. Noting that long measure separators might not
        really be straight, we use the intersection of the separator
        with the given staff.

        The second step is the difficult one. We describe the algorithm
        for inferring precedence, simultaneity span minimization,
        in a separate section.


        Simultaneity span minimization
        ------------------------------

        Inferring precedence in polyphonic music is non-trivial, especially
        if one wants to handle handwritten music, and even more so when
        extending the scope before the 1800s. We infer precedence using
        the principle that notes which are supposed to be played together
        should be as close to each other horizontally as possible: from
        all the possible precedence assignments that fulfill notation
        rule constraints, choose the one which minimizes the horizontal
        span assigned to each unit of musical time in the bar.

        The algorithm is initialized as follows:

        * Determine the shortest subdivision of the measure (in beats)
          which has to be treated independently. This generally corresponds
          to the shortest note in the measure.
        * Initialize the assignment table: for each onset-carrying object,
          we will assign it to one of the time bins.

        There are some rules of music notation that we use to prune the space
        of possible precedence assignments by associating the notes (or rests)
        into blocks:

        * Beamed groups without intervening rests
        * Tied note pairs
        * Notes that share a stem
        * Notes within a tuple

        Rests within beamed groups (e.g., 8th - 8th_rest - 8th) are a problem.
        A decision needs to be made whether the rest does belong to the group
        or not.

        """
        func_name = inspect.currentframe().f_code.co_name
        warnings.warn(
            f"{func_name}() is deprecated.",
            category=DeprecationWarning,
            stacklevel=2
        )
        #
        # if not self.measure_separators:
        #     self._collect_symbols_for_pitch_inference(nodes)

        measure_separators = [c for c in nodes
                              if c.class_name in self._CONST.MEASURE_SEPARATOR_CLASS_NAMES]

        ######################################################################
        # An important feature of measure-factorized onset inference
        # instead of going left-to-right per part throughout is resistance
        # to staves appearing & disappearing on line breaks (e.g. orchestral
        # scores). Measures are (very, very often) points of synchronization
        #  -- after all, that is their purpose.

        # We currently DO NOT aim to process renaissance & medieval scores:
        # especially motets may often have de-synchronized measure separators.

        # Add the relationships between the measure separator nodes.
        #  - Get staves to which the mseps are connected
        msep_staffs = {m.id: self.children(m, [InferenceEngineConstants.STAFF])
                       for m in measure_separators}
        #  - Sort first by bottom-most staff to which the msep is connected
        #    to get systems
        #  - Sort left-to-right within systems to get final ordering of mseps
        ordered_mseps = sorted(measure_separators,
                               key=lambda m: (max([s.bottom
                                                   for s in msep_staffs[m.id]]),
                                              m.left))
        ordered_msep_nodes = [PrecedenceGraphNode(node=m,
                                                  inlinks=[],
                                                  outlinks=[],
                                                  onset=None,
                                                  duration=0)
                              for m in ordered_mseps]

        # Add root node: like measure separator, but for the first measure.
        # This one is the only one which is initialized with onset,
        # with the value onset=0.
        root_msep = PrecedenceGraphNode(objid=-1,
                                        node=None,
                                        inlinks=[], outlinks=[],
                                        duration=0,
                                        onset=0)

        # Create measure bins. i-th measure ENDS at i-th ordered msep.
        # We assume that every measure has a rightward separator.
        measures = [(None, ordered_mseps[0])] + [(ordered_mseps[i], ordered_mseps[i + 1])
                                                 for i in range(len(ordered_mseps) - 1)]
        measure_nodes = [PrecedenceGraphNode(objid=None,
                                             node=None,
                                             inlinks=[root_msep],
                                             outlinks=[ordered_msep_nodes[0]],
                                             duration=0,  # Durations will be filled in
                                             onset=None)] + \
                        [PrecedenceGraphNode(objid=None,
                                             node=None,
                                             inlinks=[ordered_msep_nodes[i + 1]],
                                             outlinks=[ordered_msep_nodes[i + 2]],
                                             duration=0,  # Durations will be filled in
                                             onset=None)
                         for i in range(len(ordered_msep_nodes) - 2)]
        #: A list of PrecedenceGraph nodes. These don't really need any Node
        #  or id, they are just introducing through their duration the offsets
        #  between measure separators (mseps have legit 0 duration, so that they
        #  do not move the notes in their note descendants).
        #  The list is already ordered.

        # Add measure separator inlinks and outlinks.
        for m_node in measure_nodes:
            r_sep = m_node.outlinks[0]
            r_sep.inlinks.append(m_node)
            if len(m_node.inlinks) > 0:
                l_sep = m_node.inlinks[0]
                l_sep.outlinks.append(m_node)

        # Finally, hang the first measure on the root msep node.
        root_msep.outlinks.append(measure_nodes[0])

        ######################################################################
        # Now, compute measure node durations from time signatures.
        #  This is slightly non-trivial. Normally, a time signature is
        #  (a) at the start of the staff, (b) right before the msep starting
        #  the measure to which it should apply. However, sometimes the msep
        #  comes up (c) at the *start* of the measure to which it should
        #  apply. We IGNORE option (c) for now.
        #
        #  - Collect all time signatures
        time_signatures = [c for c in nodes
                           if c.class_name in self._CONST.TIME_SIGNATURES]

        #  - Assign time signatures to measure separators that *end*
        #    the bars. (Because as opposed to the starting mseps,
        #    the end mseps are (a) always there, (b) usually on the
        #    same staff, (c) if not on the same staff, then they are
        #    an anticipation at the end of a system, and will be repeated
        #    at the beginning of the next one anyway.)
        time_signatures_to_first_measure = {}
        for t in time_signatures:
            s = self.children(t, [InferenceEngineConstants.STAFF])[0]
            # - Find the measure pairs
            for i, (left_msep, right_msep) in enumerate(measures):
                if s not in msep_staffs[right_msep.id]:
                    continue
                if (left_msep is None) or (s not in msep_staffs[left_msep.id]):
                    # Beginning of system, valid already for the current bar.
                    time_signatures_to_first_measure[t.id] = i
                else:
                    # Use i + 1, because the time signature is valid
                    # for the *next* measure.
                    time_signatures_to_first_measure[t.id] = i + 1

        # - Interpret time signatures.
        time_signature_durations = {t.id: self.interpret_time_signature(t)
                                    for t in time_signatures}

        # - Reverse map: for each measure, the time signature valid
        #   for the measure.
        measure_to_time_signature = [None for _ in measures]
        time_signatures_sorted = sorted(time_signatures,
                                        key=lambda x: time_signatures_to_first_measure[x.id])
        for t1, t2 in zip(time_signatures_sorted[:-1], time_signatures_sorted[1:]):
            affected_measures = list(range(time_signatures_to_first_measure[t1.id],
                                           time_signatures_to_first_measure[t2.id]))
            for i in affected_measures:
                # Check for conflicting time signatures previously
                # assigned to this measure.
                if measure_to_time_signature[i] is not None:
                    _competing_time_sig = measure_to_time_signature[i]
                    if (time_signature_durations[t1.id] !=
                            time_signature_durations[_competing_time_sig.id]):
                        raise ValueError('Trying to overwrite time signature to measure'
                                         ' assignment at measure {0}: new time sig'
                                         ' {1} with value {2}, previous time sig {3}'
                                         ' with value {4}'
                                         ''.format(i, t1.id,
                                                   time_signature_durations[t1.id],
                                                   _competing_time_sig.id,
                                                   time_signature_durations[_competing_time_sig.id]))

                measure_to_time_signature[i] = t1

        logging.debug('Checking that every measure has a time signature assigned.')
        for i, (msep1, msep2) in enumerate(measures):
            if measure_to_time_signature[i] is None:
                raise ValueError('Measure without time signature: {0}, between'
                                 'separators {1} and {2}'
                                 ''.format(i, msep1.id, msep2.id))

        # - Apply to each measure node the duration corresponding
        #   to its time signature.
        for i, m in enumerate(measure_nodes):
            _tsig = measure_to_time_signature[i]
            m.duration = time_signature_durations[_tsig.id]

        # ...
        # Now, the "skeleton" of the precedence graph consisting
        # pf measure separator and measure nodes is complete.
        ######################################################################

        ######################################################################
        # Collecting onset-carrying objects (at this point, noteheads
        # and rests; the repeat-measure object that would normally
        # affect duration is handled through measure node durations.
        onset_objs = [c for c in nodes
                      if c.class_name in self._CONST.classes_bearing_duration]

        # Assign onset-carrying objects to measures (their left msep).
        # (This is *not* done by assigning outlinks to measure nodes,
        # we are now just factorizing the space of possible precedence
        # graphs.)
        #  - This is done by iterating over staves.
        staff_to_objs_map = collections.defaultdict(list)
        for c in onset_objs:
            ss = self.children(c, [InferenceEngineConstants.STAFF])
            for s in ss:
                staff_to_objs_map[s.id].append(c)

        #  - Noteheads and rests are all connected to staves,
        #    which immediately gives us for each staff the subset
        #    of eligible symbols for each measure.
        #  - We can just take the vertical projection of each onset
        #    object and find out which measures it overlaps with.
        #    To speed this up, we can just check whether the middles
        #    of objects fall to the region delimited by the measure
        #    separators. Note that sometimes the barlines making up
        #    the measure separator are heavily bent, so it would
        #    be prudent to perhaps use just the intersection of
        #    the given barline and the current staff.

        # Preparation: we need for each valid (staff, msep) combination
        # the bounding box of their intersection, in order to deal with
        # more curved measure separators.

        msep_to_staff_projections = {}
        #: For each measure separator, for each staff it connects to,
        #  the bounding box of the measure separator's intersection with
        #  that staff.
        for msep in measure_separators:
            msep_to_staff_projections[msep.id] = {}
            for s in msep_staffs[msep.id]:
                intersection_bbox = self.msep_staff_overlap_bbox(msep, s)
                msep_to_staff_projections[msep.id][s.id] = intersection_bbox

        staff_and_measure_to_objs_map = collections.defaultdict(
            collections.defaultdict(list))
        #: Per staff (indexed by id) and measure (by order no.), keeps a list of
        #  Nodes from that staff that fall within that measure.

        # Iterate over objects left to right, shift measure if next object
        # over bound of current measure.
        ordered_objs_per_staff = {s_objid: sorted(s_objs, key=lambda x: x.left)
                                  for s_objid, s_objs in list(staff_to_objs_map.items())}
        for s_objid, objs in list(ordered_objs_per_staff.items()):
            # Vertically, we don't care -- the attachment to staff takes
            # care of that, we only need horizontal placement.
            _c_m_idx = 0  # Index of current measure
            _c_msep_right = measure_nodes[_c_m_idx].outlinks[0]
            # Left bound of current measure's right measure separator
            _c_m_right = msep_to_staff_projections[_c_msep_right.id][s_objid][1]
            for _c_o_idx, o in objs:
                # If we are out of bounds, move to next measure
                while o.left > _c_m_right:
                    _c_m_idx += 1
                    if _c_m_idx >= len(measure_nodes):
                        raise ValueError('Object {0}: could not assign to any measure,'
                                         ' ran out of measures!'.format(o.id))
                    _c_msep_right = measure_nodes[_c_m_idx].outlinks[0]
                    _c_m_right = msep_to_staff_projections[_c_msep_right.id][s_objid][1]
                    staff_and_measure_to_objs_map[s_objid][_c_m_right] = []

                staff_and_measure_to_objs_map[s_objid][_c_m_right].append(o)

        # Infer precedence within the measure.
        #  - This is the difficult part.
        #  - First: check the *sum* of durations assigned to the measure
        #    against the time signature. If it fits only once, then it is
        #    a monophonic measure and we can happily read it left to right.
        #  - If the measure is polyphonic, the fun starts!
        #    With K graph nodes, how many prec. graphs are there?
        for s_objid in staff_and_measure_to_objs_map:
            for measure_idx in staff_and_measure_to_objs_map[s_objid]:
                _c_objs = staff_and_measure_to_objs_map[s_objid][measure_idx]
                measure_graph = self.measure_precedence_graph(_c_objs)

                # Connect the measure graph source nodes to their preceding
                # measure separator.
                l_msep_node = measure_nodes[measure_idx].inlinks[0]
                for source_node in measure_graph:
                    l_msep_node.outlinks.append(source_node)
                    source_node.inlinks.append(l_msep_node)

        return [root_msep]

    def measure_precedence_graph(self, nodes: list[Node]):
        """Indexed by staff id and measure number, holds the precedence graph
        for the given measure in the given staff as a list of PrecedenceGraphNode
        objects that correspond to the source nodes of the precedence subgraph.
        These nodes then get connected to their leftwards measure separator node.

        :param nodes: List of Nodes, assumed to be all from one
            measure.

        :returns: A list of PrecedenceGraphNode objects that correspond
            to the source nodes in the precedence graph for the (implied)
            measure. (In monophonic music, the list will have one element.)
            The rest of the measure precedence graph nodes is accessible
            through the sources' outlinks.

        """
        func_name = inspect.currentframe().f_code.co_name
        warnings.warn(
            f"{func_name}() is deprecated.",
            category=DeprecationWarning,
            stacklevel=2
        )
        _is_monody = self.is_measure_monody(nodes)
        if _is_monody:
            source_nodes = self.monody_measure_precedence_graph(nodes)
            return source_nodes

        else:
            raise ValueError('Cannot deal with onsets in polyphonic music yet.')

    def monody_measure_precedence_graph(self, nodes: list[Node]):
        """Infers the precedence graph for a plain monodic measure.
        The resulting structure is very simple: it's just a chain
        of the onset-carrying objects from left to right."""
        func_name = inspect.currentframe().f_code.co_name
        warnings.warn(
            f"{func_name}() is deprecated.",
            category=DeprecationWarning,
            stacklevel=2
        )
        nodes = []
        for c in sorted(nodes, key=lambda x: x.left):
            potential_durations = self.beats(c)

            # In monody, there should only be one duration
            if len(potential_durations) > 1:
                raise ValueError('Object {0}: More than one potential'
                                 ' duration, even though the measure is'
                                 ' determined to be monody.'.format(c.id))
            duration = potential_durations[0]

            node = PrecedenceGraphNode(objid=c.id,
                                       node=c,
                                       inlinks=[],
                                       outlinks=[],
                                       duration=duration,
                                       onset=None)
            nodes.append(node)
        for n1, n2 in zip(nodes[:-1], nodes[1:]):
            n1.outlinks.append(n2)
            n2.inlinks.append(n1)
        source_nodes = [nodes[0]]
        return source_nodes

    def is_measure_monody(self, nodes: list[Node]):
        """Checks whether the given measure is written as simple monody:
        no two of the onset-carrying objects are active simultaneously.

        Assumptions
        -----------

        * Detecting monody without looking at the time signature:
            * All stems in the same direction? --> NOPE: Violin chords in Bach...
            * All stems in horizontally overlapping noteheads in the same direction?
              --> NOPE: Again, violin chords in Bach...
            * Overlapping noteheads share a beam, but not a stem? --> this works,
              but has false negatives: overlapping quarter notes
        """
        func_name = inspect.currentframe().f_code.co_name
        warnings.warn(
            f"{func_name}() is deprecated.",
            category=DeprecationWarning,
            stacklevel=2
        )
        raise NotImplementedError()

    def is_measure_chord_monody(self, nodes: list[Node]):
        """Checks whether the given measure is written as monody potentially
        with chords. That is: same as monody, but once all onset-carrying objects
        that share a stem are merged into an equivalence class."""
        func_name = inspect.currentframe().f_code.co_name
        warnings.warn(
            f"{func_name}() is deprecated.",
            category=DeprecationWarning,
            stacklevel=2
        )
        raise NotImplementedError()

    def msep_staff_overlap_bbox(self, measure_separator, staff):
        """Computes the bounding box for the part of the input
        ``measure_separator`` that actually overlaps the ``staff``.
        This is implemented to deal with mseps that curve a lot,
        so that their left/right bounding box may mistakenly
        exclude some symbols from their preceding/following measure.

        Returns the (T, L, B, R) bounding box.
        """
        func_name = inspect.currentframe().f_code.co_name
        warnings.warn(
            f"{func_name}() is deprecated.",
            category=DeprecationWarning,
            stacklevel=2
        )
        intersection = measure_separator.bounding_box_intersection(staff)
        if intersection is None:
            # Corner case: measure separator is connected to staff,
            # but its bounding box does *not* overlap the bbox
            # of the staff.
            output_bbox = staff.top, measure_separator.left, \
                staff.bottom, measure_separator.right
        else:
            # The key step: instead of using the bounding
            # box intersection, first crop the zeros from
            # msep intersection mask (well, find out how
            # many left and right zeros there are).
            it, il, ib, ir = intersection
            msep_crop = measure_separator.mask[it, il, ib, ir]

            if msep_crop.sum() == 0:
                # Corner case: bounding box does encompass staff,
                # but there is msep foreground pixel in that area
                # (could happen e.g. with mseps only drawn *around*
                # staffs).
                output_bbox = staff.top, measure_separator.left, \
                    staff.bottom, measure_separator.right
            else:
                # The canonical case: measure separator across the staff.
                msep_crop_vproj = msep_crop.sum(axis=0)
                _dl = 0
                _dr = 0
                for i, v in enumerate(msep_crop_vproj):
                    if v != 0:
                        _dl = i
                        break
                for i in range(1, len(msep_crop_vproj)):
                    if msep_crop_vproj[-i] != 0:
                        _dr = i
                        break
                output_bbox = staff.top, measure_separator.left + _dl, \
                    staff.bottom, measure_separator.right - _dr
        return output_bbox

    @staticmethod
    def interpret_numerals(numerals: list[Node]) -> Optional[int]:
        """Returns the given numeral Node as a number, left to right."""
        for n in numerals:
            if n.class_name not in InferenceEngineConstants.NUMERALS:
                raise ValueError(f"Symbol {n.id} is not a numeral!")
        numeral_names = [n.class_name for n in sorted(numerals, key=lambda x: x.left)]
        return ClassNamesConstants.Numerals.interpret(numeral_names)

    def interpret_time_signature(
            self,
            time_signature: Node,
            fractional_vertical_iou_threshold: Optional[float] = None,
    ) -> Fraction:
        """Converts the time signature into the beat count
        (in quarter notes) it assigns to its following measures.

        Dealing with numeric time signatures
        ------------------------------------

        * Is there both a numerator and a denominator?
          (Is the time sig. "fractional"?)
           * If there is a letter_other child, then yes; use the letter_other
             symbol to separate time signature into numerator (top, left) and
             denominator regions.
           * If there is no letter_other child, then check if there is sufficient
             vertical separation between some groups of symbols. Given that it
             is much more likely that there will be the "fractional" structure,
             we say:

               If the minimum vertical IoU between two symbols is more than
               0.8, we consider the time signature non-fractional.



        * If yes: assign numerals to either num. (top), or denom. (bottom)
        * If not: assume the number is no. of beats. (In some scores, the
          base indicator may be attached in form of a note instead of a
          denumerator, like e.g. scores by Janacek, but we ignore this for now.
          In early music, 3 can mean "tripla", which is 3/2.)

        Dealing with non-numeric time signatures
        ----------------------------------------

        * whole-time mark is interpreted as 4/4
        * alla breve mark is interpreted as 4/4

        :param time_signature: Time signature Node.
        :param fractional_vertical_iou_threshold: The threshold can be controlled
            through this parameter. Defaults to 0.8.
        :returns: The denoted duration of a measure in beats.
        """
        members = sorted(
            self.children(
                time_signature,
                class_name_filter=self._CONST.TIME_SIGNATURE_MEMBERS),
            key=lambda x: x.top)

        logging.info('Interpreting time signature {0}'.format(time_signature.id))
        logging.info('... Members {0}'.format([m.class_name for m in members]))

        # Whole-time mark? Alla breve?
        if len(members) == 0:
            raise NotationGraphError('Time signature has no members: {0}'
                                     ''.format(time_signature.id))

        is_whole = False
        is_alla_breve = False
        for m in members:
            if m.class_name == self._CONST.TIME_SIG_COMMON:
                is_whole = True
            if m.class_name == self._CONST.TIME_SIG_CUT_COMMON:
                is_alla_breve = True

        if is_whole or is_alla_breve:
            logging.info('Time signature {0}: whole or alla breve, returning 4.0'
                         ''.format(time_signature.id))
            return Fraction(4)

        # Process numerals
        logging.info('... Found numeric time signature, determining whether'
                     ' it is fractional.')

        # Does the time signature have a fraction-like format?
        is_fraction_like = True
        has_letter_other = (len([m for m in members if m.class_name == self._CONST.LETTER_OTHER]) > 0)
        #  - Does it have a separator slash?
        if has_letter_other:
            logging.info('... Has fraction slash')
            is_fraction_like = True
        #  - Does it have less than 2 members?
        elif len(members) < 2:
            logging.info('... Just one member')
            is_fraction_like = False
        #  - If it has 2 or more members, determine minimal IoU and compare
        #    against FRACTIONAL_VERTICAL_IOU_THRESHOLD. If the minimal IoU
        #    is under the threshold, then consider the numerals far apart
        #    vertically so that they constitute a fraction.
        else:
            logging.info('... Must check for min. vertical overlap')
            vertical_overlaps = []
            for _i_m, m1 in enumerate(members[:-1]):
                for m2 in members[_i_m:]:
                    vertical_overlaps.append(bounding_box_dice_coefficient(m1.bounding_box, m2.bounding_box))
            logging.info('... Vertical overlaps found: {0}'.format(vertical_overlaps))
            if min(vertical_overlaps) < fractional_vertical_iou_threshold:
                is_fraction_like = True
            else:
                is_fraction_like = False

        numerals = sorted(self.children(time_signature, self._CONST.NUMERALS),
                          key=lambda x: x.top)
        if not is_fraction_like:
            logging.info('... Non-fractional numeric time sig.')
            # Read numeral left to right, this is the beat count
            if len(numerals) == 0:
                raise NotationGraphError('Time signature has no numerals, but is'
                                         ' not fraction-like! {0}'
                                         ''.format(time_signature.id))
            beats = OnsetsInferenceEngine.interpret_numerals(numerals)
            logging.info('... Beats: {0}'.format(beats))
            return Fraction(beats)

        else:
            logging.info('... Fractional time sig.')
            # Split into numerator and denominator
            #  - Sort numerals top to bottom
            #  - Find largest gap
            #  - Everything above largest gap is numerator, everything below
            #    is denominator.
            numerals_topdown = sorted(numerals, key=lambda c: (c.top + c.bottom) / 2)
            gaps = [((c2.bottom + c2.top) / 2) - ((c1.bottom + c2.top) / 2)
                    for c1, c2 in zip(numerals_topdown[:-1], numerals_topdown[1:])]
            largest_gap_idx = max(list(range(len(gaps))), key=lambda i: gaps[i]) + 1
            numerator = numerals[:largest_gap_idx]
            denominator = numerals[largest_gap_idx:]
            beat_count = OnsetsInferenceEngine.interpret_numerals(numerator)
            beat_units = OnsetsInferenceEngine.interpret_numerals(denominator)

            beats = Fraction(beat_count * 4, beat_units)
            logging.info('...signature : {0} / {1}, beats: {2}'
                         ''.format(beat_count, beat_units, beats))

            return beats

    def onsets(self, nodes: list[Node]) -> dict[int, Fraction]:
        """Infers the onsets of notes in the given Nodes.

        The onsets are measured in beats.

        :returns: A id --> onset dict for all notehead-type
            Nodes.
        """
        # We first find the precedence graph. (This is the hard
        # part.)
        # The precedence graph is a DAG structure of PrecedenceGraphNode
        # objects. The infer_precedence() method returns a list
        # of the graph's source nodes (of which there is in fact
        # only one, the way it is currently defined).
        self.__graph = NotationGraph(nodes)

        precedence_graph = self._infer_precedence_from_annotations(nodes)
        for node in precedence_graph:
            node.onset = 0

        # Once we have the precedence graph, we need to walk it.
        # It is a DAG, so we simply do a BFS from each source.
        # Whenever a node has more incoming predecessors,
        # we need to wait until they are *all* resolved,
        # and check whether they agree.
        queue = []
        # Note: the queue should be prioritized by *onset*, not number
        # of links from initial node. Leades to trouble with unprocessed
        # ancestors...
        for node in precedence_graph:
            if len(node.inlinks) == 0:
                queue.append(node)

        onsets = {}

        logging.debug('Size of initial queue: {0}'.format(len(queue)))
        logging.debug('Initial queue: {0}'.format([(q.obj.id, q.onset) for q in queue]))

        # We will only be appending to the queue, so the
        # start of the queue is defined simply by the index.
        qstart = 0
        delayed_prec_nodes = dict()
        while (len(queue) - qstart) > 0:
            # if len(queue) > 2 * n_prec_nodes:
            #     logging.warning('Safety valve triggered: queue growing endlessly!')
            #     break

            q = queue[qstart]
            logging.debug('Current @{0}: {1}'.format(qstart, q.obj.id))
            logging.debug('Will add @{0}: {1}'.format(qstart, q.outlinks))

            qstart += 1
            for post_q in q.outlinks:
                if post_q not in queue:
                    queue.append(post_q)

            logging.debug('Queue state: {0}'
                          ''.format([ppq.obj.id for ppq in queue[qstart:]]))

            logging.debug('  {0} has onset: {1}'.format(q.node_id, q.onset))
            if q.onset is not None:
                if q.onset > 0:
                    break
                onsets[q.obj.id] = q.onset
                continue

            prec_qs = q.inlinks
            prec_onsets = [pq.onset for pq in prec_qs]
            # If the node did not yet get all its ancestors processed,
            # send it down the queue.
            if None in prec_onsets:
                logging.debug('Found node with predecessor that has no onset yet; delaying processing: {0}'
                                ''.format(q.obj.id))
                queue.append(q)
                if q in delayed_prec_nodes:
                    logging.warning('This node has already been delayed once! Breaking.')
                    logging.warning('Queue state: {0}'
                                    ''.format([ppq.obj.id for ppq in queue[qstart:]]))
                    break
                else:
                    delayed_prec_nodes[q.obj.id] = q
                    continue

            prec_durations = [pq.duration for pq in prec_qs]

            logging.debug('    Prec_onsets @{0}: {1}'.format(qstart - 1, prec_onsets))
            logging.debug('    Prec_durations @{0}: {1}'.format(qstart - 1, prec_durations))

            onset_proposals = [o + d for o, d in zip(prec_onsets, prec_durations)]
            if min(onset_proposals) != max(onset_proposals):
                if self.strategy.permissive_desynchronization:
                    logging.warning('Object {0}: onsets not synchronized from'
                                    ' predecessors: {1}'.format(q.obj.id,
                                                                onset_proposals))
                    onset = max(onset_proposals)
                else:
                    raise ValueError('Object {0}: onsets not synchronized from'
                                     ' predecessors: {1}'.format(q.obj.id,
                                                                 onset_proposals))
            else:
                onset = onset_proposals[0]

            q.onset = onset
            # Some nodes do not have a Node assigned.
            if q.obj is not None:
                onsets[q.obj.id] = onset
                ### DEBUG -- add this to the Data dict
                q.obj.data['onset_beats'] = onset

        return onsets

    def children(self, c, class_name_filter: Optional[Iterable[str] | str] = None):
        """Retrieve the children of the given Node ``c``
        that have class in ``class_names``."""
        self._check_graph_init()
        return self.__graph.children(c, class_name_filter)

    def __parents(self, c, class_name_filter: Optional[Iterable[str] | str] = None):
        """Retrieve the parents of the given Node ``c``
        that have class in ``class_names``."""
        self._check_graph_init()
        return self.__graph.parents(c, class_name_filter)

    def __warning_or_error(self, message):
        if self.strategy.permissive:
            logging.warning(message)
        else:
            raise ValueError(message)

    def process_ties(self, nodes: list[Node], durations, onsets):
        """Modifies the durations and onsets so that ties are taken into
        account.

        Every left-hand note in a tie gets its duration extended by the
        right-hand note's duration. Every right-hand note's onset is removed.

        :returns: the modified durations and onsets.
        """
        logging.info('Processing ties...')
        g = NotationGraph(nodes=nodes)

        def __get_tie_notes(_tie, graph):
            notes = graph.parents(_tie,
                                  class_filter=[self._CONST.NOTEHEAD_FULL, self._CONST.NOTEHEAD_HALF,
                                                self._CONST.NOTEHEAD_WHOLE])
            if len(notes) == 0:
                raise NotationGraphError('No notes from tie {0}'.format(_tie.id))
            if len(notes) == 1:
                return [notes[0]]
            if len(notes) > 2:
                raise NotationGraphError('More than two notes from tie {0}'.format(_tie.id))
            # Now it has to be 2
            l, r = sorted(notes, key=lambda n: n.left)
            return l, r

        def _is_note_left(c, _tie, graph):
            tie_notes = __get_tie_notes(_tie, graph)
            if len(tie_notes) == 2:
                l, r = tie_notes
                return l.id == c.id
            else:
                return True

        new_onsets = copy.deepcopy(onsets)
        new_durations = copy.deepcopy(durations)
        # Sorting notes right to left. This means: for notes in the middle
        # of two ties, its duration is already updated and it can be removed from
        # the new onsets dict by the time we process the note on the left
        # of the leftward tie (its predecessor).
        for k in sorted(onsets, key=lambda x: onsets[x], reverse=True):
            ties = g.children(k, class_filter=[self._CONST.TIE_CLASS_NAME])
            if len(ties) == 0:
                continue

            if len(ties) > 1:
                # Pick the rightmost tie (we're processing onsets from the right)
                tie = max(ties, key=lambda x: x.left)
            else:
                tie = ties[0]
            n = g[k]
            tie_notes = __get_tie_notes(tie, graph=g)
            if len(tie_notes) != 2:
                continue

            l, r = tie_notes
            if l.id == n.id:
                logging.info('Note {0} is left in tie {1}'
                             ''.format(l.id, tie.id))
                new_durations[l.id] += new_durations[r.id]
                del new_onsets[r.id]

        new_durations = {k: new_durations[k] for k in new_onsets}
        return new_durations, new_onsets
