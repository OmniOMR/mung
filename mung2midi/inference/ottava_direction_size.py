from typing import Optional

from mung import Node
from mung.graph import infer_vertical_object_placement_relative_to_notes
from .pitch import (
    OttavaConstants,
    OTTAVA_SIZE_DEFAULT,
    OTTAVA_SIZE_TO_OCTAVE_MAPPING,
)
from ..logger import logger


def _interpret_ottava_size_from_text(text: str) -> int:
    """
    Extracts ottava size from a given text.

    Returns 8, 15 or 21. 8 is default,
    if no value is found.
    """

    import re

    nums = [int(x) for x in re.findall(r"\d+", text)]
    size = max(nums, default=None)
    if size not in OTTAVA_SIZE_TO_OCTAVE_MAPPING.keys():
        logger.warning(
            f"Unable to convert ottava text '{text}' to size, returning default '{OTTAVA_SIZE_DEFAULT}"
        )
        return OTTAVA_SIZE_DEFAULT

    assert size is not None
    return size


def _compute_ottava_size(ottava_text: Node | None) -> int:
    if ottava_text is None:
        return OTTAVA_SIZE_DEFAULT
    text = ottava_text.text_transcription
    if text is None:
        return OTTAVA_SIZE_DEFAULT
    return _interpret_ottava_size_from_text(text)


def compute_ottava_direction_and_size(
    ottava: Node, durables: list[Node], ottava_text: Optional[Node] = None
) -> tuple[int, int]:
    """
    Returns delta shift caused by `ottava`.

    Returns `direction, size`
    """
    direction = ottava.data.get(OttavaConstants.DIRECTION)
    if direction is None:
        direction = infer_vertical_object_placement_relative_to_notes(ottava, None, durables)  # type: ignore
        ottava.data[OttavaConstants.DIRECTION] = direction

    size = ottava.data.get(OttavaConstants.SIZE)
    if size is None:
        size = _compute_ottava_size(ottava_text)
        ottava.data[OttavaConstants.SIZE] = size

    assert size > 0
    assert direction in {-1, 1}

    return direction, size
