"""Tests for document parsers."""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from atg.ingestion.parsers import (
    BaseParser,
    TextParser,
    MarkdownParser,
    DocxParser,
    PdfParser,
    get_parser,
    PARSERS,
)


class TestBaseParser:
    """Tests for the BaseParser protocol."""

    def test_base_parser_has_required_methods(self):
        """Test that BaseParser has the required methods."""
        # Check that BaseParser has the required methods
        assert hasattr(BaseParser, "supported_formats")
        assert hasattr(BaseParser, "parse")
        assert hasattr(BaseParser, "can_parse")

    def test_base_parser_required_methods(self):
        """Test that BaseParser has the required methods."""
        assert hasattr(BaseParser, "supported_formats")
        assert hasattr(BaseParser, "parse")
        assert hasattr(BaseParser, "can_parse")


class TestTextParser:
    """Tests for the TextParser class."""

    @pytest.fixture
    def text_parser(self) -> TextParser:
        """Return a TextParser instance."""
        return TextParser()

    def test_supported_formats(self, text_parser: TextParser):
        """Test supported formats."""
        assert text_parser.supported_formats() == (".txt",)

    def test_parse(self, text_parser: TextParser, tmp_path: Path):
        """Test parsing a text file."""
        test_file = tmp_path / "test.txt"
        test_content = "Hello, world!\nThis is a test."
        test_file.write_text(test_content)

        result = text_parser.parse(test_file)
        assert result == test_content

    def test_can_parse(self, text_parser: TextParser, tmp_path: Path):
        """Test can_parse method."""
        txt_file = tmp_path / "test.txt"
        txt_file.touch()
        assert text_parser.can_parse(txt_file) is True

        md_file = tmp_path / "test.md"
        md_file.touch()
        assert text_parser.can_parse(md_file) is False


class TestMarkdownParser:
    """Tests for the MarkdownParser class."""

    @pytest.fixture
    def markdown_parser(self) -> MarkdownParser:
        """Return a MarkdownParser instance."""
        return MarkdownParser()

    def test_supported_formats(self, markdown_parser: MarkdownParser):
        """Test supported formats."""
        assert set(markdown_parser.supported_formats()) == {".md", ".markdown"}

    @patch("markdown.Markdown")
    def test_parse(
        self, mock_markdown, markdown_parser: MarkdownParser, tmp_path: Path
    ):
        """Test parsing a markdown file."""
        test_file = tmp_path / "test.md"
        test_content = "# Heading\n\nThis is a test."
        test_file.write_text(test_content)

        # Mock the markdown conversion
        mock_md_instance = MagicMock()
        mock_md_instance.convert.return_value = "<h1>Heading</h1><p>This is a test.</p>"
        mock_markdown.return_value = mock_md_instance

        result = markdown_parser.parse(test_file)
        assert "<h1>Heading</h1>" in result
        assert "<p>This is a test.</p>" in result
        mock_md_instance.convert.assert_called_once_with(test_content)


class TestDocxParser:
    """Tests for the DocxParser class."""

    @pytest.fixture
    def docx_parser(self) -> DocxParser:
        """Return a DocxParser instance."""
        return DocxParser()

    def test_supported_formats(self, docx_parser: DocxParser):
        """Test supported formats."""
        assert docx_parser.supported_formats() == (".docx",)

    @patch("docx.Document")
    def test_parse(self, mock_document, docx_parser: DocxParser, tmp_path: Path):
        """Test parsing a DOCX file."""
        test_file = tmp_path / "test.docx"
        test_file.touch()

        # Mock the document
        mock_doc = MagicMock()
        mock_paragraph = MagicMock()
        mock_paragraph.text = "This is a test paragraph."
        mock_doc.paragraphs = [mock_paragraph]
        mock_doc.tables = []
        mock_doc.sections = []
        mock_document.return_value = mock_doc

        result = docx_parser.parse(test_file)
        assert "This is a test paragraph." in result


class TestPdfParser:
    """Tests for the PdfParser class."""

    @pytest.fixture
    def pdf_parser(self) -> PdfParser:
        """Return a PdfParser instance."""
        return PdfParser()

    def test_supported_formats(self, pdf_parser: PdfParser):
        """Test supported formats."""
        assert pdf_parser.supported_formats() == (".pdf",)

    def test_parse(self, pdf_parser: PdfParser, tmp_path: Path):
        """Test parsing a PDF file with a minimal valid PDF."""
        # Create a minimal valid PDF file
        test_file = tmp_path / "test.pdf"

        # This is a minimal PDF file with one empty page
        minimal_pdf = (
            b"%PDF-1.4\n"
            b"1 0 obj\n"
            b"<< /Type /Catalog /Pages 2 0 R >>\n"
            b"endobj\n"
            b"2 0 obj\n"
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>\n"
            b"endobj\n"
            b"3 0 obj\n"
            b"<< /Type /Page /Parent 2 0 R /Resources << >> /MediaBox [0 0 612 792] >>\n"
            b"endobj\n"
            b"xref\n"
            b"0 4\n"
            b"0000000000 65535 f \n"
            b"0000000009 00000 n \n"
            b"0000000051 00000 n \n"
            b"0000000100 00000 n \n"
            b"trailer\n"
            b"<< /Size 4 /Root 1 0 R >>\n"
            b"startxref\n"
            b"184\n"
            b"%%EOF"
        )

        test_file.write_bytes(minimal_pdf)

        # Test that parsing succeeds
        result = pdf_parser.parse(test_file)
        assert isinstance(result, str)


def test_get_parser():
    """Test the get_parser function."""
    # Test with supported formats
    assert isinstance(get_parser(Path("test.txt")), TextParser)
    assert isinstance(get_parser(Path("test.md")), MarkdownParser)
    assert isinstance(get_parser(Path("test.docx")), DocxParser)
    assert isinstance(get_parser(Path("test.pdf")), PdfParser)

    # Test with unsupported format
    with pytest.raises(ValueError, match="No parser available for file type: .unknown"):
        get_parser(Path("test.unknown"))
