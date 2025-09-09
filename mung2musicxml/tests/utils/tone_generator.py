from mung.constants import STEP_ORDER
from mung2musicxml.inference import Pitch, Octave, Step


def next_tones(start: tuple[str, int], N: int) -> list[Pitch]:
    """
    Given a start tone (like ("D", 4)) and number N,
    return a list of N consecutive tones.
    Supports from ("C", 0) upwards.
    """
    note, octave = start
    if note not in STEP_ORDER:
        raise ValueError(f"Unsupported note: {note}")
    if octave < 0:
        raise ValueError(f"Unsupported octave: {octave}")

    start_index = STEP_ORDER.index(note)
    result = []

    for i in range(N):
        idx = (start_index + i) % len(STEP_ORDER)
        oct_shift = (start_index + i) // len(STEP_ORDER)
        result.append(Pitch(Octave(octave + oct_shift), Step(STEP_ORDER[idx])))

    return result
