"""Document ingestion module for ATG.

This module provides functionality to ingest and parse various document formats
into a structured format for test generation.
"""
from pathlib import Path
from typing import Dict, Optional, Protocol, Type, Union, TypeVar

from atg.ingestion.parsers import (
    BaseParser,
    DocxParser,
    MarkdownParser,
    PdfParser,
    TextParser,
)

# Type variable for document parsers
T = TypeVar("T", bound="BaseParser")

# Map file extensions to their respective parser classes
PARSERS: Dict[str, Type[BaseParser]] = {
    ".txt": TextParser,
    ".md": MarkdownParser,
    ".markdown": MarkdownParser,
    ".docx": DocxParser,
    ".pdf": PdfParser,
}


class DocumentParser(Protocol):
    """Protocol for document parsers.

    All document parsers must implement this interface.
    """

    def parse(self, file_path: Union[str, Path]) -> str:
        """Parse the document and return its content as a string.

        Args:
            file_path: Path to the document to parse.

        Returns:
            The parsed content as a string.
        """
        ...


def get_parser(file_path: Union[str, Path]) -> Type[BaseParser]:
    """Get the appropriate parser class for the given file.

    Args:
        file_path: Path to the file to parse.

    Returns:
        The parser class for the file type.

    Raises:
        ValueError: If no parser is available for the file type.
    """
    file_path = Path(file_path)
    ext = file_path.suffix.lower()
    if ext not in PARSERS:
        raise ValueError(f"No parser available for file type: {ext}")

    return PARSERS[ext]


def get_parser_for_file(file_path: Union[str, Path]) -> Optional[BaseParser]:
    """Get an instance of the appropriate parser for the given file.

    Args:
        file_path: Path to the file to parse.

    Returns:
        An instance of the appropriate parser, or None if no parser is available.
    """
    try:
        parser_class = get_parser(file_path)
        return parser_class()
    except ValueError:
        return None


def parse_document(file_path: Union[str, Path]) -> str:
    """Parse a document and return its content.

    Args:
        file_path: Path to the document to parse.

    Returns:
        The parsed content as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If no parser is available for the file type.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    parser = get_parser_for_file(file_path)
    if not parser:
        raise ValueError(f"No parser available for file: {file_path}")

    return parser.parse(file_path)


__all__ = [
    "BaseParser",
    "DocxParser",
    "MarkdownParser",
    "PdfParser",
    "TextParser",
    "DocumentParser",
    "get_parser",
    "get_parser_for_file",
    "parse_document",
]
