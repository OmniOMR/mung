from enum import StrEnum


class PrecedenceLinksConstants(StrEnum):
    """
    This class stores names of precedence-link-related fields in ``Node.data``.
    """
    PRECEDENCE_INLINKS = "precedence_inlinks"
    PRECEDENCE_OUTLINKS = "precedence_outlinks"
