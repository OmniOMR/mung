from dataclasses import dataclass

from .durable import Durable
from .subevent import Subevent


# TODO: currently only supports single measure repeats
@dataclass
class RepeatBar(Durable, Subevent):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/measure-repeat/
    """
    @property
    def all_durables(self) -> list[Durable]:
        return [self]
    
    @property
    def number(self) -> int:
        return self.staff.id
    
    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other
