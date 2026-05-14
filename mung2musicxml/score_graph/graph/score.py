from dataclasses import dataclass, field
from itertools import chain
from fractions import Fraction
from typing import Optional, Iterable
from collections import Counter
import numpy as np

from mung.interpret import TimeSigStruct
from .scene_object import SceneObject
from .score_part import ScorePart
from .score_measure import ScoreMeasure
from ...logger import logger


MIDI_1_0_DIVISIONS_LIMIT = 16_383


def closest_signature(
    value: Fraction, signatures: Iterable[TimeSigStruct]
) -> TimeSigStruct:
    """
    Return the time signature closest to `value`.
    """
    return min(signatures, key=lambda sig: abs(sig - value))


def most_common_time_signature(
    values: Iterable[Fraction], canonical: Iterable[TimeSigStruct]
) -> Optional[TimeSigStruct]:
    """
    For each value pick the closest signature and return the most common one.
    """
    mapped = [closest_signature(v, canonical) for v in values if v > 0]
    if len(mapped) == 0:
        return None
    counter = Counter(mapped)
    return counter.most_common(1)[0][0]


@dataclass
class Score(SceneObject):
    """
    Container with all score parts.
    """
    score_parts: list[ScorePart]
    system_measures: list[ScoreMeasure]

    max_measure_index: int = field(init=False)
    divisions: int = field(init=False)
    _mapping: dict[int, ScoreMeasure] = field(
        init=False, repr=False, default_factory=dict
    )


    def __post_init__(self) -> None:
        self.max_measure_index = max(
            chain.from_iterable(
                (x.id for x in sp.part_measures) for sp in self.score_parts
            )
        )

        for sm in self.system_measures:
            self._mapping[sm.id] = sm
        
        denominators = set()
        for durable in chain.from_iterable(m.all_durables for m in self.score_parts):
            denominators.add(durable.fractional_duration.denominator)

        self.divisions = self._compute_divisions(list(denominators))

    def _compute_divisions(self, denominators: list[int]) -> int:
        if len(denominators) == 0:
            logger.warning("Score is empty, divisions set to 1")
            return 1
        
        divisions = np.lcm.reduce(denominators)
        if divisions > MIDI_1_0_DIVISIONS_LIMIT:
            logger.warning(f"Incompatible with MIDI 1.0, divisions value {divisions} exceeds {MIDI_1_0_DIVISIONS_LIMIT}")
        return divisions

    def get_most_common_time_signature(
        self, canonical: Iterable[TimeSigStruct]
    ) -> Optional[TimeSigStruct]:
        """
        Returns the most common time signature
        of measure in `Score`.
        """
        # TODO: check for explicit time signatures
        QUARTER_NOTE_DURATION = Fraction(4)
        return most_common_time_signature(
            (
                sm._get_duration_impl() / QUARTER_NOTE_DURATION
                for sm in self.system_measures
            ),
            canonical,
        )

    def get_system_measure_by_id(self, value: int) -> ScoreMeasure:
        assert 0 < value <= self.max_measure_index
        return self._mapping[value]
