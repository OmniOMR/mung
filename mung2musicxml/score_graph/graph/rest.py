from dataclasses import dataclass

from .durable import Durable
from .subevent import Subevent


@dataclass
class Rest(Durable, Subevent):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/rest/

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/note/
    """
    @property
    def all_durables(self) -> list[Durable]:
        return [self]
    
    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other
