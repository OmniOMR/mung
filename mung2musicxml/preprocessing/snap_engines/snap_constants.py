from enum import Enum, auto


class StaffDirectionFromNotehead(Enum):
    UNDEFINED = 0
    UNDER = 1
    ABOVE = -1


class StaffAssignmentFallbackStrategy(Enum):
    CHORD = auto()
    BEAM = auto()
    STEM = auto()
    CLOSEST = auto()

    def can_fail(self) -> bool:
        if self == StaffAssignmentFallbackStrategy.CLOSEST:
            return False
        return True