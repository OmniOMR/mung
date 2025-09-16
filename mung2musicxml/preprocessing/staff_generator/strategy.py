from dataclasses import dataclass


@dataclass(frozen=True)
class StaffGeneratorStrategy:
    """
    If ``FORCE_STAFF_REBUILD`` is true, the staff nodes and masks
    are recomputed 
    """
    FORCE_STAFF_REBUILD: bool = True