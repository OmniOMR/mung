from typing import Any
from pathlib import Path
from abc import ABC, abstractmethod

from ..graph import Score


class ExportEngine(ABC):
    """
    Abstract `Score` exporter.
    """
    @abstractmethod
    def export(self, score: Score) -> Any:
        pass

    @abstractmethod
    def export_to_file(self, score: Score, file_name: Path | str) -> None:
        pass
    