from dataclasses import dataclass, field
from mung.constants import ClassNamesConstants as C, InferenceEngineConstants as I


@dataclass(frozen=True)
class MultistemResolverStrategy:
    # If set to True, throws an error, print a warning if set to False
    PERMISSIVE: bool = False
    # List of class names of objects to share between original and ghost notehead
    SHARED_OBJECTS: list[str] = field(
        default_factory= lambda: list(set(
            I.STAFF_CLASSES
            + I.STAFFLINE_LIKE_CLASS_NAMES
            + I.ACCIDENTAL_CLASS_NAMES
            + I.HAIRPINS
            + [C.AUGMENTATION_DOT, C.SLUR, C.TUPLE]
        )))
    
    # List of class names of objects to divide between original and ghost notehead
    DIVIDED_OBJECTS: list[str] = field(
        default_factory=lambda: list(set(
            I.FLAGS_AND_BEAMS
        )))
    
    # If set to True, shifts the ghost notehead a bit for it to be visible
    _DEBUG_GHOST_SHIFT: bool = False

    def __post_init__(self) -> None:
        self._validate()
    
    def _validate(self) -> None:
        if len(set(self.SHARED_OBJECTS) & set(self.DIVIDED_OBJECTS)) > 0:
            raise ValueError(f"{self.SHARED_OBJECTS=} and {self.DIVIDED_OBJECTS=} must have an empty intersection")
