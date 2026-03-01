from dataclasses import dataclass
from typing import TYPE_CHECKING
from functools import cached_property

from .tokens import AccidentalValue
from .in_part_measure_modifier import InMeasureModifier
if TYPE_CHECKING:
    from .accidental import Accidental


# TODO: supports only traditional key signatures
@dataclass
class Key(InMeasureModifier):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/key/
    """
    def _compute_fifths(self) -> int:
        acc = self.accidentals
        assert len(set(a.type_ for a in acc)) == 1
        if acc[0].type_ == AccidentalValue.SHARP:
            return len(acc)
        elif acc[0].type_ == AccidentalValue.FLAT:
            return - len(acc)
        elif acc[0].type_ == AccidentalValue.NATURAL:
            return 0
        else:
            raise ValueError
    
    @cached_property
    def fifths(self) -> int:
        return self._compute_fifths()

    @property
    def accidentals(self) -> list["Accidental"]:
        from .accidental import Accidental
        return Accidental.many_of(self, lambda a: a.parent)
