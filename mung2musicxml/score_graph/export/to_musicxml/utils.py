from typing import Iterator

from ...graph import Subevent, InPartMeasureModifier


def _aggregate_mods(
    objects: list[Subevent | InPartMeasureModifier],
) -> Iterator[Subevent | list[InPartMeasureModifier]]:
    """
    Iterate through objects, grouping consecutive items that meet a condition.
    
    Args:
        objects: List of objects to iterate through
        condition: Function that takes an object and returns True/False
    
    Yields:
        Either a single object or a list of consecutive objects meeting the condition
    """          
    streak: list[InPartMeasureModifier] = []
    current_id: None | int = None
    
    for obj in objects:
        if isinstance(obj, InPartMeasureModifier):
            obj_onset = obj.in_measure_onset
            
            # start new streak or continue if same onset
            if not streak or obj_onset == current_id:
                streak.append(obj)
                current_id = obj_onset
            else:
                # different onset - yield old streak and start new one
                yield streak
                streak = [obj]
                current_id = obj_onset
        else:
            # yield accumulated streak if any
            if streak:
                yield streak
                streak = []
                current_id = None
            # yield single object
            yield obj
    
    # remaining streak at the end
    if streak:
        yield streak
        