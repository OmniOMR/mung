from dataclasses import dataclass

from .scene_object import SceneObject
from .durable import Durable
from .grace_note import GraceNote


@dataclass
class Dot(SceneObject):
    durable: Durable | GraceNote
