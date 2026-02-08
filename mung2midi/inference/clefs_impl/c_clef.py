from mung.constants import ClassNameConstants as C

from .clef_base import ClefBase


class CClef(ClefBase):
    @property
    def name(self) -> str:
        return C.Clefs.C_CLEF

    @property
    def base_pitch(self) -> int:
        return 60

    @property
    def delta_steps(self) -> list[int]:
        return [0, 2, 2, 1, 2, 2, 2, 1]

    @property
    def base_pitch_step(self) -> int:
        return 0
    
    @property
    def base_pitch_octave(self) -> int:
        return 4

    @property
    def default_staffline_delta(self) -> int:
        return 0
    
    @property
    def common_staffline_deltas(self) -> list[int]:
        return [-4, -2, 0, 2, 4]
    
    @property
    def deltas_sharp(self) -> list[int]:
        return [3, 0, 4, 1, 5, 2, 6]

    @property
    def deltas_flat(self) -> list[int]:
        return [6, 2, 5, 1, 4, 0, 3]