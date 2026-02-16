from abc import abstractmethod
from typing import Optional
from fractions import Fraction

from ...constants import ClassNameConstants as C
from ... import Node, NotationGraph
from ...logger import logger
from ..numeral_interpreter_base import NumeralInterpreterBase

T = C.TimeSignatures


class TupletModifierInterpreter(NumeralInterpreterBase):
    __enums__ = C.Tuplets

    @abstractmethod
    def _interpret_impl(self, container: Node, graph: NotationGraph) -> Optional[Fraction]:
        pass

    def interpret_tuplet_modifier(
        self, container: Node, graph: NotationGraph
    ) -> Optional[Fraction]:
        assert container.class_name == C.Tuplets.TUPLET
        try:
            return self._interpret_impl(container, graph)
        except Exception as e:
            logger.warning(e)
            return None
