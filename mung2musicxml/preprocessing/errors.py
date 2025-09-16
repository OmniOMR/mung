from mung.constants import WESTERN_NOTATION_STAFFLINE_COUNT


class StafflineCountNotMultipleError(ValueError):
    def __init__(self):
        message = f"Provided staffline count is not a multiple of {WESTERN_NOTATION_STAFFLINE_COUNT}"
        super().__init__(message)


class StaffspaceCountNotMultipleError(ValueError):
    def __init__(self):
        message = f"Provided staffspace count is not a multiple of {WESTERN_NOTATION_STAFFLINE_COUNT + 1}"
        super().__init__(message)


class MaskIsNoneError(ValueError):
    def __init__(self):
        message = "Mask is None"
        super().__init__(message)
