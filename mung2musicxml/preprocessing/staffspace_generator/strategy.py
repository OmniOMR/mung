from dataclasses import dataclass


@dataclass(frozen=True)
class StaffspaceGeneratorStrategy:
    """
    If ``PRECISE_MASK`` is true, the actual mask between two stafflines is computed,
    if not, the outputted mask is a rectangle covering the whole bounding box of two stafflines.
    """
    PRECISE_MASK: bool = True
