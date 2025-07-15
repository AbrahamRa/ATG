"""Document parsers for ATG.

This module contains parsers for different document formats.
"""
from pathlib import Path
from typing import Optional, Protocol, runtime_checkable, Type, Dict, TypeVar

T = TypeVar("T", bound="BaseParser")


@runtime_checkable
class BaseParser(Protocol):
    """Base interface for all document parsers.

    All document parsers must implement this interface.
    """

    @classmethod
    def supported_formats(cls) -> tuple[str, ...]:
        """Get the file extensions supported by this parser.

        Returns:
            A tuple of supported file extensions (including the dot, e.g. '.txt').
        """
        ...

    def parse(self, file_path: Path) -> str:
        """Parse the document and return its content as a string.

        Args:
            file_path: Path to the document to parse.

        Returns:
            The parsed content as a string.
        """
        ...

    @classmethod
    def can_parse(cls, file_path: Path) -> bool:
        """Check if this parser can parse the given file.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if this parser can parse the file, False otherwise.
        """
        return file_path.suffix.lower() in cls.supported_formats()


# Import all parser implementations
from .text_parser import TextParser
from .markdown_parser import MarkdownParser
from .docx_parser import DocxParser
from .pdf_parser import PdfParser

# Map of file extensions to their respective parser classes
PARSERS: Dict[str, Type[BaseParser]] = {
    ".txt": TextParser,
    ".md": MarkdownParser,
    ".markdown": MarkdownParser,
    ".docx": DocxParser,
    ".pdf": PdfParser,
}


def get_parser(file_path: Path) -> BaseParser:
    """Get the appropriate parser for the given file.

    Args:
        file_path: Path to the file to parse.

    Returns:
        An instance of the appropriate parser.

    Raises:
        ValueError: If no parser is available for the file type.
    """
    ext = file_path.suffix.lower()
    if ext not in PARSERS:
        raise ValueError(f"No parser available for file type: {ext}")
    return PARSERS[ext]()
