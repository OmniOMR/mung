from dataclasses import dataclass, field
from fractions import Fraction
from collections import Counter

from .subevent import Subevent
from .scene_object import SceneObject
from .note import Note
from .tokens import StemValueToken
from .durable import Durable
from ...logger import logger


@dataclass
class Chord(Subevent, SceneObject):
    """
    Group list of notes into a single chord.

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/chord/
    """
    notes: list[Note]
    stem_orientation: StemValueToken = field(init=False)

    def __post_init__(self) -> None:
        assert len(self.notes) > 0
        assert all(isinstance(n, Note) for n in self.notes)
        assert all(
            self.notes[0].in_measure_fractional_onset == n.in_measure_fractional_onset
            for n in self.notes
        ), f"Chord durables differ in onset {[(n, n.in_measure_fractional_onset) for n in self.notes]}"
        # notes will be outputted in order
        #  - longest to shortest
        #  - lowest to highest
        self.notes.sort(key=lambda n: (-n.fractional_duration, n.pitch))
        self.stem_orientation = self._compute_stem_orientation()
    
    def _compute_stem_orientation(self) -> StemValueToken:
        """
        Finds the most common stem orientation among given notes.
        """
        c = Counter(n.stem_orientation for n in self.notes)
        if len(c.items()) > 1:
            logger.warning(f"Inconsistent stem orientation for chord {self.notes}, "
                           "will choose the most common orientation")
        
        return c.most_common(1)[0][0]
    
    @property
    def all_durables(self) -> list[Durable]:
        return self.notes # type: ignore
    
    @property
    def first_note(self) -> Note:
        return self.notes[0]
    
    @property
    def fractional_duration(self) -> Fraction:
        return max(n.fractional_duration for n in self.notes)

    @property
    def in_measure_fractional_onset(self) -> Fraction:
        return self.notes[0].in_measure_fractional_onset
    
    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other
    
