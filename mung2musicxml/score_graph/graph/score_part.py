from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
from itertools import chain

from .scene_object import SceneObject
from .utils.id_class import IDClass
from .staff import Staff
from .durable import Durable
from .part_measure import PartMeasure
from ...utils import flatten
if TYPE_CHECKING:
    from .score import Score
    from .part_group import PartGroup


@dataclass
class ScorePart(SceneObject, IDClass):
    """
    Score part contains information
    for a single instrument of `Score`.
    
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/score-part/
    """
    part_measures: list[PartMeasure]

    staffs: list[Staff] = field(init=False)
    name: str = field(default="")

    _mapping: dict[int, PartMeasure] = field(init=False, repr=False, default_factory=dict)

    def __post_init__(self) -> None:
        IDClass.__init__(self)
        ids = [m.id for m in self.part_measures]
        assert len(ids) == len(set(ids))

        self.part_measures.sort(key=lambda m: m.id)

        # setup staffs and compute divisions
        staffs = set()
        for durable in chain.from_iterable(m.all_durables for m in self.part_measures):
            staffs.add(durable.staff)
        
        self.staffs = sorted(staffs, key=lambda s: s.id)

        if len(self.name) == 0:
            self.name = f"{self.id}-{len(self.staffs)}"

        for part in self.part_measures:
            self._mapping[part.id] = part

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other

    @property
    def divisions(self) -> int:
        return self.score.divisions

    @property
    def id(self) -> int:
        return self._id

    @property
    def is_first(self) -> bool:
        return self._id == 1
    
    def get_part_measure_by_id(self, value: int) -> Optional[PartMeasure]:
        assert 0 < value <= self.score.max_measure_index
        return self._mapping.get(value)
    
    @property
    def all_durables(self) -> list[Durable]:
        return flatten(m.all_durables for m in self.part_measures)
    
    @property
    def score(self) -> "Score":
        from .score import Score
        return Score.of(self, lambda s: s.score_parts)
    
    @property
    def part_groups(self) -> list["PartGroup"]:
        from .part_group import PartGroup
        return PartGroup.many_of(self, lambda p: p.parts)
    