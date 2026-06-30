from typing import Optional
from mung import Node, NotationGraph
from mung.constants import ClassNameConstants as C

from ...graph import Lyric, VerseNumber, Subevent
from ....logger import logger
from .collector import needs_graph


@needs_graph
def construct_lyric(
        mung_lyric: Node,
        subs: list[Subevent],
        graph: NotationGraph
) -> Optional[Lyric]:
    """
    Constructs Lyric scene object along with its VerseNumber,
    if it has one. If `mung_lyric` is missing text transcription
    return None.
    """
    if mung_lyric.text_transcription is None:
        logger.warning(f"No text transcription provided for {mung_lyric}")
        return None
    
    # subs = _filter_lyrics_subevents(subs)
    subs.sort(key=lambda s: s.global_fractional_onset)
    # solve multiple links from subevents with the same onset
    # (choose one with the lowest voice)
    if subs[0].global_fractional_onset == subs[-1].global_fractional_onset:
        subs = [min(subs, key=lambda s: s.voice.id)]
    
    if len(subs) == 1:
        lyric = Lyric(start=subs[0], text=mung_lyric.text_transcription)
    else:
        lyric = Lyric(start=subs[0], stop=subs[-1], text=mung_lyric.text_transcription)

    # resolve verse number
    verse_numbers = graph.children(mung_lyric, class_filter=C.Lyrics.VERSE_NUMBER)
    if len(verse_numbers) > 1:
        logger.warning(f"Found multiple verse numbers for {mung_lyric}, choosing the first one")
    if len(verse_numbers) > 0:
        verse_number = verse_numbers[0]
        if verse_number.text_transcription is None:
            logger.warning(f"No text transcription provided for {mung_lyric}")
        else:
            VerseNumber(lyric, verse_number.text_transcription)

    return lyric


def _filter_lyrics_subevents(subs: list[Subevent]) -> list[Subevent]:
    # f_subs = [s for s in subs if s.voice.id in FIRST_VOICES]
    # todo find the lowest voice with maximal number of subevents
    f_subs = list(subs)
    if len(f_subs) == 0:
        return []
    
    assert all(s.voice.id == f_subs[0].voice.id for s in f_subs)

    return f_subs