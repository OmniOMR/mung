from abc import abstractmethod
from typing import Optional

from ...constants import ClassNameConstants as C
from ... import Node, NotationGraph
from .time_sig_struct import TimeSigStruct
from ...logger import logger
from ..numeral_interpreter_base import NumeralInterpreterBase

T = C.TimeSignatures


class TimeSignatureInterpreter(NumeralInterpreterBase):
    __enums__ = C.TimeSignatures

    @abstractmethod
    def _interpret_impl(self, container: Node, graph: NotationGraph) -> Optional[TimeSigStruct]:
        pass

    def interpret_time_signature(
        self, container: Node, graph: NotationGraph
    ) -> Optional[TimeSigStruct]:
        assert container.class_name == C.TimeSignatures.TIME_SIGNATURE
        try:
            return self._interpret_impl(container, graph)
        except Exception as e:
            logger.warning(e)
            return None
