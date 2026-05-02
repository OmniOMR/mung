
from ..utils import is_uuid_pair
from pathlib import Path
from ..logger import logger
from typing import Generator, Optional, Callable


DEFAULT_LOCAL_DIR_UFAL: Path = Path("/home/mayer/public_html/mung-studio-simple-php-backend/documents")
DEFAULT_MUNG_FILE_NAME: str = "mung.xml"


def count_lines_in_file(file: Path) -> int:
    with open(file, "r") as f:
        num_lines = sum(1 for _ in f)
    return num_lines


def wrap_local_file(
        name: str,
        local_dir: Path = DEFAULT_LOCAL_DIR_UFAL,
        file: str = DEFAULT_MUNG_FILE_NAME
    ) -> Path:    
    if file is not None:
        return local_dir / name / file
    else:
        return local_dir / name
    

def _file_or_local(file: str) -> Path:
    if is_uuid_pair(file):
        return wrap_local_file(file)
    else:
        return Path(file)


def _get_name(file: Path) -> str:
    return str(file.parent.name)


def _yield_batch(batch_file: Path, get_name: Callable[[Path], str]) -> Generator[Path, None, None]:
    num_lines = count_lines_in_file(batch_file)
    
    with open(batch_file, "r", encoding="utf8") as file:
        for index, line in enumerate(file):

            if line.startswith("#"):
                logger.info(f"[{index + 1}/{num_lines}] Skipped '{line}'")
                continue

            line = line.rstrip()
            if is_uuid_pair(line):
                input_file = wrap_local_file(line)
            else:
                input_file = Path(line.rstrip())
            
            logger.info(f"[{index + 1}/{num_lines}] Processing file '{input_file}'")
            yield input_file


def load_mung_paths(file: str, get_name: Optional[Callable[[Path], str]] = None) -> Generator[Path, None, None]:
    if get_name is None:
        get_name = _get_name
    if is_uuid_pair(file):
        yield wrap_local_file(file)
    
    file_path = Path(file)

    if file_path.suffix == ".txt":
        yield from _yield_batch(file_path, get_name)
        