from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceEngineStrategy:
    """
    If `OFFSET_VOICES_IN_GRAND_STAFF` is set to True,
    voices used for the bottom staff will be offset from
    `1-4` by `OFFSET_VALUE`. Default is `4`,  voices ids
    `5-8`.
    """
    OFFSET_VOICES_IN_GRAND_STAFF: bool = True
    OFFSET_VALUE: int = 4
