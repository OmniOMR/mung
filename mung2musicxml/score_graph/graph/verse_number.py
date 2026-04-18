from dataclasses import dataclass

from .scene_object import SceneObject
from .lyric import Lyric


@dataclass
class VerseNumber(SceneObject):
    parent: Lyric
    text: str
