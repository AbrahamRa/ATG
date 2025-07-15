"""Text file parser for ATG."""
from pathlib import Path

from . import BaseParser


class TextParser(BaseParser):
    """Parser for plain text files (.txt)."""

    @classmethod
    def supported_formats(cls) -> tuple[str, ...]:
        """Get the file extensions supported by this parser.

        Returns:
            A tuple of supported file extensions.
        """
        return (".txt",)

    def parse(self, file_path: Path) -> str:
        """Parse a text file and return its content.

        Args:
            file_path: Path to the text file to parse.

        Returns:
            The content of the text file as a string.

        Raises:
            UnicodeDecodeError: If the file cannot be decoded as UTF-8.
        """
        return file_path.read_text(encoding="utf-8")
