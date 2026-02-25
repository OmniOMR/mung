from dataclasses import dataclass

from .durable import Durable
from .subevent import Subevent


# TODO: currently only supports repeats inside single measure
@dataclass
class RepeatBar(Durable, Subevent):
    @property
    def all_durables(self) -> list[Durable]:
        return [self]
    
    @property
    def number(self) -> int:
        return self.staff.staff_id
    
    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other
