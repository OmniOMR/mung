import yaml
import unicodedata

from mung import Node, NotationGraph
from mung.constants import ClassNameConstants as C
from ..assets import VOLTA_MAPPING_PATH
from ...graph import Volta, ScoreMeasure
from ....logger import logger


SPECIAL_CHARACTERS = {" ", ".", ",", "[", "]", "(", ")", "/", "\\"}


def strip_accents(s):
    # Source - https://stackoverflow.com/a/518232
    # Posted by oefe, modified by community. See post 'Timeline' for change history
    # Retrieved 2026-06-26, License - CC BY-SA 3.0
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


def load_volta_text_mapping() -> dict[str, int]:
    with open(VOLTA_MAPPING_PATH, "r", encoding="utf8") as f:
        data = yaml.safe_load(f)

    normalized: dict[str, int] = {}

    for key, value in data.items():
        n_key = strip_accents(key.lower())
        normalized[n_key] = value

    return normalized


VOLTA_TEXT_MAPPING = load_volta_text_mapping()


def normalize_volta_text(volta_text: str) -> list[str]:
    output: list[str] = []
    current = ""
    for c in volta_text:
        if c not in SPECIAL_CHARACTERS:
            current += c

        elif len(current) > 0:
            output.append(current)
            current = ""

    if len(current) > 0:
        output.append(current)

    return output


def extract_numbers_from_volta_text(volta_text: str) -> set[int]:
    volta_text = strip_accents(volta_text.lower())

    normalized = normalize_volta_text(volta_text)

    numbers: set[int] = set()

    for t in normalized:
        n = VOLTA_TEXT_MAPPING.get(t)
        if n is not None:
            numbers.add(n)
            logger.debug(f"Matched '{t}' from '{volta_text}' to {n}")

    return numbers


def extract_numbers_from_multiple_volta_text_nodes(texts: list[Node]) -> list[int]:
    numbers: set[int] = set()

    for text in texts:
        transcript = text.text_transcription
        if transcript is None:
            logger.warning(f"No text transcription for {text}")
        else:
            numbers.update(extract_numbers_from_volta_text(transcript))

    return sorted(numbers)


def construct_volta(
    mung_volta: Node, score_measures: list[ScoreMeasure], graph: NotationGraph
) -> Volta:
    """
    Create with with volta text attached to the given volta.

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/ending/
    """

    assert len(score_measures) > 0
    texts = graph.children(mung_volta, class_filter=C.Repeat.VOLTA_TEXT)
    texts.sort(key=lambda t: t.left)

    numbers = extract_numbers_from_multiple_volta_text_nodes(texts)
    if len(numbers) == 0:
        numbers = [1]
    text = " ".join(
        t.text_transcription for t in texts if t.text_transcription is not None
    )
    score_measures.sort(key=lambda sm: sm.id)
    return Volta(
        start=score_measures[0],
        stop=score_measures[-1],
        text=text,
        numbers=numbers,
    )
