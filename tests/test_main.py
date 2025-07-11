"""Tests for the main module."""
import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src import main


def test_parse_args():
    """Test argument parsing."""
    # Test with no arguments should fail (source is required)
    with pytest.raises(SystemExit):
        main.parse_args([])

    # Test with required arguments
    args = main.parse_args(["source_file.py"])
    assert args.source == Path("source_file.py")
    assert args.output == Path("tests")
    assert args.verbose == 0

    # Test with all arguments
    args = main.parse_args(["-v", "-o", "test_output", "source_file.py"])
    assert args.verbose == 1
    assert args.output == Path("test_output")


def test_setup_logging():
    """Test logging setup."""
    # Test with different verbosity levels
    for verbosity, expected_level in [
        (0, logging.WARNING),
        (1, logging.INFO),
        (2, logging.DEBUG),
        (3, logging.DEBUG),  # Shouldn't go below DEBUG
    ]:
        with patch("logging.basicConfig") as mock_basic_config:
            main.setup_logging(verbosity)
            mock_basic_config.assert_called_once()
            assert mock_basic_config.call_args[1]["level"] == expected_level


class TestMain:
    """Test the main function."""

    @patch("src.main.parse_args")
    @patch("src.main.setup_logging")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.exists", return_value=True)
    def test_main_success(
        self,
        mock_exists,
        mock_mkdir,
        mock_setup_logging,
        mock_parse_args,
        caplog,
    ):
        """Test successful execution of main."""
        # Setup mocks
        mock_args = MagicMock()
        mock_args.source = Path("source.py")
        mock_args.output = Path("tests")
        mock_args.verbose = 0
        mock_parse_args.return_value = mock_args

        # Run main
        with caplog.at_level(logging.INFO):
            result = main.main()

        # Verify results
        assert result == 0
        mock_setup_logging.assert_called_once_with(0)
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        assert "Starting ATG" in caplog.text
        assert "Processing: source.py" in caplog.text

    @patch("src.main.parse_args")
    def test_main_source_not_found(self, mock_parse_args, caplog):
        """Test main when source file doesn't exist."""
        # Setup mocks
        mock_args = MagicMock()
        mock_args.source = Path("nonexistent.py")
        mock_args.source.exists.return_value = False
        mock_args.verbose = 0
        mock_parse_args.return_value = mock_args

        # Run main
        with caplog.at_level(logging.ERROR):
            result = main.main()

        # Verify results
        assert result == 1
        assert "Source not found" in caplog.text

    @patch("src.main.parse_args")
    def test_main_exception(self, mock_parse_args, caplog):
        """Test main when an exception occurs."""
        # Setup mocks to raise an exception
        mock_parse_args.side_effect = Exception("Test error")

        # Run main
        with caplog.at_level(logging.ERROR):
            result = main.main()

        # Verify results
        assert result == 1
        assert "An error occurred" in caplog.text


if __name__ == "__main__":
    pytest.main(["-v", __file__])
