from dataclasses import dataclass, field

from .snap_constants import StaffAssignmentFallbackStrategy


@dataclass(frozen=True)
class NoteheadSnapEngineStrategy:
    """
    If a notehead with a single leger line is encountered, ``STAFF_ASSIGNMENT_FALLBACK_PRIORITY``
    specifies the order of fallbacks to solve this difficult case.
    The first definitive result will be used. Default order is ```chord, beam, closest, stem``.
    For implementation details, see the notehead snap engine.
    """
    STAFF_ASSIGNMENT_FALLBACK_PRIORITY: list[StaffAssignmentFallbackStrategy] = field(default_factory=lambda:
    [
        StaffAssignmentFallbackStrategy.CHORD,
        StaffAssignmentFallbackStrategy.BEAM,
        StaffAssignmentFallbackStrategy.CLOSEST,
        StaffAssignmentFallbackStrategy.STEM,
    ])

    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if len(self.STAFF_ASSIGNMENT_FALLBACK_PRIORITY) == 0:
            raise ValueError("Priority has to specify at least one strategy")
        
        if all(f.can_fail() for f in self.STAFF_ASSIGNMENT_FALLBACK_PRIORITY):
            raise ValueError("Priority has to specify at least one strategy that cannot fail.")


@dataclass(frozen=True)
class GeneralSnapEngineStrategy:
    """
    If ``PERMISSIVE`` is true, in certain situation,
    the engine does not raise an error and only logs a warning.

    There can be situation when the computed staff id differs
    from the derived one (staff id can be derived from stafflines),
    if ``DEFAULT_TO_COMPUTED`` is true, the computed value will used,
    if not, the derived one will be used.
    """
    PERMISSIVE: bool = True
    DEFAULT_TO_COMPUTED: bool = False


@dataclass(frozen=True)
class MeasureSeparatorSnapEngineStrategy:
    """
    If more than ``MEASURE_ASSIGNMENT_THRESHOLD`` of measure separator
    is vertically overlapping with a staff, that measure separator
    will be linked to that staff.
    """
    MEASURE_ASSIGNMENT_THRESHOLD: float = 0.5


@dataclass(frozen=True)
class SnapWrapperStrategy:
    notehead_strategy: NoteheadSnapEngineStrategy = field(default_factory=NoteheadSnapEngineStrategy)
    measure_separator_strategy: MeasureSeparatorSnapEngineStrategy = field(default_factory=MeasureSeparatorSnapEngineStrategy)
    general_strategy: GeneralSnapEngineStrategy = field(default_factory=GeneralSnapEngineStrategy)
