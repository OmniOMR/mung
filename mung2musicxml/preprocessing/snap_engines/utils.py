import numpy as np
from mung import Node
from mung.graph import resolve_notehead_wrt_staffline
from typing import Optional, TypeVar, Iterable
from collections import Counter

from .snap_constants import StaffDirectionFromNotehead
from ...logger import logger


def check_leger_line_assignments(notehead: Node, leger_lines: list[Node]) -> None:
    """
    Checks the relations of a notehead and its leger lines based on their relative positioning.
    Raises warnings, if something suspicious is found.
    """
    leger_lines_pos = [resolve_notehead_wrt_staffline(notehead, x) for x in leger_lines]
    assert len(leger_lines) > 0

    counts = np.bincount(np.array(leger_lines_pos, dtype=int) + 1, minlength=3)
    assert len(counts) == 3

    if counts[0] > 0 and counts[2] > 0:
        logger.warning("Notehead cannot have leger lines both above and below. "
                        f"Notehead: {notehead.id}, leger lines: {', '.join([str(x.id) for x in leger_lines])}")
    if counts[1] > 1:
        logger.warning("Notehead cannot be directly on more than one leger line. "
                        f"Notehead: {notehead.id}, leger lines: {', '.join([str(x.id) for x in leger_lines])}")


def get_staff_direction_based_on_notehead_and_leger_lines_position(notehead: Node, leger_lines: list[Node]) -> StaffDirectionFromNotehead:
        """
        Returns the assumed the direction of staff from the given notehead and its leger lines.
        Returns an instance of ``StaffDirectionFromNotehead``.
        """
        assert len(leger_lines) > 0
        distances_from_notehead = sum([leger_line.middle[0] - notehead.middle[0] for leger_line in leger_lines])
        return (StaffDirectionFromNotehead.UNDER
                if distances_from_notehead >= 0
                else StaffDirectionFromNotehead.ABOVE)


def count_ids_check_for_draw(ids: list[int]) -> Optional[int]:
    """
    Counts given IDs and returns the most common one,
    in a case of a draw, returns ``None`` .
    """
    assert len(ids) > 0

    c = Counter(ids)
    two_most_common = c.most_common(2)
    if len(two_most_common) < 2:
        two_most_common: list[tuple[int,int]]
        return two_most_common[0][0]
    
    (f_id, f_count), (_, s_count) = two_most_common
    if f_count == s_count:
        logger.warning("Cannot resolve")
        return None
    
    return f_id


T = TypeVar("T", bound=type)

def all_subclasses(cls: T) -> set[T]:
    """
    Returns all subclasses recursively that are derived
    from the given ``cls``. 
    """
    subclasses = set(cls.__subclasses__())
    for subclass in cls.__subclasses__():
        subclasses.update(all_subclasses(subclass))
    return subclasses


def log_total(total: int, names: Iterable[str] | str):
    names_: list[str] = sorted(names) if not isinstance(names, str) else [names]
    logger.info(f"Snapped {total} {', '.join(names_)} to staffs.")
