from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from .subevent import Subevent
from .tokens import SyllabicTypeToken
from .interface import GenericStartStopOnset

if TYPE_CHECKING:
    from .verse_number import VerseNumber
    from .lyric_level import LyricLevel


SYLLABIC_HYPHEN_CHARACTER = "-"
MELISMA_CHARACTER = "_"


@dataclass(kw_only=True)
class Lyric(GenericStartStopOnset[Subevent]):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/examples/extend-element-lyric/
    """
    text: str

    def __post_init__(self) -> None:
        super().__post_init__()
        self._check_start_is_set()
        self._check_start_stop_onset_strong()
        assert len(self.text) > 0

    @property
    def clear_text(self) -> str:
        if self.text[-1] in {
            SYLLABIC_HYPHEN_CHARACTER,
            MELISMA_CHARACTER
        }:
            return self.text[:-1]
        
        return self.text
    
    @property
    def is_syllabic(self) -> bool:
        """
        Returns true, if the lyric text ends with "-".
        """
        return self.text.endswith(SYLLABIC_HYPHEN_CHARACTER)
    
    @property
    def is_extend(self) -> bool:
        """
        Returns true, if the lyric text ends with "_".
        """
        return self.text.endswith(MELISMA_CHARACTER)
    
    @property
    def syllabic_type(self) -> SyllabicTypeToken:
        previous = self.lyric_level.get_previous(self)
        following = self.lyric_level.get_following(self)

        prev_syllabic = previous is not None and previous.is_syllabic
        curr_syllabic = self.is_syllabic and following is not None

        if prev_syllabic and curr_syllabic:
            return SyllabicTypeToken.MIDDLE
        if curr_syllabic:
            return SyllabicTypeToken.BEGIN
        if prev_syllabic:
            return SyllabicTypeToken.END
        return SyllabicTypeToken.SINGLE

    @property
    def lyric_level(self) -> "LyricLevel":
        from .lyric_level import LyricLevel
        return LyricLevel.of(self, lambda l: l.lyrics)
    
    @property
    def verse_number(self) -> Optional["VerseNumber"]:
        from .verse_number import VerseNumber
        return VerseNumber.of_or_none(self, lambda v: v.parent)
