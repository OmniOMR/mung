import collections
import copy
import logging
import operator
from typing import List, Dict, Tuple, Optional

from mung.constants import InferenceEngineConstants
from mung.graph import group_staffs_into_systems, NotationGraph, NotationGraphError
from mung.node import bounding_box_dice_coefficient, Node

_CONST = InferenceEngineConstants()


class PitchInferenceStrategy(object):
    def __init__(self):
        self.permissive = True


class PitchInferenceEngineState(object):
    """This class represents the state of the MIDI pitch inference
    engine during inference.

    Reading pitch is a stateful operations. One needs to remember
    how stafflines and staffspaces map to pitch codes. This is governed
    by two things:

    * The clef, which governs
    * The accidentals: key signatures and inline accidentals.

    Clef and key signature have unlimited scope which only changes when
    a new key signature is introduced (or the piece ends). The key
    signature affects all pitches in the given step class (F, C, G, ...)
    regardless of octave. Inline accidentals have scope until the next
    measure separator, and they are only valid within their own octave.

    The pitch inference algorithm is run for each staff separately.

    Base pitch representation
    -------------------------

    The base pitch corresponds to the pitch encoded by a notehead
    simply sitting on the given staffline/staffspace, without any
    regard to accidentals (key signature or inline). It is computed
    by *distance from center staffline* of a staff, with positive
    distance corresponding to going *up* and negative for going *down*
    from the center staffline.

    Accidentals representation
    --------------------------

    The accidentals are associated also with each staffline/staffspace,
    as counted from the current center. (This means i.a. that
    the octave periodicity is 7, not 12.)

    There are two kinds of accidentals based on scope: key signature,
    and inline. Inline accidentals are valid only up to the next
    measure_separator, while key signature accidentals are valid
    up until the key signature changes. Key signature accidentals
    also apply across all octaves, while inline accidentals only apply
    on the specific staffline.

    Note that inline accidentals may *cancel* key signature
    accidentals: they override the key signature when given.

    Key accidentals are given **mod 7**.

    Pitch inference procedure
    -------------------------

    Iterate through the relevant objects on a staff, sorted left-to-right
    by left edge.
    """

    def __init__(self):

        self.base_pitch = None  # type: int
        '''The MIDI code corresponding to the middle staffline,
        without modification by key or inline accidentals.'''

        self.base_pitch_step = None  # type: int
        '''The name of the base pitch: C, D, E, etc.'''

        self.base_pitch_octave = None  # type: int
        '''The octave where the pitch resides. C4 = c', the middle C.'''

        self.current_clef = None  # type:Node
        '''Holds the clef Node that is currently valid.'''

        self.current_delta_steps = None  # type: List[int]
        '''Holds for each staffline delta step (i.e. staffline delta mod 7)
        the MIDI pitch codes.'''

        self.current_clef_delta_shift = 0  # type: int
        '''If the clef is in a non-standard position, this number is added
        to the pitch computation delta.'''

        self.key_accidentals = {}  # type: Dict[int,str]
        self.inline_accidentals = {}  # type: Dict[int,str]

    def reset(self):
        self.base_pitch = None
        self.current_clef = None
        self.current_delta_steps = None
        self.key_accidentals = {}
        self.inline_accidentals = {}

    def __str__(self):
        lines = list()
        lines.append('Current pitch inference state:')
        lines.append('\tbase_pitch: {0}'.format(self.base_pitch))
        lines.append('\tbase_pitch_step: {0}'.format(self.base_pitch_step))
        lines.append('\tbase_pitch_octave: {0}'.format(self.base_pitch_octave))
        if self.current_clef is not None:
            lines.append('\t_current_clef: {0}'.format(self.current_clef.id))
        else:
            lines.append('\t_current_clef: None')
        lines.append('\t_current_delta_steps: {0}'.format(self.current_delta_steps))
        lines.append('\t_current_clef_delta_shift: {0}'.format(self.current_clef_delta_shift))
        lines.append('\tkey_accidentals: {0}'.format(self.key_accidentals))
        lines.append('\tinline_accidentals: {0}'.format(self.inline_accidentals))
        return '\n'.join(lines)

    def init_base_pitch(self, clef: Node = None, delta: int = 0):
        """Initializes the base pitch while taking into account
        the displacement of the clef from its initial position."""
        self.init_base_pitch_default_staffline(clef)
        self.current_clef_delta_shift = -1 * delta

    def init_base_pitch_default_staffline(self, clef: Node = None):
        """Based solely on the clef class name and assuming
        default stafflines, initialize the base pitch.
        By default, initializes as though given a gClef."""

        # There should be a mechanism for clefs that are connected
        # directly to a staffline -- in non-standard positions
        # (mostly cClefs, like page 03, but there is no reason
        #  to limit this to cClefs).

        if (clef is None) or (clef.class_name == _CONST.G_CLEF):
            new_base_pitch = 71
            new_delta_steps = [0, 1, 2, 2, 1, 2, 2, 2]
            new_base_pitch_step = 6  # Index into pitch steps.
            new_base_pitch_octave = 4
        elif clef.class_name == _CONST.F_CLEF:
            new_base_pitch = 50
            new_delta_steps = [0, 2, 1, 2, 2, 2, 1, 2]
            new_base_pitch_step = 1
            new_base_pitch_octave = 3
        elif clef.class_name == _CONST.C_CLEF:
            new_base_pitch = 60
            new_delta_steps = [0, 2, 2, 1, 2, 2, 2, 1]
            new_base_pitch_step = 0
            new_base_pitch_octave = 4
        else:
            raise ValueError('Unrecognized clef class_name: {0}'
                             ''.format(clef.class_name))

        # Shift the key and inline accidental deltas
        # according to the change.
        if self.current_clef is not None:
            transposition_delta = _CONST.CLEF_CHANGE_DELTA[self.current_clef.class_name][clef.class_name]
            if transposition_delta != 0:
                new_key_accidentals = {
                    (d + transposition_delta) % 7: v
                    for d, v in list(self.key_accidentals.items())
                }
                new_inline_accidentals = {
                    d + transposition_delta: v
                    for d, v in list(self.inline_accidentals.items())
                }
                self.key_accidentals = new_key_accidentals
                self.inline_accidentals = new_inline_accidentals

        self.base_pitch = new_base_pitch
        self.base_pitch_step = new_base_pitch_step
        self.base_pitch_octave = new_base_pitch_octave
        self.current_clef = clef
        self.current_delta_steps = new_delta_steps

    def set_key(self, number_of_sharps: int = 0, number_of_flats: int = 0):
        """Initialize the staffline delta --> key accidental map.
        Currently works only on standard key signatures, where
        there are no repeating accidentals, no double sharps/flats,
        and the order of accidentals is the standard major/minor system.

        However, we can deal at least with key signatures that combine
        sharps and flats (if not more than 7), as seen e.g. in harp music.

        :param number_of_sharps: How many sharps are there in the key signature?

        :param number_of_flats: How many flats are there in the key signature?
        """
        if number_of_flats + number_of_sharps > 7:
            raise ValueError('Cannot deal with key signature that has'
                             ' more than 7 sharps + flats!')

        if self.base_pitch is None:
            raise ValueError('Cannot initialize key if base pitch is not known.')

        new_key_accidentals = {}

        # The pitches (F, C, G, D, ...) have to be re-cast
        # in terms of deltas, mod 7.
        if (self.current_clef is None) or (self.current_clef.class_name == _CONST.G_CLEF):
            deltas_sharp = [4, 1, 5, 2, 6, 3, 0]
            deltas_flat = [0, 3, 6, 2, 5, 1, 4]
        elif self.current_clef.class_name == _CONST.C_CLEF:
            deltas_sharp = [3, 0, 4, 1, 5, 2, 6]
            deltas_flat = [6, 2, 5, 1, 4, 0, 3]
        elif self.current_clef.class_name == _CONST.F_CLEF:
            deltas_sharp = [2, 6, 3, 0, 4, 1, 5]
            deltas_flat = [5, 1, 4, 0, 3, 6, 2]
        else:
            raise ValueError("Incorrect clef node set as current_clef {0}.".format(self.current_clef))

        for d in deltas_sharp[:number_of_sharps]:
            new_key_accidentals[d] = 'sharp'
        for d in deltas_flat[:number_of_flats]:
            new_key_accidentals[d] = 'flat'

        self.key_accidentals = new_key_accidentals

    def set_inline_accidental(self, delta: int, accidental: Node):
        self.inline_accidentals[delta] = accidental.class_name

    def reset_inline_accidentals(self):
        self.inline_accidentals = {}

    def accidental(self, delta: int) -> int:
        """Returns the modification, in MIDI code, corresponding
        to the staffline given by the delta."""
        pitch_mod = 0

        step_delta = delta % 7
        if step_delta in self.key_accidentals:
            if self.key_accidentals[step_delta] == 'sharp':
                pitch_mod = 1
            elif self.key_accidentals[step_delta] == 'double_sharp':
                pitch_mod = 2
            elif self.key_accidentals[step_delta] == 'flat':
                pitch_mod = -1
            elif self.key_accidentals[step_delta] == 'double_flat':
                pitch_mod = -2

        # Inline accidentals override key accidentals.
        if delta in self.inline_accidentals:
            if self.inline_accidentals[delta] == 'natural':
                logging.info('Natural at delta = {0}'.format(delta))
                pitch_mod = 0
            elif self.inline_accidentals[delta] == 'sharp':
                pitch_mod = 1
            elif self.inline_accidentals[delta] == 'double_sharp':
                pitch_mod = 2
            elif self.inline_accidentals[delta] == 'flat':
                pitch_mod = -1
            elif self.inline_accidentals[delta] == 'double_flat':
                pitch_mod = -2
        return pitch_mod

    def pitch(self, delta: int) -> int:
        """Given a staffline delta, returns the current MIDI pitch code.

        (This method is the main interface of the PitchInferenceEngineState.)

        :delta: Distance in stafflines + staffspaces from the middle staffline.
            Negative delta means distance *below*, positive delta is *above*.

        :returns: The MIDI pitch code for the given delta.
        """
        delta += self.current_clef_delta_shift

        # Split this into octave and step components.
        delta_step = delta % 7
        delta_octave = delta // 7

        # From the base pitch and clef:
        step_pitch = self.base_pitch \
                     + sum(self.current_delta_steps[:delta_step + 1]) \
                     + (delta_octave * 12)
        accidental_pitch = self.accidental(delta)

        pitch = step_pitch + accidental_pitch

        if self.current_clef_delta_shift != 0:
            logging.info('PitchInferenceState: Applied clef-based delta {0},'
                         ' resulting delta was {1}, pitch {2}'
                         ''.format(self.current_clef_delta_shift,
                                   delta, pitch))

        return pitch

    def pitch_name(self, delta: int) -> Tuple[str, int]:
        """Given a staffline delta, returns the name of the corrensponding pitch."""
        delta += self.current_clef_delta_shift

        output_step = _CONST.PITCH_STEPS[(self.base_pitch_step + delta) % 7]
        output_octave = self.base_pitch_octave + ((delta + self.base_pitch_step) // 7)

        output_mod = ''
        accidental = self.accidental(delta)
        if accidental == 1:
            output_mod = _CONST.ACCIDENTAL_CODES['sharp']
        elif accidental == 2:
            output_mod = _CONST.ACCIDENTAL_CODES['double_sharp']
        elif accidental == -1:
            output_mod = _CONST.ACCIDENTAL_CODES['flat']
        elif accidental == 2:
            output_mod = _CONST.ACCIDENTAL_CODES['double_flat']

        return output_step + output_mod, output_octave


class PitchInferenceEngine(object):
    """The Pitch Inference Engine extracts MIDI from the notation
    graph. To get the MIDI, there are two streams of information
    that need to be combined: pitches and onsets, where the onsets
    are necessary both for ON and OFF events.

    Pitch inference is done through the ``infer_pitches()`` method.

    Onsets inference is done in two stages. First, the durations
    of individual notes (and rests) are computed, then precedence
    relationships are found and based on the precedence graph
    and durations, onset times are computed.

    Onset inference
    ---------------

    Onsets are computed separately by measure, which enables time
    signature constraint checking.

    (This can be implemented in the precedence graph structure,
    by (a) not allowing precedence edges to cross measure separators,
    (b) chaining measure separators, or it can be implemented
    directly in code. The first option is way more elegant.)

    Creating the precedence graph
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    * Get measure separators.
    * Chain measure separators in precedence relationships.
    * Group Nodes by bins between measure separators.
    * For each staff participating in the current measure
      (as defined by the relevant measure separator outlinks):

        * Infer precedence between the participating notes & rests,
        * Attach the sources of the resulting DAG to the leftward
          measure_separator (if there is none, just leave them
          as sources).

    Invariants
    ^^^^^^^^^^

    * There is exactly one measure separator starting each measure,
      except for the first measure, which has none. That implies:
      when there are multiple disconnected barlines marking the interface
      of the same two measures within a system, they are joined under
      a single measure_separator anyway.
    * Staff groupings are correct, and systems are read top-down.

    """

    def __init__(self, strategy=PitchInferenceStrategy()):
        # Static temp data from which the pitches are inferred
        self.id_to_node_mapping = {}

        self.strategy = strategy

        self.staves = None

        self.clefs = None
        self.clef_to_staff_map = None
        self.staff_to_clef_map = None

        self.key_signatures = None
        self.key_to_staff_map = None
        self.staff_to_key_map = None

        self.measure_separators = None
        self.staff_to_msep_map = None

        self.noteheads = None
        self.staff_to_noteheads_map = None

        # Dynamic temp data: things that change as the pitches are inferred.
        self.pitch_state = PitchInferenceEngineState()

        # Results
        self.pitches = None
        self.pitches_per_staff = None

        self.pitch_names = None
        self.pitch_names_per_staff = None

        # self.durations_beats = None
        # self.durations_beats_per_staff = None

    def reset(self):
        self.__init__()

    def infer_pitches(self, nodes: List[Node], with_names=False):
        """The main workhorse for pitch inference.
        Gets a list of Nodes and for each notehead-type
        symbol, outputs a MIDI code corresponding to the pitch
        encoded by that notehead.

        Notehead
        --------

        * Check for ties; if there is an incoming tie, apply
          the last pitch. (This is necessary because of ties
          that go across barlines and maintain inline accidentals.)
        * Determine its staffline delta from the middle staffline.
        * Check for inline accidentals, apply them to inference state.
        * Query pitch state with this staffline delta.

        Ties are problematic, because they may reach across
        staff breaks. This can only be resolved after all staves
        are resolved and assigned to systems, because until then,
        it is not clear which staff corresponds to which in the next
        system. Theoretically, this is near-impossible to resolve,
        because staves may not continue on the next system (e.g.,
        instruments that do not play for some time in orchestral scores),
        so simple staff counting is not foolproof. Some other matching
        mechanism has to be found, e.g. matching outgoing and incoming
        ties on the end and beginning of adjacent systems.

        Measure separator
        -----------------

        * Reset all inline accidentals to empty.

        Clef change
        -----------

        * Change base pitch
        * Recompute the key and inline signature delta indexes

        Key change
        ----------

        * Recompute key deltas

        :param with_names: If set, will return also a dict of
            id --> pitch names (e.g., {123: 'F#3'}).

        :returns: A dict of ``id`` to MIDI pitch code, with
            an entry for each (pitched) notehead. If ``with_names``
            is given, returns a tuple with the id --> MIDI
            and id --> pitch name dicts.

        """
        self.id_to_node_mapping = {c.id: c for c in nodes}

        # Initialize pitch temp data.
        self._collect_symbols_for_pitch_inference(nodes)

        # Staff processing: this is where the inference actually
        # happens.
        self.pitches_per_staff = {}
        self.pitches = {}
        self.pitch_names_per_staff = {}
        self.pitch_names = {}
        # self.durations_beats = {}
        # self.durations_beats_per_staff = {}

        for staff in self.staves:
            self.process_staff(staff)
            self.pitches.update(self.pitches_per_staff[staff.id])

        if with_names:
            return copy.deepcopy(self.pitches), copy.deepcopy(self.pitch_names)
        else:
            return copy.deepcopy(self.pitches)

    def process_staff(self, staff):

        self.pitches_per_staff[staff.id] = {}
        self.pitch_names_per_staff[staff.id] = {}

        # self.durations_beats_per_staff[staff.id] = {}

        self.pitch_state.reset()
        self.pitch_state.init_base_pitch()

        queue = sorted(
            self.staff_to_clef_map[staff.id]
            + self.staff_to_key_map[staff.id]
            + self.staff_to_msep_map[staff.id]
            + self.staff_to_noteheads_map[staff.id],
            key=lambda x: x.left)

        for q in queue:
            logging.info('process_staff(): processing object {0}-{1}'
                         ''.format(q.class_name, q.id))
            if q.class_name in _CONST.CLEF_CLASS_NAMES:
                self.process_clef(q)
            elif q.class_name in _CONST.KEY_SIGNATURE:
                self.process_key_signature(q)
            elif q.class_name in _CONST.MEASURE_SEPARATOR_CLASS_NAMES:
                self.process_measure_separator(q)
            elif q.class_name in _CONST.NOTEHEAD_CLASS_NAMES:
                p, pn = self.process_notehead(q, with_name=True)
                self.pitches[q.id] = p
                self.pitches_per_staff[staff.id][q.id] = p
                self.pitch_names[q.id] = pn
                self.pitch_names_per_staff[staff.id][q.id] = pn

                ### DEBUG
                if q.id in [131, 83, 89, 94]:
                    logging.info('PitchInferenceEngine: Processing notehead {0}'
                                 ''.format(q.id))
                    logging.info('{0}'.format(self.pitch_state))

                # b = self.beats(q)
                # self.durations_beats[q.id] = b
                # self.durations_beats_per_staff[staff.id][q.id] = b

        return self.pitches_per_staff[staff.id]

    def process_notehead(self, notehead, with_name=False):
        """This is the main workhorse of the pitch inference engine.

        :param notehead: The notehead-class Node for which we
            want to infer pitch.

        :param with_name: If set, will return not only the MIDI pitch
            code, but the name of the encoded note (e.g., F#3) as well.
        """
        # Processing ties
        # ---------------
        ties = self.__children(notehead, [_CONST.TIE_CLASS_NAME])
        for t in ties:
            tied_noteheads = self.__parents(t, _CONST.NOTEHEAD_CLASS_NAMES)

            # Corner cases: mistakes and staff breaks
            if len(tied_noteheads) > 2:
                raise ValueError('Tie {0}: joining together more than 2'
                                 ' noteheads!'.format(t.id))
            if len(tied_noteheads) < 2:
                logging.warning('Tie {0}: only one notehead. Staff break?'
                                ''.format(t.id))
                break

            left_tied_notehead = min(tied_noteheads, key=lambda x: x.left)
            if left_tied_notehead.id != notehead.id:
                try:
                    p = self.pitches[left_tied_notehead.id]
                    if with_name:
                        pn = self.pitch_names[left_tied_notehead.id]
                        return p, pn
                    else:
                        return p

                except KeyError:
                    raise KeyError('Processing tied notehead {0}:'
                                   ' preceding notehead {1} has no pitch!'
                                   ''.format(notehead.id, left_tied_notehead.id))

            # If the condition doesn't hold, then this is the leftward
            # note in the tie, and its pitch needs to be determined.

        # Obtain notehead delta
        # ---------------------
        delta = self.staffline_delta(notehead)

        # ### DEBUG
        # if notehead.id == 200:
        #     logging.info('Notehead {0}: delta {1}'.format(notehead.unique_id, delta))
        #     logging.info('\tdelta_step: {0}'.format(delta % 7))
        #     logging.info('\tdelta_step pitch sum: {0}'
        #                  ''.format(sum(self.pitch_state._current_delta_steps[:(delta % 7)+1])))

        # Processing inline accidentals
        # -----------------------------
        accidentals = self.__children(notehead, _CONST.ACCIDENTAL_CLASS_NAMES)

        if len(accidentals) > 0:

            # Sanity checks
            if len(accidentals) > 2:
                self.__warning_or_error('More than two accidentals attached to notehead'
                                        ' {0}'.format(notehead.id))
            elif len(accidentals) == 2:
                naturals = [a for a in accidentals if a.class_name == 'natural']
                non_naturals = [a for a in accidentals if a.class_name != 'natural']
                if len(naturals) == 0:
                    self.__warning_or_error('More than one non-natural accidental'
                                            ' attached to notehead {0}'
                                            ''.format(notehead.id))

                if len(non_naturals) == 0:
                    self.__warning_or_error('Two naturals attached to one notehead {0}'
                                            ''.format(notehead.id))
                    self.pitch_state.set_inline_accidental(delta, naturals[0])
                else:
                    self.pitch_state.set_inline_accidental(delta, non_naturals[0])

            elif len(accidentals) == 1:
                self.pitch_state.set_inline_accidental(delta, accidentals[0])

        # Get the actual pitch
        # --------------------
        p = self.pitch_state.pitch(delta)

        ### DEBUG
        if notehead.id in [131, 83, 89, 94]:
            logging.info('PitchInferenceEngine: results of pitch processing'
                         ' for notehead {0}'.format(notehead.id))
            logging.info('\tties: {0}'.format(ties))
            logging.info('\taccidentals: {0}'.format(accidentals))
            logging.info('\tdelta: {0}'.format(delta))
            logging.info('\tpitch: {0}'.format(p))

        if with_name is True:
            pn = self.pitch_state.pitch_name(delta)
            return p, pn
        else:
            return p

    def staffline_delta(self, notehead: Node):
        """Computes the staffline delta (distance from middle stafflines,
        measured in stafflines and staffspaces) for the given notehead
        (or any other symbol connected to a staffline/staffspace).
        Accounts for leger lines.
        """
        current_staff = self.__children(notehead, ['staff'])[0]
        staffline_objects = self.__children(notehead,
                                            _CONST.STAFFLINE_CLASS_NAMES)

        # Leger lines
        # ------------
        if len(staffline_objects) == 0:

            # Processing leger lines:
            #  - count leger lines
            lls = self.__children(notehead, _CONST.LEGER_LINE)
            n_lls = len(lls)
            if n_lls == 0:
                raise ValueError('Notehead with no staffline or staffspace,'
                                 ' but also no leger lines: {0}'
                                 ''.format(notehead.id))

            #  Determine: is notehead above or below staff?
            is_above_staff = (notehead.top < current_staff.top)

            #  Determine: is notehead on/next to (closest) leger line?
            #    This needs to be done *after* we know whether the notehead
            #    is above/below staff: if the notehead is e.g. above,
            #    then it would be weird to find out it is in the
            #    mini-staffspace *below* the closest leger line,
            #    signalling a mistake in the data.
            closest_ll = min(lls, key=lambda x: (x.top - notehead.top) ** 2 + (x.bottom - notehead.bottom) ** 2)

            # Determining whether the notehead is on a leger
            # line or in the adjacent temp staffspace.
            # This uses a magic number, ON_STAFFLINE_RATIO_THRESHOLD.
            on_leger_line = True

            ### DEBUG!!!
            dtop, dbottom = 1, 1

            # Weird situation with notehead vertically *inside* bbox
            # of leger line (could happen with slanted LLs and very small
            # noteheads).
            if closest_ll.top <= notehead.top <= notehead.bottom <= closest_ll.bottom:
                on_leger_line = True

            # No vertical overlap between LL and notehead
            elif closest_ll.top > notehead.bottom:
                on_leger_line = False
            elif notehead.top > closest_ll.bottom:
                on_leger_line = False

            # Complicated situations: overlap
            else:
                # Notehead "around" leger line.
                if notehead.top < closest_ll.top <= closest_ll.bottom < notehead.bottom:
                    dtop = closest_ll.top - notehead.top
                    dbottom = notehead.bottom - closest_ll.bottom

                    if min(dtop, dbottom) / max(dtop, dbottom) \
                            < _CONST.ON_STAFFLINE_RATIO_THRESHOLD:
                        on_leger_line = False

                        # Check orientation congruent with rel. to staff.
                        # If it is wrong (e.g., notehead mostly under LL
                        # but above staffline, and looks like off-LL),
                        # change back to on-LL.
                        if (dtop > dbottom) and not is_above_staff:
                            on_leger_line = True
                            logging.debug('Notehead in LL space with wrong orientation '
                                          'w.r.t. staff:'
                                          ' {0}'.format(notehead.id))
                        if (dbottom > dtop) and is_above_staff:
                            on_leger_line = True
                            logging.debug('Notehead in LL space with wrong orientation '
                                          'w.r.t. staff:'
                                          ' {0}'.format(notehead.id))

                # Notehead interlaced with leger line, notehead on top
                elif notehead.top < closest_ll.top <= notehead.bottom <= closest_ll.bottom:
                    # dtop = closest_ll.top - notehead.top
                    # dbottom = max(notehead.bottom - closest_ll.top, 1)
                    # if float(dbottom) / float(dtop) \
                    #         < _CONST.ON_STAFFLINE_RATIO_TRHESHOLD:
                    on_leger_line = False

                # Notehead interlaced with leger line, leger line on top
                elif closest_ll.top <= notehead.top <= closest_ll.bottom < notehead.bottom:
                    # dtop = max(closest_ll.bottom - notehead.top, 1)
                    # dbottom = notehead.bottom - closest_ll.bottom
                    # if float(dtop) / float(dbottom) \
                    #         < _CONST.ON_STAFFLINE_RATIO_TRHESHOLD:
                    on_leger_line = False

                else:
                    raise ValueError('Strange notehead {0} vs. leger line {1}'
                                     ' situation: bbox notehead {2}, LL {3}'
                                     ''.format(notehead.id, closest_ll.id,
                                               notehead.bounding_box,
                                               closest_ll.bounding_box))

            delta = (2 * n_lls - 1) + 5
            if not on_leger_line:
                delta += 1

            if not is_above_staff:
                delta *= -1

            return delta

        elif len(staffline_objects) == 1:
            current_staffline = staffline_objects[0]

            # Count how far from the current staffline we are.
            #  - Collect staffline objects from the current staff
            all_staffline_objects = self.__children(current_staff,
                                                    _CONST.STAFFLINE_CLASS_NAMES)

            #  - Determine their ordering, top to bottom
            sorted_staffline_objects = sorted(all_staffline_objects,
                                              key=lambda x: (x.top + x.bottom) / 2.)

            delta = None
            for i, s in enumerate(sorted_staffline_objects):
                if s.id == current_staffline.id:
                    delta = 5 - i

            if delta is None:
                raise ValueError('Notehead {0} attached to staffline {1},'
                                 ' which is however not a child of'
                                 ' the notehead\'s staff {2}!'
                                 ''.format(notehead.id, current_staffline.id,
                                           current_staff.id))

            return delta

        else:
            raise ValueError('Notehead {0} attached to more than one'
                             ' staffline/staffspace!'.format(notehead.id))

    def process_measure_separator(self, measure_separator):
        self.pitch_state.reset_inline_accidentals()

    def process_key_signature(self, key_signature):
        sharps = self.__children(key_signature, ['sharp'])
        flats = self.__children(key_signature, ['flat'])
        self.pitch_state.set_key(len(sharps), len(flats))

    def process_clef(self, clef):
        # Check for staffline children
        stafflines = self.__children(clef, class_names=_CONST.STAFFLINE_CLASS_NAMES)
        if len(stafflines) == 0:
            logging.info('Clef not connected to any staffline, assuming default'
                         ' position: {0}'.format(clef.id))
            self.pitch_state.init_base_pitch(clef=clef)
        else:
            # Compute clef staffline delta from middle staffline.
            delta = self.staffline_delta(clef)
            logging.info('Clef {0}: computed staffline delta {1}'
                         ''.format(clef.id, delta))
            self.pitch_state.init_base_pitch(clef=clef, delta=delta)

    def _collect_symbols_for_pitch_inference(self, nodes: List[Node],
                                             ignore_nonstaff=True):
        """
        Extract all symbols from the document relevant for pitch
        inference and index them in the Engine's temp data structures.

        Collects:
            - Staffs
            - Clefs
            - Key Signatures
            - Measure Separators
            - Noteheads
        """
        graph = NotationGraph(nodes)

        # Collect staves.
        self.staves = graph.filter_vertices(InferenceEngineConstants.STAFF)
        logging.info('We have {0} staves.'.format(len(self.staves)))

        # Collect clefs and key signatures per staff.
        self.clefs = graph.filter_vertices(_CONST.CLEF_CLASS_NAMES)
        if ignore_nonstaff:
            self.clefs = [c for c in self.clefs if graph.has_children(c, [InferenceEngineConstants.STAFF])]
        logging.info(f"We have {len(self.clefs)} clefs.")

        self.key_signatures = graph.filter_vertices(InferenceEngineConstants.KEY_SIGNATURE)
        if ignore_nonstaff:
            self.key_signatures = [c for c in self.key_signatures
                                   if graph.has_children(c, [InferenceEngineConstants.STAFF])]
        logging.info(f"We have {len(self.key_signatures)} key signatures.")

        self.clef_to_staff_map = {}
        # There may be more than one clef per staff.
        self.staff_to_clef_map = collections.defaultdict(list)
        for c in self.clefs:
            # Assuming one staff per clef
            children = graph.children(c, [InferenceEngineConstants.STAFF])
            if len(children) > 0:
                s = children[0]
                self.clef_to_staff_map[c.id] = s
                self.staff_to_clef_map[s.id].append(c)
            else:
                logging.warning('Clef {0} has no staff attached! Will not be'
                                ' part of pitch inference.'.format(c.id))
            continue

        self.key_to_staff_map = {}
        # There may be more than one key signature per staff.
        self.staff_to_key_map = collections.defaultdict(list)
        for k in self.key_signatures:
            children = graph.children(k, [InferenceEngineConstants.STAFF])
            if len(children) > 0:
                s = children[0]
                self.key_to_staff_map[k.id] = s
                self.staff_to_key_map[s.id].append(k)
            else:
                logging.warning('Key signature {0} has no staff attached! Will not be'
                                ' part of pitch inference.'.format(k.id))
                continue

        # Collect measure separators.
        self.measure_separators = graph.filter_vertices(InferenceEngineConstants.MEASURE_SEPARATOR)
        if ignore_nonstaff:
            self.measure_separators = [c for c in self.measure_separators
                                       if graph.has_children(c, [InferenceEngineConstants.STAFF])]
        logging.info(f"We have {len(self.measure_separators)} measure separators.")

        self.staff_to_msep_map = collections.defaultdict(list)
        for m in self.measure_separators:
            _m_staves = self.__children(m, [InferenceEngineConstants.STAFF])
            # (Measure separators might belong to multiple staves.)
            for s in _m_staves:
                self.staff_to_msep_map[s.id].append(m)
                # Collect accidentals per notehead.

        # Collect noteheads.
        self.noteheads = [c for c in nodes
                          if c.class_name in _CONST.NOTEHEAD_CLASS_NAMES]
        if ignore_nonstaff:
            self.noteheads = [c for c in self.noteheads
                              if graph.has_children(c, [InferenceEngineConstants.STAFF])]
        logging.info(f"We have {len(self.noteheads)} noteheads.")

        self.staff_to_noteheads_map = collections.defaultdict(list)
        for n in self.noteheads:
            s = self.__children(n, [InferenceEngineConstants.STAFF])[0]
            self.staff_to_noteheads_map[s.id].append(n)

    def __children(self, c: Node, class_names: List[str]) -> List[Node]:
        """
        Retrieve the children of the given Node ``c`` that have class in ``class_names``.
        """
        return [self.id_to_node_mapping[o] for o in c.outlinks
                if self.id_to_node_mapping[o].class_name in class_names]

    def __has_children(self, c: Node, class_names: List[str]) -> List[Node]:
        """
        Returns true if the given node has a least one child that has the class name in ``class_names``.
        """
        return [self.id_to_node_mapping[o] for o in c.outlinks
                if self.id_to_node_mapping[o].class_name in class_names]

    def __parents(self, c: Node, class_names: List[str]) -> List[Node]:
        """
        Retrieve the parents of the given Node ``c`` that have class in ``class_names``.
        """
        return [self.id_to_node_mapping[i] for i in c.inlinks
                if self.id_to_node_mapping[i].class_name in class_names]

    def __warning_or_error(self, message):
        if self.strategy.permissive:
            logging.warning(message)
        else:
            raise ValueError(message)
