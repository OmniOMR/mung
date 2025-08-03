from enum import Enum
from .symbol import Symbol
import numpy as np


class LinkDirection(Enum):
    OUTLINK = "out"
    INLINK = "in"

    def to_arrow(self) -> str:
        if self == LinkDirection.OUTLINK:
            return "->"
        elif self == LinkDirection.INLINK:
            return "<-"
        else:
            raise ValueError(f"Unknown LinkDirection: {self}")


class GrammarConstants:
    ANY_SYMBOL = Symbol("__ANY__")
    DEFAULT_LOWER_LIMIT: int = 0
    DEFAULT_UPPER_LIMIT: int = np.inf  # type: ignore
    COMMENT_SYMBOL = "#"
    RULE_DELIMITER = "|"
