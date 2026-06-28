import xml.etree.ElementTree as ET
from xml.dom import minidom
from time import localtime, strftime
from pathlib import Path
from typing import Optional, Literal, Iterable
from collections import defaultdict

from mung2musicxml.score_graph.graph import Score
from mung.interpret import TimeSigStruct
from ...graph import *
from ...graph.interface import ScoreText
from ....logger import logger
from ..id_pool import IDPool
from .utils import _aggregate_mods
from ..export_engine import ExportEngine
from .settings import MusicXMLExportSettings


class MusicXML_ExportEngine(ExportEngine):
    """
    Graph to MusicXML 4.0 exporter.
    """

    def __init__(self, settings: Optional[MusicXMLExportSettings] = None) -> None:
        if settings is None:
            self.settings = MusicXMLExportSettings()
        else:
            self.settings = settings
        
        self._wedge_register = IDPool()
        self._slur_register = IDPool()
        self._part_group_register = IDPool()
    
    def export(self, score: Score) -> ET.Element:
        output = self.xml_Score(score)
        # self._reset()
        return output
    
    def export_to_file(self, score: Score, file_name: Path | str) -> None:
        """
        Converts `score` to MusicXML and saves it to `file_name`.

        :param score: Graph score
        :param file_name: Output file name
        :param indent: If `int`, the output text is indented with `indent` spaces,
            if `str`, the output text is indented using this string. 
        """
        if isinstance(file_name, str):
            file_name = Path(file_name)
        
        if not (file_name.name.endswith(".xml") or file_name.name.endswith(".musicxml")):
            logger.warning(f"Unknown file extension: '{file_name.name}'")
        
        s = self.xml_Score(score)
        with open(file_name, "w", encoding="utf8") as file:
            file.write(self._str_xml(s, indent=self._get_indent_str()))

        logger.info(f"Saved score to '{file_name.absolute()}'")
    
    def _get_indent_str(self) -> str:
        if isinstance(self.settings.indent, int):
            return self.settings.indent * " "
        return self.settings.indent
    
    def _reset(self) -> None:
        """
        Checks if ID pools are empty and resets them.
        """
        assert self._wedge_register.is_empty()
        assert self._slur_register.is_empty()
        assert self._part_group_register.is_empty()
        self._wedge_register.reset()
        self._slur_register.reset()
        self._part_group_register.reset()

    def create_forward(self, duration: int) -> ET.Element:
        """
        Creates a forward element with given duration.
        The duration has to be larger than 0.

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/forward/
        """
        assert duration > 0
        f = ET.Element("forward")
        ET.SubElement(f, "duration").text = str(duration)
        return f
    
    def create_backup(self, duration: int) -> ET.Element:
        """
        Creates a backup element with given duration.
        The duration has to be larger than 0.

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/backup/
        """
        assert duration > 0
        b = ET.Element("backup")
        ET.SubElement(b, "duration").text = str(duration)
        return b
    
    def xml_encoding_date(self) -> ET.Element:
        """
        Returns encoded current date.

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/encoding-date/
        """
        ed = ET.Element("encoding-date")
        ed.text = strftime("%Y-%m-%d", localtime())
        return ed

    def xml_credit(self) -> ET.Element:
        """
        Tags the exported MusicXML with the exporter's credit.

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/credit/
        """
        c = ET.Element("credit", {"page": "1"})
        ET.SubElement(c, "credit-type").text = "title"
        ET.SubElement(
            c, "credit-words",
            {"justify": "left", "valign": "top", "font-size": "12"}
        ).text = self.settings.credit.text
        return c

    def xml_Score(self, score: Score) -> ET.Element:
        """
        Main method, creates an element based on the given
        score ordered as a `score-partwise` score.

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/score-partwise/
        """
        self._log_middle_barline_warning(score)
        
        s = ET.Element("score-partwise", {"version": self.settings.musicxml_version})
        s.append(self.xml_Identification())

        if self.settings.credit.show:
            s.append(self.xml_credit())
        s.append(self.xml_part_list(score))

        for part in score.score_parts:
            s.append(self.xml_ScorePart(part))
        
        return s
    
    def _log_middle_barline_warning(self, score: Score) -> None:
        for sm in score.score_measures:
            for bar in sm.bars:
                if bar.location == LeftRightMiddleToken.MIDDLE:
                    logger.warning(f"{LeftRightMiddleToken.MIDDLE} not supported for {type(bar).__name__}")
        

    def _str_xml(self, root: ET.Element, indent: int | str = 2) -> str:
        """
        Converts given etree to a pretty string.

        https://stackoverflow.com/a/28814053
        """
        if isinstance(indent, int):
            indent = indent * " "
        xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent=indent)
        return xmlstr
    
    def xml_ScorePart(self, score_part: ScorePart) -> ET.Element:
        """
        Retrieves all measure inside `score_part` and outputs them
        according to their ids, starting from `1`.

        If a measure is missing, fills its place with an empty
        hidden measure.

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/part-partwise/
        """
        logger.info(f"Writing score part: {score_part.id}")
        sc = ET.Element("part", {"id": score_part.id})
        for id_ in range(1, score_part.score.max_measure_index + 1):
            measure = score_part.get_part_measure_by_id(id_)

            # measure is empty and hidden
            if measure is None:
                absolute_duration = score_part.divisions * score_part.score.get_system_measure_by_id(id_).fractional_duration
                assert absolute_duration.denominator == 1
                sc.append(self._xml_empty_hidden_measure(
                    number=id_,
                    new_system=score_part.score.get_system_measure_by_id(id_).is_new_system,
                    divisions=score_part.divisions,
                    staff_count=len(score_part.staffs),
                    absolute_duration=absolute_duration.denominator
                ))
                logger.warning(f"Created empty measure {id_} of {type(score_part).__name__} {score_part.id} ")
            
            # standard measure, visible
            else:
                sc.append(self.xml_Measure(measure))

        return sc

    def _xml_empty_hidden_measure(
            self,
            number: int,
            new_system: bool,
            absolute_duration: int,
            divisions: int,
            staff_count: int
        ) -> ET.Element:
        """
        Returns an empty hidden measure element.
        `divisions` and `staff_count` are only used,
        if the measure is the first measure in its part.

        :param number: Measure index
        :param new_system: If True, measure is on a new line
        :param absolute_duration: Measure with this duration will be created,
            the number has to be normalized using divisions before passed to the method
        :param divisions: MusicXML divisions
        :param staff_count: Number of staffs for this part
        :return: Empty hidden measure element
        """
        m = ET.Element("measure", {"number": str(number)})

        if new_system:
            ET.SubElement(m, "print", {"new-system": "yes"})
        
        # create attributes
        attributes = ET.Element("attributes")
        if number == 1:
            ET.SubElement(attributes, "divisions").text = str(divisions)
            ET.SubElement(attributes, "staves").text = str(staff_count)
        
        # hide measure
        ET.SubElement(attributes, "staff-details", {"print-object": "no"})
        m.append(attributes)
        
        m.append(self.create_forward(absolute_duration))
        return m
    
    def _xml_first_Measure_attributes(self, measure: PartMeasure, attributes: ET.Element) -> ET.Element:
        """
        Fills in attributes of the first measure of a part of a score.
        Given attributes are modified in place.

        :param measure: Current measure with number 1
        :param attributes: Element with name `attributes`
        :return: Modified `attributes`
        """
        def _key_at_measure_start(measure: PartMeasure) -> Optional[Key]:
            """
            Finds the first key that is at the start of a measure -
            has in-measure onset 0.
            """
            for m in measure.modifiers:
                if m.in_measure_fractional_onset == 0 and isinstance(m, Key):
                    return m
            return None
        
        def _time_sig_at_measure_start(measure: PartMeasure) -> Optional[TimeSignature]:
            """
            Finds the first key that is at the start of a measure -
            has in-measure onset 0.
            """
            for m in measure.modifiers:
                if m.in_measure_fractional_onset == 0 and isinstance(m, TimeSignature):
                    return m
            return None
        
        def _clefs_at_measure_start(measure: PartMeasure) -> list[Clef]:
            """
            Finds clefs that are at the start of a measure -
            have in-measure onset 0.
            """
            output: list[Clef] = []
            for m in measure.modifiers:
                if m.in_measure_fractional_onset == 0 and isinstance(m, Clef):
                    output.append(m)
            return output
        
        # divisions
        ET.SubElement(attributes, "divisions").text = str(measure.score_part.divisions)

        # key
        if (start_key := _key_at_measure_start(measure)) is not None:
            attributes.append(self.xml_Key(start_key))
        
        # time signature
        # TODO: default time signature?
        # TODO: measure should collect data starting from itself,
        # extending, until there is some time signature change
        if (start_time := _time_sig_at_measure_start(measure)) is not None:
            attributes.append(self.xml_TimeSignature(start_time))
        elif self.settings.time_sig.fallback_to_default_time_signature:
            attributes.append(self._xml_default_time_signature(measure.score_part.score))
        
        # at least one staff has to exist, but if the measure is empty,
        # it is not registered
        staff_count = max(1, len(measure.score_part.staffs))
        ET.SubElement(attributes, "staves").text = str(staff_count)

        # clefs
        clefs = _clefs_at_measure_start(measure)
        if len(clefs) > 0:
            for clef in clefs:
                attributes.append(self.xml_Clef(clef))

        elif self.settings.clefs.fallback_to_default_clefs:
            attributes.extend(self._xml_default_clefs(staff_count))

        return attributes

    def xml_Clef(self, clef: Clef) -> ET.Element:
        """
        Clef

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/clef/
        """
        c = ET.Element("clef", {"number": str(clef.number)})
        ET.SubElement(c, "sign").text = clef.sign
        ET.SubElement(c, "line").text = str(clef.line)
        return c
    
    def _xml_default_clefs(self, staff_line_count: int) -> list[ET.Element]:
        """
        Creates default clefs based on values defined in settings.
        """
        output = []
        for number in range(1, staff_line_count + 1):
            sign, line = self.settings.clefs.default_clefs_by_staff_index[number]
            c = ET.Element("clef", {"number": str(number), "print-object": YesNoToken.NO})
            ET.SubElement(c, "sign").text = sign
            ET.SubElement(c, "line").text = str(line)
            output.append(c)
        return output
    
    def xml_TimeSignature(self, time_sig: TimeSignature) -> ET.Element:
        """
        Time signature

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/time/
        """
        time = ET.Element("time", {
            "symbol": time_sig.symbol_type,
        })

        # add separator attribute for numeral time signatures
        if time_sig.symbol_type == TimeSymbolToken.NORMAL:
            time.attrib.update({
                "separator": time_sig.separator_type,
            })
        
        ET.SubElement(time, "beats").text = str(time_sig.numerator)
        ET.SubElement(time, "beat-type").text = str(time_sig.denominator)
        return time
    
    def xml_Key(self, key: Key) -> ET.Element:
        """
        Key

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/key/
        """
        xml_key = ET.Element("key")
        ET.SubElement(xml_key, "fifths").text = str(key.fifths)
        return xml_key

    def xml_TimeModification(self, time_modification: TimeModification) -> ET.Element:
        """
        Time modification

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/time-modification/
        """
        time_mod = ET.Element("time-modification")
        ET.SubElement(time_mod, "actual-notes").text = str(time_modification.actual)
        ET.SubElement(time_mod, "normal-notes").text = str(time_modification.normal)
        return time_mod
    
    def _xml_direction_base(self, placement: AboveBelowToken, staff_id: int) -> tuple[ET.Element, ET.Element]:
        dir = ET.Element("direction", {"placement": placement})
        ET.SubElement(dir, "staff").text = str(staff_id)
        dir_type = ET.SubElement(dir, "direction-type")
        return dir, dir_type
    
    def _xml_font_settings(self, obj: SceneObject) -> dict[str, str]:
        """
        Finds font definition for a given object
        inside setting and returns it formatted
        as a dictionary with MusicXML keys and values.

        Returns an empty dictionary if not font definition
        is found.
        """
        fs = self.settings.text_settings.get(type(obj))
        if fs is None:
            return {}
        else:
            output: dict[str, str]= {}
            for key, value in vars(fs).items():
                key: str
                if key.startswith("font") and value is not None:
                    key = key.replace("_", "-")
                    output[key] = str(value)
            return output

    def xml_Dynamics(self, subevent: Subevent) -> list[ET.Element]:
        """
        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/dynamics/
        """
        output = []
        for dynamic in subevent.dynamics:
            dir, dir_type = self._xml_direction_base(dynamic.placement, dynamic.staff.id)
            dyn = ET.SubElement(dir_type, "dynamics")
            dyn_impl = ET.SubElement(dyn, str(dynamic.type_))
            if dynamic.type_ == DynamicsTypeToken.OTHER_DYNAMICS:
                assert dyn_impl is not None
                dyn_impl.text = dynamic.text
            output.append(dir)
        return output
    
    def xml_ScoreText(self, subevent: Subevent, texts: Iterable[ScoreText]) -> list[ET.Element]:
        """
        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/words/
        """
        output = []
        for text in texts:
            if text.is_start(subevent):
                dir, dir_type = self._xml_direction_base(text.placement, text.staff.id)
                ET.SubElement(dir_type, "words", self._xml_font_settings(text)).text = text.text
                output.append(dir)
        return output
    
    def xml_Subevent(self, subevent: Subevent) -> list[ET.Element]:
        """
        Subevent does not have a direct MusicXML equivalent.
        It represents a group of durables that have the same onset
        and are played by the same voice.

        List of `note` elements is outputted along with
        possible other symbols, like wedges, slurs, ties, ...
        """
        output = []
        
        output.extend(self.xml_Wedge(subevent, "start"))
        output.extend(self.xml_Dynamics(subevent))
        output.extend(self.xml_ScoreText(subevent, subevent.dynamics_texts))
        output.extend(self.xml_ScoreText(subevent, subevent.tempos))
        output.extend(self.xml_ScoreText(subevent, subevent.interpretation_texts))

        if isinstance(subevent, Chord):
            for note in subevent.notes:
                for grace in note.grace_notes:
                    output.append(self.xml_GraceNote(grace))
                output.append(self.xml_Note(note))
        elif isinstance(subevent, Rest):
            output += [self.xml_Rest(subevent)]
        elif isinstance(subevent, RepeatBar):
            return [self.create_forward(subevent.duration)]
        
        output.extend(self.xml_Wedge(subevent, "stop"))

        return output
    
    def xml_Note(self, note: Note) -> ET.Element:
        """
        `Note` does not correspond directly to MusicXML `note`.

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/note/
        """
        n = ET.Element("note")
        if note.is_chord_continuation:
            ET.SubElement(n, "chord")

        n.append(self.xml_Pitch(note.pitch))

        ET.SubElement(n, "duration").text = str(note.duration)
        for tie in self.xml_Ties(note, notations=False):
            if tie.get("type") != TiedTypeToken.LET_RING:
                n.append(tie)

        ET.SubElement(n, "voice").text = str(note.voice.id)
        ET.SubElement(n, "type").text = note.type_
        
        for _ in note.dots:
            ET.SubElement(n, "dot")
        
        accidental = note.accidental
        if accidental is not None:
            ET.SubElement(n, "accidental").text = accidental.type_
        
        if note.tuplet is not None:
            n.append(self.xml_TimeModification(note.tuplet.time_modification))
        
        if note.tremolo_beam is not None:
            n.append(self.xml_TimeModification(note.tremolo_beam.time_modification))
        
        if note.has_stem:
            ET.SubElement(n, "stem").text = note.chord_stem_orientation

        ET.SubElement(n, "staff").text = str(note.staff.id)

        if note.is_first_in_chord:
            for beam in self.xml_Beams(note):
                n.append(beam)
        
        notations = self.xml_notations(note)
        if notations is not None:
            n.append(notations)

        if not note.is_chord_continuation:
            lyrics = self.xml_Lyrics(note)
            n.extend(lyrics)
        
        return n
        
    def xml_Rest(self, rest: Rest) -> ET.Element:
        """
        Rest

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/note/
        """
        def _rest_is_measure_lasting(rest: Rest) -> bool:
            """
            Only rest with that one in its measure.
            """
            if rest.type_.can_be_measure_lasting():
                # on the same staff in the same measure
                i = set.intersection(set(rest.staff.durables), rest.part_measure.all_durables)
                # same voice, care only about other rests
                i = [d for d in i if (isinstance(d, Rest) and d.voice == rest.voice)]
                return len(i) == 1
            return False
        
        r = ET.Element("note")

        if _rest_is_measure_lasting(rest):
            ET.SubElement(r, "rest", {"measure": "yes"})
        else:
            ET.SubElement(r, "rest")
        
        ET.SubElement(r, "duration").text = str(rest.duration)
        
        for tie in self.xml_Ties(rest, notations=False):
            if tie.get("type") != TiedTypeToken.LET_RING:
                r.append(tie)

        ET.SubElement(r, "voice").text = str(rest.voice.id)
        ET.SubElement(r, "type").text = rest.type_
        
        for _ in rest.dots:
            ET.SubElement(r, "dot")
        
        if rest.tuplet is not None:
            r.append(self.xml_TimeModification(rest.tuplet.time_modification))
        
        ET.SubElement(r, "staff").text = str(rest.staff.id)
        
        for beam in self.xml_Beams(rest):
            r.append(beam)
        
        notations = self.xml_notations(rest)
        if notations is not None:
            r.append(notations)

        return r
    
    def xml_Ties(self, durable: Durable, notations: bool) -> list[ET.Element]:
        """
        Ties have to be declared both inside the `note` itself
        and inside its subelement `notations`. The only difference
        being the `tie` / `tied` tag.

        The method automatically sorts created ties,
        so that all concerned ties are closed before others
        are opened.

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/tie/

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/tied/

        :param durable: Durable to which the ties are connected
        :param notations: Change between usage inside
            the `note` and `notations` element
        """
        if notations:
            name = "tied"
        else:
            name = "tie"
        
        xml_ties: list[tuple[ET.Element, TiedTypeToken]] = []
        for tie in durable.ties:
            if tie.is_let_ring:
                xml_ties.append((ET.Element(
                    name, {"type": TiedTypeToken.LET_RING}
                ), TiedTypeToken.LET_RING))
            
            elif tie.is_start(durable):
                attrs: dict[str, str] = {"type": TiedTypeToken.START}
                if notations:
                    attrs["placement"] = tie.placement
                
                xml_ties.append((ET.Element(
                    name, attrs
                ), TiedTypeToken.START))
            
            elif tie.is_stop(durable):
                xml_ties.append((ET.Element(
                    name, {"type": TiedTypeToken.STOP}
                ), TiedTypeToken.STOP))
            
            else:
                raise ValueError
        
        # first, stop ties, then start them
        xml_ties.sort(key=lambda t: t[1], reverse=True)
        return [t[0] for t in xml_ties]

    def xml_Lyrics(self, durable: Durable) -> list[ET.Element]:
        output = []
        for lyric in sorted(durable.lyrics, key=lambda l: l.lyric_level.number):
            if lyric.is_start(durable.subevent):
                l = ET.Element("lyric", {"number": str(lyric.lyric_level.number)})
                ET.SubElement(l, "syllabic").text = lyric.syllabic_type
                l_text = lyric.clear_text
                if lyric.verse_number is not None:
                    l_text = lyric.verse_number.text + " " + l_text
                ET.SubElement(l, "text").text = l_text
                if lyric.is_extend:
                    if lyric.has_start_and_stop_set:
                        ET.SubElement(l, "extend", {"type": StartStopContinueToken.START})
                    else:
                        ET.SubElement(l, "extend")
                output.append(l)
            elif lyric.is_stop(durable.subevent) and lyric.is_extend:
                l = ET.Element("lyric", {"number": str(lyric.lyric_level.number)})
                ET.SubElement(l, "extend", {"type": StartStopContinueToken.STOP})
                
                output.append(l)

        return output

    
    def xml_Tuplet(self, durable: Durable) -> Optional[ET.Element]:
        """
        Creates a single tuplet for given tuplet and durable.
        Modifies `notations` in place.
        """
        if self._durable_is_chord_continuation(durable):
            return None
        
        tuplet = durable.tuplet
        if tuplet is not None:
            if tuplet.is_start(durable.subevent):
                attrs: dict[str, str] = {
                    "type": StartStopContinueToken.START,
                    "show-number": tuplet.show_number,
                    "bracket": tuplet.bracket,
                }

                if tuplet.placement is not None:
                    attrs["placement"] = tuplet.placement
                
                return ET.Element("tuplet", attrs)
                
            elif tuplet.is_stop(durable.subevent):
                return ET.Element("tuplet", {
                    "type": StartStopContinueToken.STOP,
                })
        
        return None
    
    def xml_Slurs(self, durable: Durable) -> list[ET.Element]:
        """
        Creates slurs.
        The methods checks, if retrieved slurs are valid.
        We consider valid MusicXML slur to have start and stop durables
        both of which are not a `RepeatBar`
        (as repeat bars are an attribute and cannot be a start/stop).

        `continue` durables are not supported.

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/slur/
        """

        def _is_valid_musicxml_slur(slur: Slur) -> bool:
            """
            Slur has to have start and end. These durables cannot be Repeat Bars.
            """
            return (
                slur.start is not None
                and slur.stop is not None
                and not isinstance(slur.start, RepeatBar)
                and not isinstance(slur.stop, RepeatBar)
            )
        
        def _get_sorted_slurs(durable: Durable) -> list[tuple[StartStopContinueToken, Slur]]:
            """
            Sorts slurs, so that stops are processed first.
            """
            stops: list[tuple[StartStopContinueToken, Slur]] = []
            starts: list[tuple[StartStopContinueToken, Slur]] = []
            for slur in durable.slurs:
                if slur.is_start(durable.subevent):
                    starts.append((StartStopContinueToken.START, slur))
                elif slur.is_stop(durable.subevent):
                    stops.append((StartStopContinueToken.STOP, slur))
            
            return stops + starts
            
        
        output = []
        for start_stop, slur in _get_sorted_slurs(durable):
            # slurs are only added to first note in chord
            if self._durable_is_chord_continuation(durable):
                continue

            if not _is_valid_musicxml_slur(slur):
                continue
            
            if start_stop == StartStopContinueToken.START:
                id_ = self._slur_register.ask_id_start(slur)
                output.append(ET.Element(
                    "slur", {
                        "type": StartStopContinueToken.START,
                        "placement": slur.placement,
                        "number": str(id_),
                    }
                ))
            elif start_stop == StartStopContinueToken.STOP:
                id_ = self._slur_register.ask_id_stop(slur)
                output.append(ET.Element(
                    "slur", {
                        "type": StartStopContinueToken.STOP,
                        "number": str(id_),
                    }
                ))
        
        return output
    
    def _durable_is_chord_continuation(self, durable: Durable) -> bool:
        """
        Returns True, if `durable` is a chord continuation.
        """
        return isinstance(durable, Note) and durable.is_chord_continuation
    

    def xml_TremoloBeam(self, durable: Durable) -> ET.Element:
        beam = durable.tremolo_beam
        assert beam is not None
        
        if beam.is_start(durable.subevent):
            b = ET.Element("tremolo", {"type": TremoloType.START})
        elif beam.is_stop(durable.subevent):
            b = ET.Element("tremolo", {"type": TremoloType.STOP})
        else:
            raise ValueError
        
        b.text = str(beam.marks)
        return b

    def xml_TremoloSingle(self, durable: Durable) -> ET.Element:
        single = durable.tremolo_single
        assert single is not None
        s = ET.Element("tremolo", {"type": TremoloType.SINGLE})
        s.text = str(single.marks)
        return s

    def xml_ornaments(self, durable: Durable) -> Optional[ET.Element]:
        ornaments = ET.Element("ornaments")
        
        # write tremolo beams only to first note of a chord
        if not self._durable_is_chord_continuation(durable):
            if durable.tremolo_beam is not None:
                ornaments.append(self.xml_TremoloBeam(durable))
            if durable.tremolo_single is not None:
                ornaments.append(self.xml_TremoloSingle(durable))
        
        if len(ornaments) > 0:
            return ornaments
        
        return None

    def xml_Fermata(self, durable: Durable) -> list[ET.Element]:
        used_types: set[FermataOrientationToken] = set()
        output = []
        for fermata in durable.fermatas:
            if fermata.type_ not in used_types:
                output.append(ET.Element("fermata", {"type": str(fermata.type_)}))
                used_types.add(fermata.type_)

        return output
    
    def xml_notations(self, durable: Durable) -> Optional[ET.Element]:
        """
        Fills in `note`'s `notations` element with slurs, ties, ...

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/notations/
        """
        notations = ET.Element("notations")
        is_chord_continuation = self._durable_is_chord_continuation(durable)        

        
        if not is_chord_continuation:
            if (xml_tuplet := self.xml_Tuplet(durable)) is not None:
                notations.append(xml_tuplet)
            
            notations.extend(self.xml_Slurs(durable))

        notations.extend(self.xml_Ties(durable, notations=True))

        if (xml_ornaments := self.xml_ornaments(durable)) is not None:
            notations.append(xml_ornaments)

        if not is_chord_continuation:
            if (xml_artic := self.xml_Articulations(durable)) is not None:
                notations.append(xml_artic)
        
        notations.extend(self.xml_Fermata(durable))

        if len(notations) > 0:
            return notations
        
        return None

    def xml_Articulations(self, durable: Durable) -> Optional[ET.Element]:
        articulations = ET.Element("articulations")
        for artic in durable.articulations:
            ET.SubElement(articulations, artic.type_, {"placement": artic.placement})
        if len(articulations) > 0:
            return articulations
        return None
    
    def xml_Wedge(self, subevent: Subevent, pass_name: Literal["start", "stop"]) -> list[ET.Element]:
        """
        Creates wedges. Two pass options: `start`, `stop`.
        When the `start` pass is active, only wedge starts are processed.
        Vice versa for the second option.

        Currently does not support `continue` option for wedges.
        """
        assert pass_name in ["start", "stop"]
        
        output = []
        wedges = set(subevent.wedges)

        def _create_wedge(id_: int, wedge: Wedge) -> ET.Element:
            directions = ET.Element("direction", {"placement": wedge.placement})
            dtype = ET.SubElement(directions, "direction-type")
            ET.SubElement(directions, "staff").text = str(wedge.staff_id)
            ET.SubElement(dtype, "wedge", {"type": wedge.type_, "number": str(id_)})
            return directions
        
        def _close_wedge(id_: int, wedge: Wedge) -> ET.Element:
            directions = ET.Element("direction", {"placement": wedge.placement})
            dtype = ET.SubElement(directions, "direction-type")
            ET.SubElement(dtype, "wedge", {"type": WedgeDirectionType.STOP, "number": str(id_)})
            return directions

        for wedge in wedges:
            if wedge.is_start(subevent) and pass_name == "start":
                id_ = self._wedge_register.ask_id_start(wedge)
                output.append(_create_wedge(id_, wedge))

            elif wedge.is_stop(subevent) and pass_name == "stop":
                id_ = self._wedge_register.ask_id_stop(wedge)
                logger.debug(f"Closing wedge {id_}")
                output.append(_close_wedge(id_, wedge))

        return output
    
    def xml_Pitch(self, pitch: Pitch) -> ET.Element:
        """
        Pitch

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/pitch/
        """
        p = ET.Element("pitch")
        ET.SubElement(p, "step").text = pitch.step
        ET.SubElement(p, "octave").text = str(pitch.octave.value)
        if pitch.alter != 0:
            ET.SubElement(p, "alter").text = str(pitch.alter.value)
        return p
    
    def xml_GraceNote(self, grace: GraceNote) -> ET.Element:
        """
        Grace note

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/grace/
        """
        # TODO: add support for dots, accidentals and beams

        n = ET.Element("note")
        ET.SubElement(n, "grace")
        n.append(self.xml_Pitch(grace.pitch))

        ET.SubElement(n, "voice").text = str(grace.voice.id)
        ET.SubElement(n, "type").text = grace.type_
        
        ET.SubElement(n, "stem").text = grace.stem_orientation
        
        for beam in self.xml_Beams(grace):
            n.append(beam)

        ET.SubElement(n, "staff").text = str(grace.staff.id)

        return n
    
    def xml_Beams(self, note_like: Durable | GraceNote) -> list[ET.Element]:
        """
        Creates beams for durables and grace notes.

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/beam/
        """
        beams = note_like.beams
        beams.sort(key=lambda b: b.number)
        output = []
        for beam in beams:
            b = ET.Element("beam", {"number": beam.number})
            if isinstance(note_like, Durable):
                assert isinstance(beam, DurableBeam)
                b.text = beam.beam_value(note_like.subevent)
            else:
                assert isinstance(beam, GraceNoteBeam)
                b.text = beam.beam_value(note_like)
            output.append(b)
        return output
    
    def _resolve_repeat_repeat(self, measure: PartMeasure) -> list[ET.Element]:
        """
        If previous measure is a full repeat, closes it.
        If current measure is a full repeat, opens it.

        Returns list of subelements of `attributes`, if any full measure repeats are found.
        """

        def _repeat_alone_on_staff_in_measure(repeat: RepeatBar) -> bool:
            i = set.intersection(set(repeat.staff.durables), repeat.part_measure.all_durables)
            return len(i) == 1
        
        previous = measure.get_previous()
        frs: list[ET.Element] = []
        
        # if previous.has_full_repeat:
        if previous is not None and previous.has_full_repeat:
            for repeat in (r for r in previous.subevents if isinstance(r, RepeatBar)):
                if _repeat_alone_on_staff_in_measure(repeat):
                    ms = ET.Element("measure-style", {"number": str(repeat.number)})
                    ET.SubElement(ms, "measure-repeat", {"type": StartStopContinueToken.STOP})
                    frs.append(ms)
        
        # if measure.has_full_repeat:
        if measure.has_full_repeat:
            for repeat in (r for r in measure.subevents if isinstance(r, RepeatBar)):
                if _repeat_alone_on_staff_in_measure(repeat):
                    ms = ET.Element("measure-style", {"number": str(repeat.number)})
                    ET.SubElement(ms, "measure-repeat", {"type": StartStopContinueToken.START}).text = "1"
                    frs.append(ms)
        
        return frs
    
    def _is_first_voice(self, voice_id: int) -> bool:
        """
        Returns true, if the given voice id is a first voice
        in its respective staff.
        """
        return voice_id in self.settings.first_voices
    
    def _normalize_repeat_style_mss4(self, repeat: RepeatBarline) -> BarStyleToken:
        if repeat.bf == BackwardForwardToken.FORWARD:
            return BarStyleToken.HEAVY_LIGHT
        return BarStyleToken.LIGHT_HEAVY
      
    def xml_Barlines(self, measure: PartMeasure, location: LeftRightMiddleToken) -> list[ET.Element]:
        def _gen_bar_style(
                bar: Barline
            ) -> ET.Element:
            style = bar.style
            if isinstance(bar, RepeatBarline) and self.settings.use_mss4_compatible_repeat_barline_style:
                style = self._normalize_repeat_style_mss4(bar)
            
            barline = ET.Element("barline", {"location": bar.location})
            ET.SubElement(barline, "bar-style").text = style
            return barline

        def _add_bar(
                bar: Barline
            ) -> ET.Element | None:
            if isinstance(bar, RepeatBarline):
                barline = _gen_bar_style(bar)
                repeat = ET.SubElement(
                    barline,
                    "repeat",
                    {
                        "direction": bar.bf,
                        "winged": bar.winged,
                    }
                )
                return repeat
        
            if bar.style != BarStyleToken.default():
                barline = ET.Element("barline", {"location": bar.location})
                ET.SubElement(barline, "bar-style").text = bar.style
                return barline
        
        output: list[ET.Element] = []
        sm = measure.system_measure
        for bar in sm.bars:
            if bar.location == location:
                b = _add_bar(bar)
                if b is not None:
                    output.append(b)
        
        if measure.score_part.is_first:
                output.extend(self.xml_Voltas(sm, location))
        
        return output
    
    def xml_Voltas(self, score_measure: ScoreMeasure, location: LeftRightMiddleToken) -> list[ET.Element]:
        output: list[ET.Element] = []
        
        for volta in score_measure.voltas:
            start_stop: StartStopDiscontinueToken | None = None
            if volta.is_start(score_measure) and location == LeftRightMiddleToken.LEFT:
                start_stop = StartStopDiscontinueToken.START
            elif volta.is_stop(score_measure) and location == LeftRightMiddleToken.RIGHT:
                start_stop = StartStopDiscontinueToken.STOP
            
            if start_stop is not None:
                if len(volta.numbers) == 0:
                    number = "1"
                else:
                    number = ",".join(str(n) for n in volta.numbers)
                
                barline = ET.Element("barline", {"location": location})
                ET.SubElement(
                    barline,
                    "ending",
                    {"number": number, "type": start_stop}
                ).text = volta.text
                
                output.append(barline)
        
        return output                
        
    def xml_right_Barlines(self, measure: PartMeasure) -> list[ET.Element]:
        return self.xml_Barlines(measure, LeftRightMiddleToken.RIGHT)

    def xml_left_Barlines(self, measure: PartMeasure) -> list[ET.Element]:
        return self.xml_Barlines(measure, LeftRightMiddleToken.LEFT)        
    
    def _get_subevent_and_modifiers(self, measure: PartMeasure, subevents: list[Subevent], voice_id: int) -> list[InMeasureModifier | Subevent]:
        """
        Returns a list of symbols that will be written in to `measure`.

        Modifiers (key, time signature, clef, ...) are outputted within the first voice
        (first voices, both top and bottom staff in grand staff have a first voice).

        In measure, all modifiers with onset 0 have already been outputted in its
        attributes that define many other features of a part the measure belongs to.

        All of the modifiers are returned when the method is asked for a `voice_id`
        equal to 1, except for clefs that belong to the bottom staff, they are returned
        with `voice_id` equal to 5.
        """
        # modifiers (key, time signatures, clefs, ...) are outputted in the first voice
        # - if measure is first, modifiers with onset 0 have already been written
        # - clefs are staff-dependant
        if self._is_first_voice(voice_id):
            # filter out mods that have already been outputted
            mods = [m for m in measure.modifiers if not (measure.is_first and m.in_measure_fractional_onset == 0)]
            # if second staff is being written, take only staff-dependant symbols (clefs)
            if voice_id == 1:
                mods = [m for m in mods if not (isinstance(m, Clef) and m.number == 2)]
            else:
                mods = [m for m in mods if isinstance(m, Clef) and m.number == 2]
            
            subevents_and_mods: list[InMeasureModifier | Subevent] = sorted(subevents + mods, key=lambda sm: (sm.in_measure_fractional_onset, not isinstance(sm, InMeasureModifier)))
        # standard voice (without modifiers)
        else:
            subevents_and_mods: list[InMeasureModifier | Subevent] = sorted(subevents, key=lambda s: s.in_measure_fractional_onset)
        
        return subevents_and_mods
    
    def _xml_in_measure_modifiers(self, mods: list[InMeasureModifier]) -> ET.Element:
        assert all(m.in_measure_onset == mods[0].in_measure_onset for m in mods)
        attributes = ET.Element("attributes")
        for mod in mods:
            if isinstance(mod, Key):
                attributes.append(self.xml_Key(mod))
            elif isinstance(mod, Clef):
                attributes.append(self.xml_Clef(mod))
            elif isinstance(mod, TimeSignature):
                attributes.append(self.xml_TimeSignature(mod))
            else:
                raise ValueError
            
        return attributes
    
    def _add_empty_measure(self, m_element: ET.Element, measure: PartMeasure) -> ET.Element:
        ed = measure.system_measure.get_expected_duration_for_part_measure(measure)
        if ed == 0:
            ts = self._get_most_common_time_signature(measure.score_part.score)
            ed = (ts * measure.score_part.divisions).numerator
        
        m_element.append(self.create_forward(ed))
        return m_element
    
    def xml_Measure(self, measure: PartMeasure) -> ET.Element:
        m = ET.Element("measure", {"number": str(measure.id)})

        if measure.is_new_system:
            ET.SubElement(m, "print", {"new-system": "yes"})
        
        # Create attributes for the first measure:
        #   MusicXML requires a specific ordering of these attributes,
        #   that's why the first measure is processed like this
        #   and why the modifiers are not left for later processing
        attributes = ET.Element("attributes")
        if measure.is_first:
            logger.debug("creating first measure attributes")
            attributes = self._xml_first_Measure_attributes(measure, attributes)

        # resolve repeat one bars
        full_repeat_attr = self._resolve_repeat_repeat(measure)
        
        if measure.is_full_repeat:
            assert full_repeat_attr is not None
            logger.debug(f"{measure.score_part.name} {measure.id} measure is full repeat")
            attributes.extend(full_repeat_attr)
            m.append(attributes)
            m.append(self.create_forward(
                measure.system_measure.get_expected_duration_for_part_measure(measure)
            ))
            return m
        
        if full_repeat_attr is not None:
            attributes.extend(full_repeat_attr)

        if len(attributes) > 0:
            m.append(attributes)
        
        m.extend(self.xml_left_Barlines(measure))

        # empty measure
        if len(measure.subevents) == 0:
            m = self._add_empty_measure(m, measure)
            m.extend(self.xml_right_Barlines(measure))
            return m
        
        subevents_by_voice: defaultdict[int, list[Subevent]] = defaultdict(list)
        for subevent in measure.subevents:
            subevents_by_voice[subevent.voice.id].append(subevent)
        
        retrieved_voice_ids = sorted(subevents_by_voice.keys())
        last_voice_id = retrieved_voice_ids[-1]

        # relative start of every measure is at 0 (even if the measure is not first)
        expected_duration = measure.system_measure.get_expected_duration_for_part_measure(measure)
        
        logger.debug(f"- Writing measure {measure.id}")
        logger.debug(f"Expected measure duration: {expected_duration}")
        
        # buffer to handle potential crashes
        m_buffer: list[ET.Element] = []

        try:
            for voice_id in retrieved_voice_ids:
                logger.debug(f"-- Writing voice {voice_id} of {retrieved_voice_ids}")
                subevents = subevents_by_voice[voice_id]

                subevents_and_mods = self._get_subevent_and_modifiers(measure, subevents, voice_id)
                current_onset = 0
                
                for subevent_or_mods in _aggregate_mods(subevents_and_mods):
                    logger.debug(f"Current onset {current_onset}")
                    logger.debug(f"Writing {subevent_or_mods}")

                    
                    # AGGREGATED MODIFIERS 
                    if isinstance(subevent_or_mods, list):

                        modifiers: list[InMeasureModifier] = subevent_or_mods
                        attributes = self._xml_in_measure_modifiers(modifiers)
                        
                        # shift modifiers in time, if needed
                        mod_shift = modifiers[0].in_measure_onset - current_onset
                        if mod_shift > 0:
                            m_buffer.append(self.create_forward(mod_shift))
                            m_buffer.append(attributes)
                            m_buffer.append(self.create_backup(mod_shift))
                        elif mod_shift < 0:
                            m_buffer.append(self.create_backup(mod_shift))
                            m_buffer.append(attributes)
                            m_buffer.append(self.create_forward(mod_shift))
                        else:
                            m_buffer.append(attributes)
                        
                        logger.debug(f"Wrote {modifiers}")
                    
                    # SUBEVENT
                    else:
                        subevent: Subevent = subevent_or_mods

                        if isinstance(subevent, RepeatBar):
                            logger.warning(f"Skipped {RepeatBar.__name__} in {measure.score_part.name} {measure.id}, it is not a full repeat")
                            continue

                        assert subevent.in_measure_onset >= current_onset, f"{subevent.in_measure_onset}, {current_onset}"
                        # there exists a space between last and current subevent
                        if current_onset < subevent.in_measure_onset:
                            logger.warning(f"Filling in gap, {current_onset=}, {subevent.in_measure_onset=}")
                            m_buffer.append(self.create_forward(subevent.in_measure_onset - current_onset))
                            current_onset = subevent.in_measure_onset
                        
                        assert subevent.in_measure_onset == current_onset
                        
                        # write subevent to output
                        for d in self.xml_Subevent(subevent):
                            m_buffer.append(d)
                        
                        # advance time by subevent duration
                        current_onset += subevent.duration
                    
                # end of measure, make sure, that written time matches expected end onset
                if current_onset < expected_duration:
                    logger.warning(f"Filling in gap at the end of measure {measure.id}, from {current_onset=} to {expected_duration=}")
                    m_buffer.append(self.create_forward(expected_duration - current_onset))
                    current_onset += expected_duration - current_onset
                
                assert current_onset == expected_duration

                # return to the start of measure for next voice (if voice is not max voice)
                if voice_id != last_voice_id:
                    m_buffer.append(self.create_backup(expected_duration))
        
        except Exception as e:
            msg = (
                f"Unable to write {PartMeasure.__name__} {measure.id}"
                f" of {ScorePart.__name__} {measure.score_part.id}"
            )
            if self.settings.error_handling.skip_broken_measure:
                logger.critical(f"Measure written as empty")
                logger.warning(msg, exc_info=True)
                m = self._add_empty_measure(m, measure)
                return m
            else:
                raise ValueError(msg) from e
        
        m.extend(m_buffer)
        m.extend(self.xml_right_Barlines(measure))

        return m
    
    def _get_most_common_time_signature(self, score: Score) -> TimeSigStruct:
        """
        Computes most common time signature in `Score`.
        """
        mcts = score.get_most_common_time_signature(self.settings.time_sig.canonical_time_sigs)
        if mcts is None:
            mcts = self.settings.time_sig.default_time_signature
        return mcts

    def _xml_default_time_signature(self, score: Score) -> ET.Element:
        """
        Returns a default time signature element based on
        settings.
        """
        mcts = self._get_most_common_time_signature(score)
        time = ET.Element("time", {"print-object": YesNoToken.NO})
        ET.SubElement(time, "beats").text = str(mcts.numerator)
        ET.SubElement(time, "beat-type").text = str(mcts.denominator)
        return time

    def xml_part_list(self, score: Score) -> ET.Element:
        """
        Returns a list of score parts - basic information
        about each of the score's instruments.

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/part-list/
        """
        # orders groups from smallest to largest
        # (group id affects ordering in MSS4 render)
        score_groups: set[PartGroup] = set()
        for part in score.score_parts:
            score_groups.update(part.part_groups)
        
        for group in sorted(score_groups, key=lambda g: -len(g.parts)):
            self._part_group_register.ask_id_start(group)

        # create instrument group structure
        pl = ET.Element("part-list")
        for part in score.score_parts:
            pl.extend(self.xml_part_list_element(part))
        return pl
    
    def xml_PartGroup(self, part_group: PartGroup, number: int, start_stop: StartStopContinueToken) -> ET.Element:
        pg = ET.Element("part-group", {"number": str(number), "type": start_stop})
        if start_stop == StartStopContinueToken.START:
            ET.SubElement(pg, "group-symbol").text = part_group.bracket_type
            ET.SubElement(pg, "group-barline").text = part_group.barline_type
        return pg

    def xml_part_list_element(self, score_part: ScorePart) -> list[ET.Element]:
        """
        Returns a single instrument element for a `score-partwise`
        and any part group elements that start or stop at this part.

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/part-list/
        """
        group_starts: list[ET.Element] = []
        group_ends: list[ET.Element] = []

        for group in score_part.part_groups:
            if group.is_start(score_part):
                number = self._part_group_register.ask_id_start(group)
                group_starts.append(self.xml_PartGroup(group, number, StartStopContinueToken.START))
            if group.is_stop(score_part):
                number = self._part_group_register.ask_id_stop(group)
                group_ends.append(self.xml_PartGroup(group, number, StartStopContinueToken.STOP))
                
        sp = ET.Element("score-part", {"id": score_part.id})
        ET.SubElement(sp, "part-name").text = score_part.name
        
        return group_starts + [sp] + group_ends
    
    def xml_Identification(self) -> ET.Element:
        """
        Creates a score metadata element.

        https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/identification/
        """
        ide = ET.Element("identification")
        enc = ET.SubElement(ide, "encoding")
        ET.SubElement(enc, "software").text = self.settings.software_name
        enc.append(self.xml_encoding_date())
        for data in [
            {"element": "accidental", "type": "yes"},
            {"element": "beam", "type": "yes"},
            {"element": "print", "attribute": "new-page", "type": "yes", "value": "yes"},
            {"element": "print", "attribute": "new-system", "type": "yes", "value": "yes"},
            {"element": "stem", "type": "yes"},
        ]:
            ET.SubElement(enc, "supports", data)
        return ide
