from fractions import Fraction
from pathlib import Path
from typing import Self, Any, Optional, Type
from collections import defaultdict, Counter
from itertools import chain
from dataclasses import dataclass, field
from contextlib import contextmanager


from mung import NotationGraph, Node
from mung.constants import ClassNameConstants as C, InferenceEngineConstants as I
from mung.subevents_from_nodes import subevents_from_list_of_symbols
from mung.interpret import BasicTimeSignatureInterpreter
from mung.graph import group_by_system_measure_and_system, group_staffs_into_systems
from ..load_engine import LoadEngine
from ....preprocessing.instruments import (
    graph_to_instruments,
    get_instrument_groups_from_systems
)
from ...graph import *
from ...graph.utils import IDClass

from .utils import (
    get_voice,
    get_onset_beats,
    _log_object_creation
)
from .construct_key_signature import construct_key_signature
from .construct_time_signature import construct_time_signature
from .construct_beam import construct_durable_beam
from .construct_articulation import construct_articulation
from .construct_tuplet import construct_tuplet
from .construct_slur import construct_slur
from .construct_tie import try_construct_tie
from .construct_wedge import construct_wedge
from .construct_dynamics import construct_dynamics
from .construct_clef import construct_clef
from .construct_tremolo import construct_tremolo_single
from .construct_durable import construct_durable
from .construct_fermata import construct_fermata
from .construct_lyric import construct_lyric
from .construct_tempo import construct_tempo
from .construct_dynamics_text import construct_dynamics_text
from .construct_interpretation_text import construct_interpretation_text
from .construct_barline_mapping import compute_bar_styles
from .construct_barlines import construct_bars_from_bar_mapping
from .construct_volta import construct_volta
from .construct_coda import construct_coda
from .construct_segno import construct_segno
from .construct_rest_text import construct_rest_text
from .construct_ornaments import (
    construct_turn,
    construct_trill,
    construct_short_trill,
    construct_arpeggiato,
)
from .construct_ottava import construct_ottava


from ....logger import logger
from ....utils import find_subgraphs_bfs
from .collector import SGObjectCollector, CollectorRecord
from .settings import MuNGLoaderSettings


class MuNG_LoadEngine(LoadEngine):
    def __init__(self, settings: Optional[MuNGLoaderSettings] = None) -> None:
        self._btsi = BasicTimeSignatureInterpreter()
        self._settings = settings if settings is not None else MuNGLoaderSettings()
    
    def _get_symbols_staff(self, symbol: Node, mapping: dict[Node, Staff], graph: NotationGraph):
        """
        Durable is MuNG node that belongs to exactly one staff.
        Mapping maps staff MuNG nodes to MusicXML graph staffs.
        """
        staffs = graph.children(symbol, class_filter=C.Staves.STAFF)
        assert len(staffs) == 1
        mung_staff = staffs[0]
        return mapping[mung_staff]
    
    def _construct_staff_mapping(
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

    def _construct_lyric_level_mapping(
        self,
        instrument: list[list[Node]],
        graph: NotationGraph,
        debug_tag: bool = False
    ) -> dict[Node, LyricLevel]:
        """
        Instrument is a collection (outer list) of staffs belonging to one
        instrument through multiple systems (inner list).

        Creates LyricLevel scene objects for single instrument
        and returns mapping from lyric MuNG nodes to LyricLevel.
        """
        lyrics_per_system: list[set[Node]] = []

        # collect lyrics per system per instrument
        for instrument_system in instrument:
            lyrics = set()

            for staff in instrument_system:
                durables = graph.parents(staff, class_filter=I.NOTEHEADS_AND_RESTS)
                for durable in durables:
                    lyrics.update(graph.children(durable, class_filter=[C.Lyrics.LYRICS_TEXT, C.Lyrics.LYRICS_UNISONO]))
            
            lyrics_per_system.append(lyrics)

        output: dict[Node, LyricLevel] = {}
        for system_lyrics in lyrics_per_system:
            def _has_edge(lyric1: Node, lyric2: Node, graph: NotationGraph) -> bool:
                return (
                    graph.is_precedence_parent_of(lyric1, lyric2)
                    or graph.is_precedence_parent_of(lyric2, lyric1)
                )
            # sort 
            groups = find_subgraphs_bfs(list(system_lyrics), lambda f, s: _has_edge(f, s, graph))
            groups.sort(key=lambda g: g[0].vertical_center)

            for index, group in enumerate(groups, start=1):
                level = LyricLevel(index, [])

                for lyric in group:
                    output[lyric] = level
                    if debug_tag:
                        lyric.data["lyric_number"] = index
        
        return output
    
    def load_from_file(self, file_name: Path | str) -> Score:
        return self.load(NotationGraph.from_file(file_name))
 
    def load(self, data: NotationGraph) -> Score:
        graph = data

        instros = get_instrument_groups_from_systems(graph)
        systems = group_by_system_measure_and_system(graph)

        assert len(instros) == len(systems)
        def is_on_staff(staffs: list[Node], node: Node, graph: NotationGraph) -> bool:
            """
            Returns `True`, if `node` is a connected to any of the `staffs`.
            """
            return any(graph.is_child_of(staff, node) for staff in staffs)
        
        class _InstrumentMeasureStruct:
            def __init__(self, i: int, nodes: list[Node]) -> None:
                self.id_ = i
                self.nodes = nodes
            
            def __str__(self) -> str:
                return f"(id={self.id_}, nodes={self.nodes})"
            
            def __repr__(self) -> str:
                return str(self)

        instros_to_measures: defaultdict[frozenset[Node], list[_InstrumentMeasureStruct]] = defaultdict(list)
        
        instrument_staffs = graph_to_instruments(graph)

        new_system_indexes: list[int] = []

        # loop through system, index measures visited
        # for system:
        #   for instrument in system: (instrument is defined by one or two staffs)
        #       retrieve all nodes linked to these staff
        next_measure_id = self._settings.measure_index_start
        for instrument_groups, sys in zip(instros, systems):
            offset = next_measure_id
            if offset != self._settings.measure_index_start:
                new_system_indexes.append(offset)
            
            for group in instrument_groups:
                for offset, measure in enumerate(sys, start=next_measure_id):
                    
                    # retrieve all symbols linked to instrument staffs
                    instros_to_measures[frozenset(group)].append(
                        _InstrumentMeasureStruct(offset, [
                        symbol for symbol in measure if is_on_staff(group, symbol, graph)
                    ]))
                    
            next_measure_id = offset + 1
        
        
        mung_staffs_to_staffs = self._construct_staff_mapping(instrument_staffs)

        parts: list[ScorePart] = []
        system_measures: list[ScoreMeasure] = []
        
        measures_by_id: defaultdict[int, list[PartMeasure]] = defaultdict(list)
        durables_by_voice: defaultdict[int, list[Durable]] = defaultdict(list)

        # for braces and brackets
        parts_by_group: defaultdict[Node, set[ScorePart]] = defaultdict(set)
        # for volta
        volta_by_system_measure_id: defaultdict[Node, set[int]] = defaultdict(set)

        durable_collector: SGObjectCollector[Durable] = SGObjectCollector(
            [
                CollectorRecord[Durable](Tie, C.Spanners.TIE, try_construct_tie),
            ]
        )
        
        subevent_collector: SGObjectCollector[Subevent] = SGObjectCollector(
            [
                CollectorRecord[Subevent](Beam, C.NoteheadAttachments.BEAM, construct_durable_beam),
                CollectorRecord[Subevent](Articulation, C.Articulation.ALL(), construct_articulation), # type: ignore
                CollectorRecord[Subevent](Tuplet, C.Tuplets.TUPLET, construct_tuplet),
                CollectorRecord[Subevent](Slur, C.Spanners.SLUR, construct_slur),
                CollectorRecord[Subevent](Wedge, I.HAIRPINS, construct_wedge), # type: ignore
                CollectorRecord[Subevent](Dynamics, C.Dynamics.DYNAMICS_TEXT, construct_dynamics),
                CollectorRecord[Subevent](Fermata, [C.NoteheadAttachments.FERMATA_ABOVE, C.NoteheadAttachments.FERMATA_BELOW], construct_fermata),
                CollectorRecord[Subevent](Tempo, C.Tempo.ALL(), construct_tempo), # type: ignore
                CollectorRecord[Subevent](DynamicsText, [C.Dynamics.DYNAMIC_CRESCENDO, C.Dynamics.DYNAMIC_DIMINUENDO], construct_dynamics_text),
                CollectorRecord[Subevent](InterpretationText, C.Text.INTERPRETATION_TEXT, construct_interpretation_text),
                CollectorRecord[Subevent](Segno, C.Repeat.SEGNO, construct_segno),
                CollectorRecord[Subevent](Coda, C.Repeat.CODA, construct_coda),
                CollectorRecord[Subevent](RestText, C.Text.REST_TEXT, construct_rest_text),
                CollectorRecord[Subevent](Turn, [C.Ornaments.ORNAMENT_TURN, C.Ornaments.ORNAMENT_TURN_INVERTED], construct_turn),
                CollectorRecord[Subevent](Trill, C.Ornaments.ORNAMENT_TRILL, construct_trill),
                CollectorRecord[Subevent](ShortTrill, C.Ornaments.ORNAMENT_SHORT_TRILL, construct_short_trill),
                CollectorRecord[Subevent](Arpeggiato, C.Arpeggiato.ALL(), construct_arpeggiato), # type: ignore
                CollectorRecord[Subevent](Ottava, C.Octaves.OTTAVA_SPANNER, construct_ottava),

                CollectorRecord[Subevent](TremoloBeam, C.Tremolo.TREMOLO_BEAM, None),
                CollectorRecord[Subevent](Lyric, [C.Lyrics.LYRICS_TEXT, C.Lyrics.LYRICS_UNISONO], None),
            ]
        )

        lyrics_to_level: dict[Node, LyricLevel] = {}
        for instrument in instrument_staffs:
            lyrics_to_level.update(self._construct_lyric_level_mapping(instrument, graph))

        
        for instrument in instrument_staffs:
            # instrument is a list of lists of staffs
            # instrument -> staffs in a system -> staffs
            staff_to_durables: defaultdict[Staff, list[Durable]] = defaultdict(list)
            staff_to_others: defaultdict[Staff, list[Clef]] = defaultdict(list)
            from ...graph.grace_note import GraceNote
            staff_to_grace_notes: defaultdict[Staff, list[GraceNote]] = defaultdict(list)
            logger.info(f"Processing instrument: {instrument}")
            
            part_measures: list[PartMeasure] = []

            for measure in (chain.from_iterable(instros_to_measures[frozenset(s)] for s in instrument)):
                single_measure_subevents: list[Subevent] = []
                found_grace_notes: set[Node] = set()

                subs = subevents_from_list_of_symbols([x for x in measure.nodes if x.class_name in I.CLASSES_BEARING_DURATIONS], graph)
                
                for sub in subs:
                    try:
                        chordlike = []
                        found_tremolo_singles: list[Node] = []

                        for dur in sub:
                            durable = construct_durable(dur, graph)
                            chordlike.append(durable)

                            staff_to_durables[
                                self._get_symbols_staff(dur, mung_staffs_to_staffs, graph)
                            ].append(durable)

                            durables_by_voice[get_voice(dur)].append(durable)

                            subevent_collector.collect_nodes(dur, graph)
                            durable_collector.collect_nodes(dur, graph)

                            # register tremolo singles
                            for tremolo_single in graph.children(dur, class_filter=I.TREMOLO_SINGLES):
                                if tremolo_single not in found_tremolo_singles:
                                    found_tremolo_singles.append(tremolo_single)
                            
                            # register volta
                            for volta in graph.parents(dur, class_filter=C.Repeat.VOLTA):
                                volta_by_system_measure_id[volta].add(measure.id_)
                            
                            # register grace notes
                            found_grace_notes.update(graph.children(dur, class_filter=I.GRACE_NOTEHEAD_CLASS_NAMES))

                        # All durables inside a subevent should be either notes, rests or other
                        if isinstance(chordlike[0], Note):
                            chord = Chord(chordlike)
                            subevent = chord
                            single_measure_subevents.append(chord)
                        
                        else:
                            assert len(chordlike) == 1
                            single_measure_subevents.append(chordlike[0])
                            subevent = chordlike[0]
                        
                        # Update collectors
                        subevent_collector.add_score_object(subevent)
                        for d in subevent.all_durables:
                            durable_collector.add_score_object(d)
                        
                        # TREMOLO SINGLES
                        if len(found_tremolo_singles) > 0:
                            construct_tremolo_single(
                                subevent,
                                sub,
                                found_tremolo_singles,
                                graph
                            )
                            
                        # GRACE NOTES
                        from .construct_grace_notes import construct_grace_notes_for_durable
                        for mung_grace, grace in construct_grace_notes_for_durable(sub, subevent, graph):
                            staff_to_grace_notes[
                                    self._get_symbols_staff(mung_grace, mung_staffs_to_staffs, graph)
                                ].append(grace)
                            
                    except AssertionError as ae:
                        raise ValueError(f"Unable to construct subevent from: {sub}") from ae
                
                modifiers: list[InMeasureModifier] = []

                # CLEFS
                for node in measure.nodes:
                    for mung_clef in graph.children(node, class_filter=I.CLEF_CLASS_NAMES):
                        clef = construct_clef(mung_clef, graph)

                        modifiers.append(clef)
                        staff_to_others[
                            self._get_symbols_staff(mung_clef, mung_staffs_to_staffs, graph)
                        ].append(clef)
                        _log_object_creation(clef, mung_clef)
                
                # KEY SIGNATURES
                key_sigs_by_onset: defaultdict[Fraction, list[Node]] = defaultdict(list)
                for ks in chain.from_iterable(graph.children(s, class_filter=C.KeySignature.KEY_SIGNATURE) for s in measure.nodes):
                    key_sigs_by_onset[get_onset_beats(ks)].append(ks)
                
                for onset, kss in key_sigs_by_onset.items():
                    if len(kss) > 1:
                        logger.warning(f"Found multiple key signatures {[ks.id for ks in kss]} for in-measure onset {onset}, choosing the first one")
                    ks = kss[0]

                    key = construct_key_signature(ks, onset, graph)
                    modifiers.append(key)
                    _log_object_creation(key, ks)
                
                # TIME SIGNATURES
                time_sigs_by_onset: defaultdict[Fraction, list[Node]] = defaultdict(list)
                for ts in chain.from_iterable(graph.children(s, class_filter=C.TimeSignatures.TIME_SIGNATURE) for s in measure.nodes):
                    time_sigs_by_onset[get_onset_beats(ts)].append(ts)
                
                for onset, tss in time_sigs_by_onset.items():
                    if len(tss) > 1:
                        logger.warning(f"Found multiple time signatures {[ks.id for ks in tss]} for in-measure onset {onset}, choosing the first one")
                    ts = tss[0]
                    time_sig = construct_time_signature(ts, get_onset_beats(ts), graph, self._btsi)
                    if time_sig is None:
                        logger.warning(f"Could not interpret {ts}")
                        continue
                    modifiers.append(time_sig)
                    _log_object_creation(time_sig, ts)
                
                m = PartMeasure(
                    id=measure.id_,
                    subevents=single_measure_subevents,
                    modifiers=modifiers
                )
                
                measures_by_id[measure.id_].append(m)
                part_measures.append(m)
            
            for staff, values in staff_to_durables.items():
                staff.durables = values
                
            for staff, values in staff_to_grace_notes.items():
                staff.grace_notes = values
            
            for staff, values in staff_to_others.items():
                staff.other_symbols = values # type: ignore
            
            all_part_staff = set()
            for pm in part_measures:
                for d in pm.all_durables:
                    all_part_staff.add(d.staff)
            
            score_part = ScorePart(part_measures=part_measures, staffs=list(all_part_staff))
            parts.append(score_part)

            # collect all braces and brackets
            for mung_grouping in set(chain.from_iterable(
                    graph.parents(staff, class_filter=C.StaffGroupingBracketsAndBraces.STAFF_GROUPING)
                    for staff in chain.from_iterable(instrument)
                )):
                parts_by_group[mung_grouping].add(score_part)
        

        barline_types = compute_bar_styles(graph, self._settings.measure_index_start)
        system_index = 0
        measure_index = self._settings.measure_index_start
        for id_, measures in measures_by_id.items():
            if id_ in new_system_indexes:
                system_index += 1
                measure_index = self._settings.measure_index_start

            right_barline_onset = max(measures, key=lambda m: m.fractional_duration).fractional_duration
            
            bars = construct_bars_from_bar_mapping(
                barline_types,
                system_index,
                measure_index,
                right_barline_onset
            )

            system_measures.append(ScoreMeasure(
                id=id_,
                part_measures=measures,
                is_new_system=id_ in new_system_indexes,
                bars=bars
            ))
            measure_index += 1
        
        score = Score(score_parts=parts, score_measures=system_measures)
        
        # REGISTER VOLTA
        for mung_volta, sm_ids in volta_by_system_measure_id.items():
            assert len(sm_ids) > 0
            volta = construct_volta(
                mung_volta,
                [score.get_system_measure_by_id(id_) for id_ in sm_ids],
                graph
            )
        
        for id_ in durables_by_voice.keys():
            assert id_ <= self._settings.voice_limit, f"Unsupported number of voices. {id_}"
        
        voices: list[Voice] = []
        for id_ in range(1, self._settings.voice_limit + 1):
            voices.append(Voice(id_, durables_by_voice[id_]))
        

        @dataclass(frozen=True)
        class _GroupingStruct:
            parts: frozenset[ScorePart]
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
                return hash((tuple(p._id for p in self.parts), self.bracket_type))
            
            def __str__(self) -> str:
                return f"{type(self).__name__}({[x.id for x in self.parts]}, {self.bracket_type})"

        gs: set[_GroupingStruct] = set()
        for grouping, score_parts in parts_by_group.items():
            brackets = graph.children(grouping, class_filter=I.INSTRUMENT_GROUP_BRACKETS)
            if len(brackets) > 1:
                logger.warning(f"{grouping} has multiple brackets assigned, outputting all.")
            if len(brackets) == 0:
                gs.add(_GroupingStruct(
                    frozenset(score_parts),
                    GroupSymbolToken.NONE,
                ))
            else:
                for bracket in brackets:
                    gs.add(_GroupingStruct(
                        frozenset(score_parts),
                        GroupSymbolToken(bracket.class_name),
                    ))
        
        for g in gs:
            if g.bracket_type == GroupSymbolToken.NONE:
                continue
            PartGroup(
                list(g.parts),
                bracket_type=g.bracket_type,
            )
        
        subevent_collector.run_constructors(graph, self._settings.critical_classes)
        durable_collector.run_constructors(graph, self._settings.critical_classes)

        l_to_l: defaultdict[LyricLevel, list[Lyric]] = defaultdict(list)
        for mung_lyric, subs in subevent_collector.score_objects_by(Lyric).items():
            try:
                if mung_lyric.class_name == C.Lyrics.LYRICS_UNISONO:
                    mung_lyric.data["text_transcription"] = self._settings.lyrics_unisono_character
                lyric = construct_lyric(mung_lyric, list(subs), graph)
                if lyric is not None:
                    l_to_l[lyrics_to_level[mung_lyric]].append(lyric)
                    _log_object_creation(lyric, mung_lyric)
            except AssertionError as ae:
                raise ValueError(f"Unable to construct {Lyric.__name__} from: {mung_lyric}") from ae
            

        for l_level, lyrics in l_to_l.items():
            l_level.lyrics = lyrics
            
        
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


        # TODO: make beam filtering better, union find does not work - removes overlaps but also duplicates
        connected_by_tremolo_beam: list[list[Subevent]] = [list(g) for g in subevent_collector.score_objects_by(TremoloBeam).values()]
        for mung_tremolo_beam, subs in subevent_collector.score_objects_by(TremoloBeam).items():
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
        for tb, counts in tremolo_counts.items():
            TremoloBeam(start=tb.start, stop=tb.stop, marks=counts)
            logger.info(f"Created tremolo beam with marks {subevent_collector}")
        
        IDClass.reset()
        
        return score
    