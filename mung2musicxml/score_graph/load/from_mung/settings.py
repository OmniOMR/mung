from dataclasses import dataclass, field
from ...graph import SceneObject, DurableBeam, Tuplet, TremoloBeam
from typing import Type


@dataclass
class MuNGLoaderSettings:
    critical_classes: set[Type[SceneObject]] = field(
        default_factory=lambda: {DurableBeam, Tuplet, TremoloBeam}
    )
    measure_index_start: int = 1
    voice_limit: int = 8
