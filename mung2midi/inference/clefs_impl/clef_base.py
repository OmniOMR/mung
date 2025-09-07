from abc import ABC, abstractmethod


class ClefBase(ABC):
    _DELTA_STEP_COUNT = 8
    _MIN_COMMON_DELTA_COUNT = 1
    def __init__(self):
        self.__post_init__()

    def __post_init__(self):
        if len(self.delta_steps) != ClefBase._DELTA_STEP_COUNT:
            raise ValueError(
                f"There have to be exactly {ClefBase._DELTA_STEP_COUNT} deltas, "
                f"class initialized with {len(self.delta_steps)}"
            )
        if len(self.common_staffline_deltas) < ClefBase._MIN_COMMON_DELTA_COUNT:
            raise ValueError(
                f"There has to be more than {ClefBase._MIN_COMMON_DELTA_COUNT} deltas "
                "in common deltas specified, "
                f"class initialized with {len(self.common_staffline_deltas)}"
            )
    
    def is_common_delta(self, delta: int) -> bool:
        return delta in self.common_staffline_deltas
        
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def base_pitch(self) -> int:
        pass

    @property
    @abstractmethod
    def delta_steps(self) -> list[int]:
        pass

    @property
    @abstractmethod
    def base_pitch_step(self) -> int:
        pass
    
    @property
    @abstractmethod
    def base_pitch_octave(self) -> int:
        pass

    @property
    @abstractmethod
    def default_staffline_delta(self) -> int:
        pass

    @property
    @abstractmethod
    def common_staffline_deltas(self) -> list[int]:
        pass
