from dataclasses import dataclass
from typing import Optional

from .scene_object import SceneObject
from .lyric import Lyric


SYLLABIC_HYPHEN_CHARACTER = "-"
MELISMA_CHARACTER = "_"


@dataclass
class LyricLevel(SceneObject):
    number: int
    lyrics: list[Lyric]

    def __post_init__(self) -> None:
        self.lyrics.sort(
            key=lambda l: l.start.global_fractional_onset # type: ignore
        )

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other

    def get_previous(self, lyric: Lyric) -> Optional[Lyric]:
        """
        Returns the previous Lyric on the
        same level as the given one, if it exists,
        otherwise returns None.
        """
        index = self.lyrics.index(lyric)
        if index == 0:
            return None
        else:
            return self.lyrics[index - 1]
    
    def get_following(self, lyric: Lyric) -> Optional[Lyric]:
        """
        Returns the following Lyric on the
        same level as the given one, if it exists,
        otherwise returns None.
        """
        index = self.lyrics.index(lyric)
        if index == len(self.lyrics) - 1:
            return None
        else:
            return self.lyrics[index + 1]
