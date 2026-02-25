from dataclasses import dataclass, field
from itertools import chain
from collections import defaultdict

from .scene_object import SceneObject
from .voice import Voice
from .score_part import ScorePart
from .system_measure import SystemMeasure
from .part_measure import PartMeasure

from fractions import Fraction
MUSICXML_VERSION = "4.0"
SOFTWARE_NAME = "placeholder software name"
QUARTER_NOTE_DURATION = Fraction(4)


from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Tuple
from collections import Counter
from functools import cached_property


from dataclasses import dataclass
@dataclass
class TimeSigStruct:
    numerator: int
    denominator: int

    def as_fraction(self) -> Fraction:
        return Fraction(self.numerator, self.denominator)
    
    def __add__(self, other: Fraction) -> Fraction:
        return self.as_fraction() + other
    
    def __sub__(self, other: Fraction) -> Fraction:
        return self.as_fraction() - other
    
    def __hash__(self) -> int:
        return hash(self.as_fraction())
    

# Define the canonical time signatures you want to consider
# 6/8 is left out as it is 3/4
CANONICAL = [
    TimeSigStruct(4, 4),
    TimeSigStruct(3, 4),
    TimeSigStruct(2, 4),
    TimeSigStruct(9, 8),
    TimeSigStruct(3, 2),
    TimeSigStruct(5, 4),
    TimeSigStruct(7, 8),
]

def closest_signature(value: Fraction, signatures: list[TimeSigStruct]=CANONICAL) -> TimeSigStruct:
    """Return the time signature closest to 'value'."""
    return min(signatures, key=lambda sig: abs(sig - value))

DEFAULT_TIME_SIGNATURE = TimeSigStruct(4, 4)
def most_common_time_signature(values: list[Fraction]) -> TimeSigStruct:
    """For each value pick the closest signature and return the most common one."""
    mapped = [closest_signature(v) for v in values if v > 0]
    if len(mapped) == 0:
        return DEFAULT_TIME_SIGNATURE
    counter = Counter(mapped)
    return counter.most_common(1)[0][0]


@dataclass
class Score(SceneObject):
    score_parts: list[ScorePart]
    system_measures: list[SystemMeasure]

    max_measure_index: int = field(init=False)
    _mapping: dict[int, SystemMeasure] = field(init=False, repr=False, default_factory=dict)

    def __post_init__(self) -> None:
        self.max_measure_index = max(chain.from_iterable(
            (x.id for x in sp.part_measures) for sp in self.score_parts
        ))

        # collect system measure
        # part_measure_to_system_measures: defaultdict[int, list[PartMeasure]] = defaultdict(list)
        # for sp in self.score_parts:
        #     for pm in sp.part_measures:
        #         part_measure_to_system_measures[pm.id_].append(pm)
        
        # sms = []
        # for id_, pms in part_measure_to_system_measures.items():
        #     sms.append(SystemMeasure(id_=id_, part_measures=pms, is_new_system=pms[0].is_new_system))

        # self.system_measures = sms
        
        for sm in self.system_measures:
            self._mapping[sm.id_] = sm

    # @property
    # def musicxml_version(self) -> str:
    #     return MUSICXML_VERSION
    
    # @property
    # def software_name(self) -> str:
    #     return SOFTWARE_NAME
    
    @cached_property
    def most_common_time_signature(self) -> TimeSigStruct:
        return most_common_time_signature([sm._get_duration_impl() / QUARTER_NOTE_DURATION for sm in self.system_measures])

    def get_system_measure_by_id(self, value: int) -> SystemMeasure:
        assert 0 < value <= self.max_measure_index
        return self._mapping[value]
