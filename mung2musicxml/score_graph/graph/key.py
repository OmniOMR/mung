from dataclasses import dataclass
from typing import TYPE_CHECKING
from functools import cached_property

from .accidental_type import AccidentalType
from .in_part_measure_modifier import InPartMeasureModifier
if TYPE_CHECKING:
    from .accidental import Accidental


# TODO: supports only traditional key signatures
@dataclass
class Key(InPartMeasureModifier):
    def _compute_fifths(self) -> int:
        acc = self.accidentals
        assert len(set(a.type_ for a in acc)) == 1
        if acc[0].type_ == AccidentalType.SHARP:
            return len(acc)
        elif acc[0].type_ == AccidentalType.FLAT:
            return - len(acc)
        else:
            raise ValueError
    
    @cached_property
    def fifths(self) -> int:
        return self._compute_fifths()

    @property
    def accidentals(self) -> list["Accidental"]:
        from .accidental import Accidental
        return Accidental.many_of(self, lambda a: a.parent)
