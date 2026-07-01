from dataclasses import dataclass

from .barline import Barline
from .tokens import BackwardForwardToken, WingedToken


@dataclass(kw_only=True)
class RepeatBarline(Barline):
    bf: BackwardForwardToken
    winged: WingedToken

    def __post_init__(self) -> None:
        return super().__post_init__()
    