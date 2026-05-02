from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter
import logging
from mung import NotationGraph
from pathlib import Path

from .pipeline import MuNGPreprocessingPipeline
from .mung_path_loader import load_mung_paths, _get_name


def parse_args() -> Namespace:
    parser = ArgumentParser(
        description="MuNG Preprocessor",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    # logging control
    parser.add_argument(
        "-l",
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NONE"],
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

    # app args
    parser.add_argument("input", type=str, help="Input value to process")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--batch-output", help="Directory for output files")

    return parser.parse_args()


def setup_logging(level: str) -> None:
    if level.upper() == "NONE":
        logging.disable(logging.CRITICAL)
        return
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main() -> None:
    args = parse_args()

    if args.verbose:
        log_level = "DEBUG"
    elif args.quiet:
        log_level = "WARNING"
    else:
        log_level = args.log_level

    setup_logging(log_level)

    output_dir = args.batch_output
    if output_dir is not None:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)

    for mung_path in load_mung_paths(args.input):
        g = NotationGraph.from_file(mung_path)
        g = MuNGPreprocessingPipeline.run(g)
        if args.output is not None:
            g.save_to_file(args.output)
        if output_dir is not None:
            g.save_to_file(output_dir / f"{_get_name(mung_path)}.xml")


if __name__ == "__main__":
    main()
