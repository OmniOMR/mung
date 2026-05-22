from abc import ABC

from ..constants.utils.num_map import AllStrEnumNumeralMapped
from .. import Node


class NumeralInterpreterBase(ABC):
    __enums__: type[AllStrEnumNumeralMapped] = ... # type: ignore

    _all_numbers: set[AllStrEnumNumeralMapped] = set()
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.__enums__ is not ...:
            cls._all_numbers = cls.__enums__.all_numeral_members()

    def interpret_single_number(self, node: Node) -> int:
        return self.__enums__(node.class_name).to_digit()
    
    def interpret_number(self, nodes: list[Node]) -> int:
        assert len(nodes) > 0

        total = 0
        for n in nodes:
            total = total * 10 + self.interpret_single_number(n)
        return total
