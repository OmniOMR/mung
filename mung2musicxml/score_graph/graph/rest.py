from dataclasses import dataclass

from .durable import Durable
from .subevent import Subevent


@dataclass
class Rest(Durable, Subevent):
    @property
    def all_durables(self) -> list[Durable]:
        return [self]

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other
