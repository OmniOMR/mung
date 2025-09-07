# natural notes
NOTES = ["C", "D", "E", "F", "G", "A", "B"]

def next_tones(start: tuple[str, int], N: int) -> list[tuple[str, int]]:
    """
    Given a start tone (like ("D", 4)) and number N,
    return a list of N consecutive tones.
    Supports from ("C", 0) upwards.
    """
    note, octave = start
    if note not in NOTES:
        raise ValueError(f"Unsupported note: {note}")
    if octave < 0:
        raise ValueError(f"Unsupported octave: {octave}")

    start_index = NOTES.index(note)
    result = []

    for i in range(N):
        idx = (start_index + i) % len(NOTES)
        oct_shift = (start_index + i) // len(NOTES)
        result.append((NOTES[idx], octave + oct_shift))

    return result
