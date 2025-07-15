"""PDF file parser for ATG."""
from pathlib import Path
from typing import List, Optional

from PyPDF2 import PdfReader

from . import BaseParser


class PdfParser(BaseParser):
    """Parser for PDF documents (.pdf)."""

    @classmethod
    def supported_formats(cls) -> tuple[str, ...]:
        """Get the file extensions supported by this parser.

        Returns:
            A tuple of supported file extensions.
        """
        return (".pdf",)

    def _extract_text_from_page(self, page) -> str:
        """Extract text from a single PDF page.

        Args:
            page: A page object from PyPDF2.

        Returns:
            Extracted text from the page.
        """
        try:
            return page.extract_text() or ""
        except Exception as e:
            print(f"Warning: Could not extract text from page: {e}")
            return ""

    def _extract_metadata(self, reader) -> str:
        """Extract metadata from the PDF.

        Args:
            reader: The PDF reader object.

        Returns:
            Formatted metadata as a string.
        """
        metadata = []
        if info := reader.metadata:
            if title := info.get("/Title"):
                metadata.append(f"Title: {title}")
            if author := info.get("/Author"):
                metadata.append(f"Author: {author}")
            if subject := info.get("/Subject"):
                metadata.append(f"Subject: {subject}")
            if keywords := info.get("/Keywords"):
                metadata.append(f"Keywords: {keywords}")
        return "\n".join(metadata) if metadata else ""

    def parse(self, file_path: Path) -> str:
        """Parse a PDF file and return its content as plain text.

        Args:
            file_path: Path to the PDF file to parse.

        Returns:
            The parsed content as plain text.

        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If the file cannot be accessed.
            ValueError: If there's an error parsing the PDF.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, "rb") as file:
                reader = PdfReader(file)

                # Extract metadata
                metadata = self._extract_metadata(reader)

                # Extract text from each page
                pages_text = []
                for page_num, page in enumerate(reader.pages, 1):
                    page_text = self._extract_text_from_page(page)
                    if page_text.strip():
                        pages_text.append(f"--- Page {page_num} ---\n{page_text}")

                # Combine metadata and content
                content_parts = []
                if metadata:
                    content_parts.append(f"--- Document Metadata ---\n{metadata}")
                if pages_text:
                    content_parts.append("\n\n".join(pages_text))

                return "\n\n".join(content_parts)

        except Exception as e:
            raise ValueError(f"Error parsing PDF file {file_path}: {str(e)}")
