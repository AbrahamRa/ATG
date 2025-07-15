"""Markdown file parser for ATG."""
from pathlib import Path
from typing import Optional, cast

import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

from . import BaseParser


class MarkdownExtractor(Treeprocessor):
    """Custom Markdown processor to extract text content."""

    def run(self, root):
        """Process the markdown tree and return plain text content.

        Args:
            root: The root element of the markdown tree.

        Returns:
            The root element (modified in place).
        """
        # This processor doesn't modify the tree, just returns it
        return root


class MarkdownExtension(Extension):
    """Markdown extension to customize the parsing process."""

    def extendMarkdown(self, md):
        """Register the extractor with the markdown instance.

        Args:
            md: The markdown instance to extend.
        """
        md.treeprocessors.register(MarkdownExtractor(md), "atg_extractor", 0)


class MarkdownParser(BaseParser):
    """Parser for Markdown files (.md, .markdown)."""

    @classmethod
    def supported_formats(cls) -> tuple[str, ...]:
        """Get the file extensions supported by this parser.

        Returns:
            A tuple of supported file extensions.
        """
        return (".md", ".markdown")

    def parse(self, file_path: Path) -> str:
        """Parse a Markdown file and return its content as plain text.

        Args:
            file_path: Path to the Markdown file to parse.

        Returns:
            The parsed content as plain text.

        Raises:
            UnicodeDecodeError: If the file cannot be decoded as UTF-8.
            markdown.MarkdownException: If there's an error parsing the Markdown.
        """
        # Read the file content
        content = file_path.read_text(encoding="utf-8")

        # Configure markdown with our custom extension
        md = markdown.Markdown(extensions=[MarkdownExtension()])

        # Convert markdown to HTML
        html = md.convert(content)

        # For now, we'll return the raw HTML, but we might want to convert it to plain text
        # or process it further based on our needs
        return html
