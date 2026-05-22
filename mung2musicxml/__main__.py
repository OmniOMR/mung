import argparse
import logging
from pathlib import Path
from typing import Optional

from mung import NotationGraph
from .utils import is_uuid_pair
from .score_graph.load.from_mung import MuNG_LoadEngine
from .score_graph.export.to_musicxml import (
    MusicXML_ExportEngine,
    MusicXMLExportSettings,
    ErrorHandlingSettings,
)
from .preprocessing.pipeline import MuNGPreprocessingPipeline
from .preprocessing.mung_path_loader import load_mung_paths, _get_name


DEFAULT_LOCAL_DIR_UFAL: Path = Path(
    "/home/mayer/public_html/mung-studio-simple-php-backend/documents"
)
DEFAULT_MUNG_FILE_NAME: str = "mung.xml"


def setup_logging(level: str) -> None:
    if level == "NONE":
        logging.disable()
        return

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MuNG to MusicXML Convertor",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("input", type=str, help="Input MuNG file to process")

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["NONE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging verbosity level",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Shorthand for --log-level DEBUG",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Shorthand for --log-level WARNING",
    )

    parser.add_argument("--output", "-o", help="Output file or dir")
    parser.add_argument(
        "--skip-broken-measure",
        action="store_true",
        help="Skips broken measures in export",
    )

    return parser.parse_args()


def process_single_mung_to_musicxml(
    input_file: Path,
    output: Optional[Path] = None,
    pipeline: Optional[MuNGPreprocessingPipeline] = None,
    loader: Optional[MuNG_LoadEngine] = None,
    exporter: Optional[MusicXML_ExportEngine] = None,
) -> None:
    if pipeline is None:
        pipeline = MuNGPreprocessingPipeline()
    if loader is None:
        loader = MuNG_LoadEngine()
    if exporter is None:
        exporter = MusicXML_ExportEngine()

    g = NotationGraph.from_file(input_file)
    g = pipeline(g)
    score = loader.load(g)

    if output is not None:
        exporter.export_to_file(score, output)
    else:
        exp = exporter.export(score)


def count_lines_in_file(file: Path) -> int:
    with open(file, "r") as f:
        num_lines = sum(1 for _ in f)
    return num_lines


def process_batch(
    batch_file: Path,
    output_dir: Optional[Path] = None,
    pipeline: Optional[MuNGPreprocessingPipeline] = None,
    loader: Optional[MuNG_LoadEngine] = None,
    exporter: Optional[MusicXML_ExportEngine] = None,
) -> None:
    if pipeline is None:
        pipeline = MuNGPreprocessingPipeline()
    if loader is None:
        loader = MuNG_LoadEngine()
    if exporter is None:
        exporter = MusicXML_ExportEngine()

    if output_dir is not None:
        output_dir.mkdir(exist_ok=True, parents=True)

    for input_file in load_mung_paths(str(batch_file)):
        output_file = None
        if output_dir is not None:
            output_file = output_dir / f"{_get_name(input_file)}.musicxml"
        process_single_mung_to_musicxml(
            input_file, output_file, pipeline=pipeline, loader=loader, exporter=exporter
        )


def wrap_local_file(
    name: str,
    local_dir: Optional[Path] = None,
    file: Optional[str] = DEFAULT_MUNG_FILE_NAME,
) -> Path:
    if local_dir is None:
        local_dir = DEFAULT_LOCAL_DIR_UFAL

    if file is not None:
        return local_dir / name / file
    else:
        return local_dir / name


def main() -> None:
    args = parse_args()

    # resolve log level
    if args.verbose:
        log_level = "DEBUG"
    elif args.quiet:
        log_level = "WARNING"
    else:
        log_level = args.log_level

    setup_logging(log_level)

    if is_uuid_pair(args.input.strip()):
        input_file = wrap_local_file(args.input)
    else:
        input_file = Path(args.input)

    if args.output is not None:
        args.output = Path(args.output)

    exporter = MusicXML_ExportEngine(
        MusicXMLExportSettings(
            error_handling=ErrorHandlingSettings(
                skip_broken_measure=args.skip_broken_measure
            )
        )
    )

    if input_file.suffix == ".txt":
        process_batch(input_file, args.output, exporter=exporter)
    else:
        process_single_mung_to_musicxml(input_file, args.output, exporter=exporter)


if __name__ == "__main__":
    main()
