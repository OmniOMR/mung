import re
from argparse import ArgumentParser
from pathlib import Path

from mung import NotationGraph
from .duplicate_groupings import remove_duplicate_groupings

DEFAULT_MUNG_FILE_NAME = "mung.xml"


def is_uuid_pair(s: str) -> bool:
    uuid_pattern = r"[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}"
    full_pattern = f"^{uuid_pattern}_{uuid_pattern}$"
    return re.fullmatch(full_pattern, s) is not None


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("input", type=Path, help="Input directory")
    args = parser.parse_args()
    input_dir: Path = args.input

    for directory in input_dir.iterdir():
        if is_uuid_pair(directory.name):
            graph = NotationGraph.from_file(directory / DEFAULT_MUNG_FILE_NAME)
            removed_any = remove_duplicate_groupings(graph)
            if removed_any:
                print(f"Removed duplicate groupings: {directory.name}")
