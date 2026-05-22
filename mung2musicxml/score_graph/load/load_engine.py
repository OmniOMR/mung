from typing import Any
from pathlib import Path
from abc import ABC, abstractmethod

from ..graph import Score


class LoadEngine(ABC):
    """
    Load given file as a `Score`.
    """
    @abstractmethod
    def load(self, data: Any) -> Score:
        pass

    @abstractmethod
    def load_from_file(self, file_name: Path | str) -> Score:
        pass
    