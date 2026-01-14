from enum import StrEnum


class AllExtendedStrEnum(StrEnum):
    """
    Implements the "ALL" function that returns
    all constants defined in the class.
    """
    @classmethod
    def ALL(cls):
        return list(cls)
