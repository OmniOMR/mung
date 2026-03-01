from fractions import Fraction
from typing import Optional
from pathlib import Path
from typing import Self, Any
from collections import defaultdict, Counter
from itertools import chain

from mung import NotationGraph, Node
from mung.constants import ClassNameConstants as C, InferenceEngineConstants as I
from mung.subevents_from_nodes import subevents_from_list_of_symbols
from mung.interpret import BasicTimeSignatureInterpreter, TimeSigStruct
from mung.graph import (
    UnionFind,
    group_by_system_measure_and_system,
    infer_stem_orientation,
    infer_vertical_object_placement_relative_to_notes,
    infer_horizontal_object_placement_relative_to_notes
)
from ..load_engine import LoadEngine
from ....preprocessing.instruments import (
    graph_to_instruments,
    get_instrument_groups_from_systems
)
from ...graph import *
from .utils import (
    voice,
    duration_beats_w_m,
    pitch,
    onset_beats,
    duration_beats,
    tuple_time_modification,
    get_durable_pitch
)
from ....logger import logger


MEASURE_INDEX_START = 1


class MuNG_LoadEngine(LoadEngine):
    def __init__(self) -> None:
        self._stem_orientation_cache: dict[Node, StemValueToken] = dict()
        self._btsi = BasicTimeSignatureInterpreter()

    
    # region TIME SIGNATURE
    def _get_time_sig_symbol_token(self, time_sig: TimeSigStruct) -> TimeSymbolToken:
        if time_sig.is_common:
            return TimeSymbolToken.COMMON
        elif time_sig.is_common_cut:
            return TimeSymbolToken.CUT
        elif time_sig.is_single_number:
            return TimeSymbolToken.SINGLE_NUMBER
        return TimeSymbolToken.NORMAL

    def _get_separator_token(self, time_sig: TimeSigStruct) -> TimeSeparatorToken:
        if time_sig.has_slash:
            return TimeSeparatorToken.HORIZONTAL
        else:
            return TimeSeparatorToken.NONE

    def _construct_time_signature(
            self,
            mung_time_sig: Node, onset: Fraction, graph: NotationGraph
        ) -> Optional[TimeSignature]:
        tss = self._btsi.interpret_time_signature(mung_time_sig, graph)
        
        if tss is None:
            return None
        
        return TimeSignature(
            fractional_onset_=onset,
            numerator=tss.numerator,
            denominator=tss.denominator,
            symbol_type=self._get_time_sig_symbol_token(tss),
            separator_type=self._get_separator_token(tss)
        )
    # endregion

    def _construct_durable_beam(self, mung_beam: Node, subevents: list[Subevent]) -> DurableBeam:
        assert len(subevents) > 0, f"No subevents for {mung_beam}"
        subevents.sort(key=lambda s: s.global_fractional_onset)
        if len(subevents) == 1:
            return DurableBeam(
                start=subevents[0]
            )
        elif len(subevents) == 2:
            return DurableBeam(
                start=subevents[0],
                stop=subevents[1]
            )
        else:
            return DurableBeam(
                start=subevents[0],
                continue_=subevents[1:-1],
                stop=subevents[-1]
            )
    
    def _construct_tuplet(self, mung_tuplet: Node, subevents: list[Subevent], graph: NotationGraph) -> Tuplet:
        assert len(subevents) > 0, f"No subevents for {mung_tuplet}"
        subevents.sort(key=lambda s: s.global_fractional_onset)
        
        def _has_number(mung_tuplet: Node, graph: NotationGraph) -> bool:
            return graph.has_children(mung_tuplet, class_filter=I.NUMERALS)
        
        def _has_bracket(mung_tuplet: Node, graph: NotationGraph) -> bool:
            return graph.has_children(mung_tuplet, class_filter=C.Tuplets.TUPLET_BRACKET)
            
        if len(subevents) == 1:
            start = subevents[0]
            stop, continue_ = None, None
        else:
            start = subevents[0]
            stop = subevents[-1]
            continue_ = subevents[1:-1]
            if len(continue_) == 0:
                continue_ = None
        
        return Tuplet(
            start=start,
            stop=stop,
            continue_=continue_,
            time_modification=self._construct_time_modification(mung_tuplet),
            bracket=YesNoToken.from_bool(_has_bracket(mung_tuplet, graph)),
            show_number=ShowTupleToken.ACTUAL if _has_number(mung_tuplet, graph) else ShowTupleToken.NONE,
        )
    
    def _construct_time_modification(self, mung_tuplet: Node) -> TimeModification:
            return TimeModification.from_fraction(
                tuple_time_modification(mung_tuplet)
            )

    def _construct_slur(self, mung_slur: Node, subevents: list[Subevent], graph: NotationGraph) -> Slur:
        """
        Slurs is connected to the earliest and the latest two subevents.
        If there are multiple subevents at the start or the end,
        single start and stop subevents are chosen based on a computed
        `PlacementToken`.

        Creates slurs with only start or only stop,
        even though MusicXML does not support them.
        """        
        assert len(subevents) > 0, f"No subevents for {mung_slur}"
        subevents.sort(key=lambda s: s.global_fractional_onset)

        placement = AboveBelowToken.from_int(infer_vertical_object_placement_relative_to_notes(mung_slur, graph))
        if placement == AboveBelowToken.ABOVE:
            # find the topmost subevent: lowest voice id and lowest staff id
            start = min(subevents, key=lambda s: (s.global_fractional_onset, s.voice.id, min(x.id for x in s.staffs)))
            stop = min(subevents, key=lambda s: (-s.global_fractional_onset, s.voice.id, min(x.id for x in s.staffs)))
        else:
            # find the bottom most subevent: highest voice id and highest staff id
            start = min(subevents, key=lambda s: (s.global_fractional_onset, -s.voice.id, max(x.id for x in s.staffs)))
            stop = min(subevents, key=lambda s: (-s.global_fractional_onset, -s.voice.id, max(x.id for x in s.staffs)))
        
        unique_onsets = set(x.global_fractional_onset for x in subevents)

        # only start (or stop)
        if len(unique_onsets) == 1:
            # the only durable connected to the slur should be start or stop
            hor = infer_horizontal_object_placement_relative_to_notes(mung_slur, graph)
            # the slur is on the right from the durable
            if hor < 0:
                return Slur(
                    start=start,
                    stop=None,
                    placement=placement,
                )
            # the slur is on the left from the durable
            else:
                return Slur(
                    start=None,
                    stop=start,
                    placement=placement
                )
        
        # both start and stop were found
        else:
            continue_ = [x for x in subevents if (x != start and x != stop)]
            if len(continue_) == 0:
                continue_ = None
            
            return Slur(
                start=start,
                continue_=continue_,
                stop=stop,
                placement=placement,
            )

    def _try_construct_tie(self, mung_tie: Node, durables: list[Durable], graph: NotationGraph) -> Optional[Slur | Tie]:
        """
        A slur might be misclassified as a tie, in which case,
        it might happen that the connected noteheads differ in pitch.
        A tie constructed for these noteheads would be invalid.

        The method first tries to construct a tie and if it fails,
        it creates a slur.
        """
        unique_onsets = set(d.global_fractional_onset for d in durables)
        unique_pitches = set(d.pitch for d in durables if isinstance(d, Note))
        
        def _slur_from_tie_input(mung_tie: Node, durables: list[Durable], graph: NotationGraph) -> Optional[Slur | Tie]:
            return self._construct_slur(mung_tie, list(set(d.subevent for d in durables)), graph)
        
        # invalid tie specification, outputting as slur
        if len(unique_onsets) > 2 or len(unique_pitches) > 1:
            if len(unique_onsets) > 2:
                logger.warning(f"Too many onsets for tie, {unique_onsets}, has to be at most 2, processing as {Slur.__name__}")
            if len(unique_pitches) > 1:
                logger.warning(f"Too many pitches for tie, {unique_onsets}, has to be at most 1, processing as {Slur.__name__}")
            
            return _slur_from_tie_input(mung_tie, durables, graph)
        
        placement = AboveBelowToken.from_int(infer_horizontal_object_placement_relative_to_notes(mung_tie, graph))
        
        if placement == AboveBelowToken.ABOVE:
            # minimizing:
            #  - onset (minimal onset wanted)
            #  - note/rest (minimizing for notes (0))
            #  - -pitch (minimizing midi pitch)
            start = min(durables, key=lambda d: (d.global_fractional_onset, not isinstance(d, Note), -get_durable_pitch(d)))
        else:
            # same as above but lowest pitch first
            start = min(durables, key=lambda d: (d.global_fractional_onset, not isinstance(d, Note), get_durable_pitch(d)))


        if len(unique_onsets) == 1:
            return Tie(
                start=start,
                placement=placement
            )
        
        # try match start with stop based on pitch
        possible_stops = sorted([
            d for d in durables 
            # find durables that start at the maximal onset and immediately after the start durable
            if (d.in_measure_fractional_onset == max(unique_onsets)
                and start.in_measure_fractional_end_onset == d.in_measure_fractional_onset
                # if durable is Note, check that pitches are the same (if start is Note)
                and (not isinstance(d, Note) or (isinstance(start, Note) and d.pitch == start.pitch))
            )
            # prefer notes over rests
        ], key=lambda d: not isinstance(d, Note))

        if len(possible_stops) == 0:
            logger.warning(f"Unable to find same pitch notes for {mung_tie}, processing as {Slur.__name__}")
            return _slur_from_tie_input(mung_tie, durables, graph)
        
        return Tie(
            start=start,
            stop=possible_stops[0],
            placement=placement,
        )

    def _construct_wedge(
            self,
            mung_hairpin: Node, subevents: list[Subevent], graph: NotationGraph
    ) -> Wedge:
        assert len(subevents) > 0
        subevents.sort(key=lambda s: s.global_fractional_onset)

        placement = AboveBelowToken.from_int(
            infer_vertical_object_placement_relative_to_notes(mung_hairpin, graph)
        )

        def _from_mung_class_name(class_name: str) -> "WedgeType":
            match class_name:
                case C.Dynamics.DYNAMIC_CRESCENDO_HAIRPIN:
                    return WedgeType.CRESCENDO
                case C.Dynamics.DYNAMIC_DIMINUENDO_HAIRPIN:
                    return WedgeType.DIMINUENDO
                case _:
                    raise ValueError(f"Unknown {WedgeType.__name__}: '{class_name}'")

        staff = min((s for s in subevents[0].staffs), key=lambda s: s.id)
        w = Wedge(
            start=subevents[0],
            stop=subevents[-1],
            continue_=subevents[1:-1] if len(subevents) > 2 else None,
            type_=_from_mung_class_name(mung_hairpin.class_name),
            placement=placement
        )

        staff.other_symbols = staff.other_symbols + [w]
        return w

    def _construct_staffs(
            self,
            instrument_staffs: list[list[list[Node]]]
        ) -> dict[Node, Staff]:
        """
        Creates `Staff` scene objects
        and returns a mapping from MuNG staff nodes to `Staff`s.
        """
        mung_staff_to_staff: dict[Node, Staff] = {}

        for instrument in instrument_staffs:
            assert len(instrument) > 0
            expected_instrument_width = len(instrument[0])

            # single staff
            if expected_instrument_width == 1:
                staff = Staff(durables=[], id=1)

                # map staff nodes across multiple systems
                # to the same staff scene object
                for group in instrument:
                    assert len(group) == expected_instrument_width
                    mung_staff_to_staff[group[0]] = staff
            
            # grand staff
            elif expected_instrument_width == 2:
                staff_top = Staff(durables=[], id=1)
                staff_bottom = Staff(durables=[], id=2)

                for group in instrument:
                    assert len(group) == expected_instrument_width
                    mung_staff_to_staff[group[0]] = staff_top
                    mung_staff_to_staff[group[1]] = staff_bottom
            
            else:
                raise ValueError(f"Unsupported number of staff in instrument {instrument}")

        return mung_staff_to_staff
    
    
    def _construct_accidental_for_notehead(self, notehead: Node, note: Note | GraceNote, graph: NotationGraph) -> None:
        accidentals = graph.children(notehead, class_filter=I.ACCIDENTAL_CLASS_NAMES)
        if len(accidentals) == 0:
            return
        
        names = [a.class_name for a in accidentals]
        # no need to return, the accidental is linked automatically
        Accidental(
            type_=self._acc_type_from_multiple_mung_class_names(names),
            parent=note
        )

    def _construct_accidental_for_key(self, accidental: Node, key: Key) -> None:
        Accidental(
                type_=self._acc_type_from_mung_class_name(accidental.class_name),
                parent=key,
            )


    def _acc_type_from_mung_class_name(self, class_name: str) -> AccidentalValue:
        _LOOKUP = {
            C.Accidentals.ACCIDENTAL_DOUBLE_FLAT : AccidentalValue.FLAT_FLAT,
            C.Accidentals.ACCIDENTAL_FLAT : AccidentalValue.FLAT,
            C.Accidentals.ACCIDENTAL_NATURAL : AccidentalValue.NATURAL,
            C.Accidentals.ACCIDENTAL_SHARP : AccidentalValue.SHARP,
            C.Accidentals.ACCIDENTAL_DOUBLE_SHARP : AccidentalValue.DOUBLE_SHARP
        }
        output = _LOOKUP.get(class_name) # type: ignore
        if output is None:
            raise ValueError(f"Unknown accidental type '{class_name}'")
        return output


    def _acc_type_from_multiple_mung_class_names(self, names: list[str]) -> AccidentalValue:
        if len(names) == 2:
            try:
                return self._acc_type_from_two_mung_class_names(names[0], names[1])
            except Exception as e:
                logger.warning(e)
                logger.warning(f"Trying first given name only, '{names[0]}'")

        if len(names) > 2:
            logger.warning(f"Trying first given name only, '{names[0]}'")
        
        return self._acc_type_from_mung_class_name(names[0])


    def _acc_type_from_two_mung_class_names(self, class_name1: str, class_name2: str) -> AccidentalValue:
        if class_name1 == class_name2:
            match class_name1:
                case C.Accidentals.ACCIDENTAL_FLAT:
                    return AccidentalValue.FLAT_FLAT
                case C.Accidentals.ACCIDENTAL_SHARP:
                    return AccidentalValue.SHARP_SHARP
                case _:
                    raise ValueError(f"Cannot deduce name from given class names: "
                                        f"'{class_name1}', '{class_name2}'")
        
        match set([class_name1, class_name2]):
            case set([C.Accidentals.ACCIDENTAL_NATURAL, C.Accidentals.ACCIDENTAL_FLAT]):
                return AccidentalValue.NATURAL_FLAT
            case set([C.Accidentals.ACCIDENTAL_NATURAL, C.Accidentals.ACCIDENTAL_SHARP]):
                return AccidentalValue.NATURAL_SHARP
            case _:
                raise ValueError(f"Cannot deduce name from given class names: "
                                    f"'{class_name1}', '{class_name2}'")


    
    def _get_stem_orientation_for_note(self, note: Node, graph: NotationGraph) -> StemValueToken:
        stems = graph.children(note, class_filter=C.NoteheadAttachments.STEM)
        
        # maybe a whole note
        if len(stems) == 0:
            return StemValueToken.NONE
        
        if len(stems) > 1:
            logger.warning(f"Too many stems found for notehead {note}, using the first one")
            stems.sort(key=lambda s: s.id)
        stem = stems[0]
        cached_so = self._stem_orientation_cache.get(stem)
        if cached_so is None:
            so = StemValueToken.from_int(infer_stem_orientation(stem, graph))
            self._stem_orientation_cache[stem] = so
            return so
        
        return cached_so
    
    def _construct_dots_for_durable_like(self, mung_durable: Node, durable: Durable | GraceNote, graph: NotationGraph) -> None:
        dots = graph.children(mung_durable, class_filter=C.NoteheadAttachments.AUGMENTATION_DOT)
        for _ in dots:
            Dot(durable=durable)
    
    def _construct_grace_note_beam(self, notes: list[GraceNote]) -> GraceNoteBeam:
        assert len(notes) > 0
        notes.sort(key=lambda s: s.at_durable_index)
        if len(notes) == 1:
            return GraceNoteBeam(
                begin=notes[0]
            )
        elif len(notes) == 2:
            return GraceNoteBeam(
                begin=notes[0],
                end=notes[1]
            )
        else:
            return GraceNoteBeam(
                begin=notes[0],
                continue_=notes[1:-1],
                end=notes[-1]
            )

    def _construct_grace_notes_for_durable(self, durable: Node, graph: NotationGraph) -> list[GraceNote]:
        grace_notes = graph.children(durable, class_filter=I.GRACE_NOTEHEAD_CLASS_NAMES)
        if len(grace_notes) == 0:
            return []
        
        beams_to_grace: defaultdict[Node, set[GraceNote]] = defaultdict(set)
        
        output = []
        for index, note in enumerate(sorted(grace_notes, key=lambda n: onset_beats(n))):
            stem_orientation = self._get_stem_orientation_for_note(note, graph)
            if stem_orientation == StemValueToken.NONE:
                stem_orientation = StemValueToken.default()
            
            gn = GraceNote(
                pitch=pitch(note),
                type_=NoteTypeValue.from_fraction(duration_beats_w_m(note)),
                at_durable_index=index,
                stem_orientation=stem_orientation
                )
            
            self._construct_accidental_for_notehead(note, gn, graph)
            self._construct_dots_for_durable_like(note, gn, graph)
            for b in graph.children(note, class_filter=C.NoteheadAttachments.BEAM):
                beams_to_grace[b].add(gn)

            output.append(gn)
        
        for grace_notes in beams_to_grace.values():
            self._construct_grace_note_beam(list(grace_notes))

        return output
    

    def _mung_class_name_to_articulation_type_and_placement(self, articulation: Node) -> tuple[ArticulationType, AboveBelowToken]:
        A = C.Articulation
        name = articulation.class_name.lower()
        if name.endswith("above"):
            placement = AboveBelowToken.ABOVE
        elif name.endswith("below"):
            placement = AboveBelowToken.BELOW
        else:
            raise ValueError(f"Articulation name '{articulation.class_name}' does not contain substring 'above' nor 'below'")
        
        _LOOKUP: dict[str, ArticulationType] = {
            A.ARTIC_STACCATO_ABOVE: ArticulationType.STACCATO,
            A.ARTIC_STACCATO_BELOW: ArticulationType.STACCATO,

            A.ARTIC_ACCENT_BELOW : ArticulationType.ACCENT,
            A.ARTIC_ACCENT_ABOVE : ArticulationType.ACCENT,

            A.ARTIC_STACCATO_ABOVE : ArticulationType.STACCATO,
            A.ARTIC_STACCATO_BELOW : ArticulationType.STACCATO,

            A.ARTIC_TENUTO_ABOVE : ArticulationType.TENUTO,
            A.ARTIC_TENUTO_BELOW : ArticulationType.TENUTO,

            A.ARTIC_STACCATISSIMO_ABOVE : ArticulationType.STACCATISSIMO,
            A.ARTIC_STACCATISSIMO_BELOW : ArticulationType.STACCATISSIMO,

            A.ARTIC_MARCATO_ABOVE : ArticulationType.STRONG_ACCENT,
            A.ARTIC_MARCATO_BELOW : ArticulationType.STRONG_ACCENT,
        }

        type_ = _LOOKUP.get(articulation.class_name)
        if type_ is None:
            raise ValueError(f"Uknown articulation type '{articulation.class_name}'")

        return type_, placement

    def _construct_articulations(self, mung_durable: Node, durable: Durable, graph: NotationGraph) -> None:
        articulations = graph.children(mung_durable, class_filter=C.Articulation.ALL())
        for mung_articulation in articulations:
            type_, placement = self._mung_class_name_to_articulation_type_and_placement(mung_articulation)
            Articulation(durable, type_, placement)
    
    def _construct_durable(self, durable: Node, graph: NotationGraph) -> Note | Rest | RepeatBar:
        
        if durable.class_name in I.NONGRACE_NOTEHEAD_CLASS_NAMES:
            def note_type_from_node(node: Node) -> NoteTypeValue:
                match node.class_name:
                    case C.Noteheads.NOTEHEAD_WHOLE:
                        return NoteTypeValue.WHOLE
                    case _:
                        return NoteTypeValue.from_fraction(duration_beats_w_m(node))
            
            grace_notes = self._construct_grace_notes_for_durable(durable, graph)
            
            stem_orientation = self._get_stem_orientation_for_note(durable, graph)
            note_type = note_type_from_node(durable)
            if stem_orientation is StemValueToken.NONE and note_type.has_stem():
                logger.warning(f"Note {durable} must have a stem but no was found, using default {StemValueToken.default()}")
                stem_orientation = StemValueToken.default()
            n = Note(
                fractional_duration_=duration_beats(durable),
                type_=note_type,
                fractional_onset_=onset_beats(durable),
                pitch=pitch(durable),
                grace_notes=grace_notes,
                stem_orientation=stem_orientation
            )
            self._construct_dots_for_durable_like(durable, n, graph)
            self._construct_accidental_for_notehead(durable, n, graph)
            self._construct_articulations(durable, n, graph)
            # construct_clef_change_for_durable(durable, n, graph)
            return n
        
        elif durable.class_name in I.REST_CLASS_NAMES:
            # print(durable)
            # print(durable.data)
            def rest_type_from_node(node: Node) -> NoteTypeValue:
                """
                Durables whose duration is dependant on measure
                duration might vary in duration. This function
                maps them directly to DurableType based on class
                name, not duration.

                For example: rest whole has duration 3 in 3/4 time
                signature, but duration 4 in 4/4 time signature.
                """
                match node.class_name:
                    case C.Rests.REST_WHOLE:
                        return NoteTypeValue.WHOLE
                    case C.Rests.REST_DOUBLE_WHOLE:
                        return NoteTypeValue.BREVE
                    case C.Rests.REST_LONGA:
                        return NoteTypeValue.LONG
                    case _:
                        return NoteTypeValue.from_fraction(duration_beats_w_m(durable))
            
            r = Rest(
                fractional_duration_=duration_beats(durable),
                type_=rest_type_from_node(durable),
                fractional_onset_=onset_beats(durable),
            )
            self._construct_dots_for_durable_like(durable, r, graph)
            # construct_clef_change_for_durable(durable, r, graph)
            return r

        elif durable.class_name == C.Repeat.REPEAT_1_BAR:
            logger.info(f"Constructing {RepeatBar.__name__} based on {durable}")

            repeat = RepeatBar(
                type_=NoteTypeValue.NONE,
                fractional_duration_=duration_beats(durable),
                fractional_onset_=onset_beats(durable),
            )
            return repeat
        
        raise ValueError(f"Unknown durable type: {durable}")
    
    def load_from_file(self, file_name: Path | str) -> Score:
        return self.load(NotationGraph.from_file(file_name))
 
    def load(self, data: NotationGraph) -> Score:
        graph = data
        # systems = group_staffs_into_systems(graph.vertices)
        # system_measures = group_by_system_measure(graph)
        # staffs = graph.filter_vertices(C.STAFF)
        instros = get_instrument_groups_from_systems(graph)
        systems = group_by_system_measure_and_system(graph)
        system_measure_count = sum(len(s) for s in systems)
        assert len(instros) == len(systems)
        def is_on_staff(staffs: list[Node], node: Node, graph: NotationGraph) -> bool:
            return any(graph.is_child_of(staff, node) for staff in staffs)
        
        class Struct:
            def __init__(self, i: int, nodes: list[Node]) -> None:
                self.id_ = i
                self.nodes = nodes
            
            def __str__(self) -> str:
                return f"(id={self.id_}, nodes={self.nodes})"
            
            def __repr__(self) -> str:
                return str(self)

        instros_to_measures: dict[frozenset[Node], list[Struct]] = {}
        
        instrument_staffs = graph_to_instruments(graph)
        # print(instrument_staffs)

        # exit()
        new_system_indexes: list[int] = []
        # loop through system, count measures visited
        next_measure_id = MEASURE_INDEX_START
        for instrument_groups, sys in zip(instros, systems):
            offset = next_measure_id
            if offset != MEASURE_INDEX_START:
                new_system_indexes.append(offset)
            for group in instrument_groups:
                # print(group)
                # print(sys)
                instros_to_measures[frozenset(group)] = []
                for offset, measure in enumerate(sys, start=next_measure_id):
                    
                    instros_to_measures[frozenset(group)].append(
                        Struct(offset, [
                        symbol for symbol in measure if is_on_staff(group, symbol, graph)
                    ]))
                    
                    # print(frozenset(group), instros_to_measures[frozenset(group)])
            next_measure_id = offset + 1
        # print(new_system_indexes)
        
        # exit()
        _STEM_ORIENTATION_CACHE: dict[Node, StemValueToken] = {}
        

        # from .graph import RepeatBar
        # from .graph.in_part_measure_modifier import InPartMeasureModifier
        
        # from .graph import Subevent
        subevents: list[Subevent] = []
        # from .graph import Durable
        # durables: dict[Node, Durable] = {}
        # def construct_subevents()
        # from .graph import Chord
        mung_staffs_to_staffs = self._construct_staffs(instrument_staffs)
        def get_staff_from_symbol_on_staff(symbol: Node, mapping: dict[Node, Staff], graph: NotationGraph):
            """
            Durable is MuNG node that belongs to exactly one staff.
            Mapping maps staff MuNG nodes to MusicXML graph staffs.
            """
            staffs = graph.children(symbol, class_filter=C.Staves.STAFF)
            assert len(staffs) == 1
            mung_staff = staffs[0]
            return mapping[mung_staff]


        parts: list[ScorePart] = []
        system_measures: list[SystemMeasure] = []
        
        measures_by_id: defaultdict[int, list[PartMeasure]] = defaultdict(list)
        durables_by_voice: defaultdict[int, list[Durable]] = defaultdict(list)
        subevents_by_beam: defaultdict[Node, set[Subevent]] = defaultdict(set)
        subevents_by_slur: defaultdict[Node, set[Subevent]] = defaultdict(set)
        subevents_by_tremolo_beam: defaultdict[Node, set[Subevent]] = defaultdict(set)
        durables_by_tie: defaultdict[Node, set[Durable]] = defaultdict(set)
        subevent_by_hairpin: defaultdict[Node, set[Subevent]] = defaultdict(set)

        subevents_by_tuple: defaultdict[Node, set[Subevent]] = defaultdict(set)
        # for braces and brackets
        parts_by_group: defaultdict[Node, set[ScorePart]] = defaultdict(set)


        for instrument in instrument_staffs:
            # instrument is a list of lists of staffs
            # instrument -> staffs in a system -> staffs
            staff_to_durables: defaultdict[Staff, list[Durable]] = defaultdict(list)
            staff_to_others: defaultdict[Staff, list[Clef]] = defaultdict(list)
            logger.info(f"processing instrument: {instrument}")
            # for instro_staffs, content in instros_to_measures.items():
            graph_measures: list[PartMeasure] = []

            for measure in (chain.from_iterable(instros_to_measures[frozenset(s)] for s in instrument)):
                # print(measure)
                # continue
                # print(instros_to_measures[frozenset(instrument[0])])

                single_measure_subevents: list[Subevent] = []
                # print(measure.nodes)
                subs = subevents_from_list_of_symbols([x for x in measure.nodes if x.class_name in I.CLASSES_BEARING_DURATIONS], graph)
                # print(subs)
                for sub in subs:
                    try:
                        chordlike = []
                        found_beams: list[Node] = []
                        found_tuplets: list[Node] = []
                        found_slurs: list[Node] = []
                        found_hairpins: list[Node] = []
                        found_tremolo_beams: list[Node] = []
                        found_tremolo_singles: list[Node] = []

                        for dur in sub:
                            durable = self._construct_durable(dur, graph)
                            # durables[dur] = durable
                            chordlike.append(durable)
                            staff_to_durables[
                                get_staff_from_symbol_on_staff(dur, mung_staffs_to_staffs, graph)
                            ].append(durable)

                            durables_by_voice[voice(dur)].append(durable)

                            # register beams, tuplets, slurs etc even for RepeatBar
                            # but! then repeat beat need to be thrown out in slur construction
                            # if isinstance(durable, Note) or isinstance(durable, Rest):
                            found_beams.extend(graph.children(dur, class_filter=C.NoteheadAttachments.BEAM))
                            found_tuplets.extend(graph.children(dur, class_filter=C.Tuplets.TUPLET))
                            found_slurs.extend(graph.children(dur, class_filter=C.Spanners.SLUR))
                            found_hairpins.extend(graph.children(dur, class_filter=I.HAIRPINS))
                            found_tremolo_beams.extend(graph.children(dur, class_filter=C.Tremolo.TREMOLO_BEAM))
                            found_tremolo_singles.extend(graph.children(dur, class_filter=I.TREMOLO_SINGLES))

                            # register tie per durable
                            for tie in graph.children(dur, class_filter=C.Spanners.TIE):
                                durables_by_tie[tie].add(durable)

                        # all durables inside a subevent should be either notes, rests or other
                        if isinstance(chordlike[0], Note):
                            chord = Chord(chordlike)
                            subevent = chord
                            single_measure_subevents.append(chord)
                        
                        else:
                            assert len(chordlike) == 1
                            single_measure_subevents.append(chordlike[0])
                            subevent = chordlike[0]
                        
                        # register large objects
                        for b in found_beams:
                            subevents_by_beam[b].add(subevent)
                        
                        for t in found_tuplets:
                            subevents_by_tuple[t].add(subevent)
                        
                        for s in found_slurs:
                            subevents_by_slur[s].add(subevent)
                        
                        for h in found_hairpins:
                            subevent_by_hairpin[h].add(subevent)
                        
                        for t in found_tremolo_beams:
                            subevents_by_tremolo_beam[t].add(subevent)

                        if len(found_tremolo_singles) > 0:
                            TremoloSingle(
                                subevent,
                                len(found_tremolo_singles),
                                AboveBelowToken.from_int(
                                    infer_vertical_object_placement_relative_to_notes(
                                        found_tremolo_singles[0],
                                        graph,
                                        sub
                                    )
                                )
                            )
                    
                    except AssertionError as ae:
                        raise ValueError(f"Unable to construct subevent from: {sub}") from ae
                
                # fallback for clefs that are not assigned to staffline
                
                def get_default_clef_line_from_node(clef: Node) -> int:
                    """
                    Default staffline delta is, for pitch inference,
                    implemented as the number of staff lines and spaces
                    from the middle staffline.
                    This method matches the clef type and converts
                    the staffline delta, so that the returner number
                    is an index of its staff line from bottom to top,
                    starting from 1.
                    """
                    from mung2midi.inference.clefs_impl import get_clef_data_from_node
                    base = get_clef_data_from_node(clef)
                    return (base.default_staffline_delta // 2) + 3

                # find clefs and key
                def find_line_index_for_symbol(symbol: Node, graph: NotationGraph) -> int:
                    staffs = graph.children(symbol, class_filter=C.Staves.STAFF)
                    assert len(staffs) > 0, f"Unsupported number of staffs for {symbol}, {staffs}"
                    lines = graph.children(symbol, class_filter=C.Staves.STAFF_LINE)
                    if len(lines) == 0:
                        index = get_default_clef_line_from_node(symbol)
                        logger.warning(f"{symbol} is not assigned to any staff line, choosing default {index}")
                        return index
                    
                    staff = staffs[0]
                    line = lines[0]

                    s_lines = graph.children(staff, class_filter=C.Staves.STAFF_LINE)
                    assert len(s_lines) == 5
                    # lowest staff line is first
                    s_lines.sort(key=lambda l: l.top, reverse=True)
                    return s_lines.index(line) + 1

                modifiers: list[InMeasureModifier] = []

                # CLEFS
                def _get_clef_sign(class_name: str) -> ClefSign:
                    _LOOKUP: dict[str, ClefSign] = {
                        C.Clefs.C_CLEF : ClefSign.C,
                        C.Clefs.F_CLEF : ClefSign.F,
                        C.Clefs.G_CLEF : ClefSign.G,
                    }
                    return _LOOKUP[C.Clefs.simplify(class_name)]
                
                for node in measure.nodes:
                    for symbol in graph.children(node, class_filter=I.CLEF_CLASS_NAMES):
                        clef = Clef(
                            fractional_onset_=onset_beats(symbol),
                            sign=_get_clef_sign(symbol.class_name),
                            line=find_line_index_for_symbol(symbol, graph)
                        )
                        modifiers.append(clef)
                        staff_to_others[
                            get_staff_from_symbol_on_staff(symbol, mung_staffs_to_staffs, graph)
                        ].append(clef)
                        # logger.info(f"Added clef based on {symbol}")
                
                # KEY SIGNATURES
                key_sigs_by_onset: defaultdict[Fraction, list[Node]] = defaultdict(list)
                for ks in chain.from_iterable(graph.children(s, class_filter=C.KeySignature.KEY_SIGNATURE) for s in measure.nodes):
                    key_sigs_by_onset[onset_beats(ks)].append(ks)
                
                for onset, kss in key_sigs_by_onset.items():
                    if len(kss) > 1:
                        logger.warning(f"Found multiple key signatures {[ks.id for ks in kss]} for in-measure onset {onset}, choosing the first one")
                    ks = kss[0]

                    key = Key(onset)
                    for acc in graph.children(ks, class_filter=I.ACCIDENTAL_CLASS_NAMES):
                        self._construct_accidental_for_key(acc, key)
                    modifiers.append(key)
                    logger.info(f"Added key based on {ks}")
                
                # TIME SIGNATURES
                time_sigs_by_onset: defaultdict[Fraction, list[Node]] = defaultdict(list)
                for ts in chain.from_iterable(graph.children(s, class_filter=C.TimeSignatures.TIME_SIGNATURE) for s in measure.nodes):
                    time_sigs_by_onset[onset_beats(ts)].append(ts)
                
                # from .construct import construct_accidental_for_key
                # from .construct.construct_time_signature import construct_time_signature
                for onset, tss in time_sigs_by_onset.items():
                    if len(tss) > 1:
                        logger.warning(f"Found multiple time signatures {[ks.id for ks in tss]} for in-measure onset {onset}, choosing the first one")
                    ts = tss[0]
                    time_sig = self._construct_time_signature(ts, onset_beats(ts), graph)
                    if time_sig is None:
                        logger.warning(f"Could not interpret {ts}")
                        continue
                    modifiers.append(time_sig)
                    logger.info(f"Added time signature based on {ts}")
                
                m = PartMeasure(
                    id=measure.id_,
                    subevents=single_measure_subevents,
                    modifiers=modifiers
                )
                
                measures_by_id[measure.id_].append(m)
                graph_measures.append(m)
            # print(graph_measures)
                # print(graph_measures[-1])
            for staff, values in staff_to_durables.items():
                staff.durables = values
            
            for staff, values in staff_to_others.items():
                staff.other_symbols = values # type: ignore
            
            score_part = ScorePart(part_measures=graph_measures)
            parts.append(score_part)

            # collect all braces and brackets
            for grouping in set(chain.from_iterable(
                    graph.parents(staff, class_filter=C.StaffGroupingBracketsAndBraces.STAFF_GROUPING)
                    for staff in chain.from_iterable(instrument)
                )):
                parts_by_group[grouping].add(score_part)
                
        for id_, measures in measures_by_id.items():
            system_measures.append(SystemMeasure(
                id=id_,
                part_measures=measures,
                is_new_system=id_ in new_system_indexes
            ))
        
        score = Score(score_parts=parts, system_measures=system_measures)
        
        MAX_VOICES = 8
        for id_ in durables_by_voice.keys():
            assert id_ <= MAX_VOICES, f"Unsupported number of voices. {id_}"
        
        voices: list[Voice] = []
        for id_ in range(1, MAX_VOICES + 1):
            voices.append(Voice(id_, durables_by_voice[id_]))

        beams: list[DurableBeam] = []
        
        from dataclasses import dataclass

        @dataclass(frozen=True)
        class _GroupingStruct:
            # mung_grouping: Node
            parts: tuple[ScorePart, ...]
            bracket_type: GroupSymbolToken

            def __eq__(self, other: object) -> bool:
                if not isinstance(other, _GroupingStruct):
                    return NotImplemented
                # Equal if part ids are equal and bracket types are equal
                return (
                    tuple(p.id for p in self.parts) == tuple(p.id for p in other.parts)
                    and self.bracket_type == other.bracket_type
                )
            
            def __hash__(self) -> int:
                # Hash based on part ids and bracket type
                return hash((tuple(p.id for p in self.parts), self.bracket_type))
            
            def __str__(self) -> str:
                return f"{type(self).__name__}({[x.id for x in self.parts]}, {self.bracket_type})"

        gs: set[_GroupingStruct] = set()
        for grouping, score_parts in parts_by_group.items():
            brackets = graph.children(grouping, class_filter=I.INSTRUMENT_GROUP_BRACKETS)
            if len(brackets) > 1:
                logger.warning(f"{grouping} has multiple brackets assigned, outputting all.")

            if len(brackets) == 0:
                gs.add(_GroupingStruct(
                    # grouping,
                    tuple(score_parts),
                    GroupSymbolToken.NONE
                ))
            else:
                for bracket in brackets:
                    gs.add(_GroupingStruct(
                        # grouping,
                        tuple(score_parts),
                        GroupSymbolToken(bracket.class_name)
                    ))
        
        for g in gs:
            PartGroup(list(g.parts), bracket_type=g.bracket_type)
            # print(f"Constructed part group {g}")

        # print(subevents_by_beam)
        for mung_beam, subs in subevents_by_beam.items():
            # print(mung_beam, len(subs))
            logger.debug(f"Creating beam based on {mung_beam}")
            beams.append(self._construct_durable_beam(mung_beam, list(subs)))
            # print(len(subs))

        tuplets: list[Tuplet] = []
        for mung_tuplet, subs in subevents_by_tuple.items():
            logger.debug(f"Creating tuplet based on {mung_tuplet}")
            tuplets.append(self._construct_tuplet(mung_tuplet, list(subs), graph))
        
        slurs: list[Slur] = []
        ties: list[Tie] = []
        for mung_slur, subs in subevents_by_slur.items():
            obj = self._construct_slur(mung_slur, list(subs), graph)
            slurs.append(obj)
            
            if obj is not None:
                logger.debug(f"Created {type(obj).__name__} based on {mung_slur}")

        for mung_tie, durs in durables_by_tie.items():
            obj = self._try_construct_tie(mung_tie, list(durs), graph)
            if isinstance(obj, Tie):
                ties.append(obj)
            elif isinstance(obj, Slur):
                slurs.append(obj)

            if obj is not None:
                logger.debug(f"Created {type(obj).__name__} based on {mung_tie}")

        for mung_hairpin, subs in subevent_by_hairpin.items():
            self._construct_wedge(mung_hairpin, list(subs), graph)
            logger.info(f"Constructed {Wedge.__name__} base on {mung_hairpin}")
        
        
        @dataclass(frozen=True)
        class TremoloBeamStruct:
            start: Subevent
            stop: Subevent

            def __eq__(self, other: Any) -> bool:
                return (
                    isinstance(other, TremoloBeamStruct)
                    and self.start == other.start
                    and self.stop == other.stop
                )
            
            @classmethod
            def from_list(cls, subs: list[Subevent]) -> Self:
                start, stop = sorted(subs, key=lambda s: s.in_measure_fractional_onset)
                return cls(start, stop)


        # print(subevents_by_tremolo_beam.values())
        connected_by_tremolo_beam: list[list[Subevent]] = UnionFind.merge_groups([list(g) for g in subevents_by_tremolo_beam.values()])
        for mung_tremolo_beam, subs in subevents_by_tremolo_beam.items():
            if len(subs) != 2:
                logger.warning(
                    f"Invalid number of subevents connected to {mung_tremolo_beam}, "
                    f"found {len(subs)}, expected 2."
                )
            else:
                pass
            
        # filter out tremolos that connect more than two subevents
        tbs = [TremoloBeamStruct.from_list(g) for g in connected_by_tremolo_beam if len(g) == 2]
        tremolo_counts = Counter(tbs)
        for tb, c in tremolo_counts.items():
            TremoloBeam(start=tb.start, stop=tb.stop, marks=c)
            logger.info("Created tremolo beam")
        # print(connected_by_tremolo_beam)


            # print(staff)
            # print(staff.score_part)
        # print(graph_to_instruments(graph))
        # print(beams)
        # for part in parts:
        #     xml_ScorePart(part)
        # for part in parts:
        #     print(part.id, len(part.part_measures))
        #     print([pm.id_ for pm in part.part_measures])
        # exit()
        return score
        # from .export.to_musicxml.engine import MusicXML_ExportEngine
        # ee = MusicXML_ExportEngine()
        # ee.export_to_file(score, "temp.musicxml")