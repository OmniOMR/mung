from mung.constants import ClassNameConstants as C

from .clef_base import ClefBase


class GClef(ClefBase):
    @property
    def name(self) -> str:
        return C.Clefs.G_CLEF

    @property
    def base_pitch(self) -> int:
        return 71

    @property
    def delta_steps(self) -> list[int]:
        return [0, 1, 2, 2, 1, 2, 2, 2]

    @property
    def base_pitch_step(self) -> int:
        return 6
    
    @property
    def base_pitch_octave(self) -> int:
        return 4

    @property
    def default_staffline_delta(self) -> int:
        return -2
    
    @property
    def common_staffline_deltas(self) -> list[int]:
        return [-2, -4]

    @property
    def deltas_sharp(self) -> list[int]:
        return [4, 1, 5, 2, 6, 3, 0]

    @property
    def deltas_flat(self) -> list[int]:
        return [0, 3, 6, 2, 5, 1, 4]