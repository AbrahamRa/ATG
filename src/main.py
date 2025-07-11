"""ATG - Main module.

This module contains the main entry point for the ATG (Automated Test Generator) tool.
"""
import argparse
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

logger = logging.getLogger(__name__)


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        args: Command line arguments. If None, uses sys.argv[1:].

    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="ATG - Automated Test Generator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (can be used multiple times)",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__import__(__package__).__version__}",
    )
    parser.add_argument(
        "source",
        type=Path,
        help="Source file or directory to generate tests for",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("tests"),
        help="Output directory for generated tests",
    )

    return parser.parse_args(args)


def setup_logging(verbosity: int = 0) -> None:
    """Set up logging configuration.

    Args:
        verbosity: Verbosity level (0=WARNING, 1=INFO, 2=DEBUG)
    """
    level = max(3 - verbosity, 0) * 10  # Convert to logging level
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def main(args: Optional[Sequence[str]] = None) -> int:
    """Run the main application.

    Args:
        args: Command line arguments. If None, uses sys.argv[1:].

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    try:
        parsed_args = parse_args(args)
        setup_logging(parsed_args.verbose)
        logger.info("Starting ATG")

        # Ensure source exists
        if not parsed_args.source.exists():
            logger.error(f"Source not found: {parsed_args.source}")
            return 1

        # Create output directory if it doesn't exist
        parsed_args.output.mkdir(parents=True, exist_ok=True)

        logger.info(f"Processing: {parsed_args.source}")
        logger.info(f"Output directory: {parsed_args.output.absolute()}")

        # TODO: Add test generation logic here
        logger.info("Test generation not yet implemented")

        return 0

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
