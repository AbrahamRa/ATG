"""Tests for the main module."""
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from atg.main import main, parse_args, setup_logging


def test_parse_args():
    """Test argument parsing."""
    # Test with no arguments should fail (source is required)
    with pytest.raises(SystemExit):
        parse_args([])

    # Test with required arguments
    args = parse_args(["source_file.py"])
    assert args.source == Path("source_file.py")
    assert args.output == Path("tests")
    assert args.verbose == 0

    # Test with all arguments
    args = parse_args(["-v", "-o", "test_output", "source_file.py"])
    assert args.verbose == 1
    assert args.output == Path("test_output")


def test_setup_logging():
    """Test logging setup."""
    # Test with different verbosity levels
    # The formula in setup_logging is: level = max(3 - verbosity, 0) * 10
    for verbosity, expected_level in [
        (0, 30),  # 3 * 10 = 30 (WARNING)
        (1, 20),  # 2 * 10 = 20 (INFO)
        (2, 10),  # 1 * 10 = 10 (DEBUG)
        (3, 0),  # 0 * 10 = 0 (NOTSET)
    ]:
        with patch("logging.basicConfig") as mock_basic_config:
            setup_logging(verbosity)
            mock_basic_config.assert_called_once()
            assert mock_basic_config.call_args[1]["level"] == expected_level


class TestMain:
    """Test the main function."""

    @patch("atg.main.parse_args")
    @patch("atg.main.setup_logging")
    @patch("atg.main.TestGenerator")
    @patch("atg.main.process_file")
    def test_main_success(
        self,
        mock_process_file,
        mock_test_generator,
        mock_setup_logging,
        mock_parse_args,
        caplog,
    ):
        """Test successful execution of main."""
        # Create a mock for the source path
        mock_source = MagicMock(spec=Path)
        mock_source.is_file.return_value = True
        mock_source.is_dir.return_value = False
        mock_source.__str__.return_value = "source.py"

        # Create a mock for the output path
        mock_output = MagicMock(spec=Path)
        mock_output.__str__.return_value = "tests"

        # Setup mock args
        mock_args = MagicMock()
        mock_args.source = mock_source
        mock_args.output = mock_output
        mock_args.verbose = 0
        mock_args.quiet = False
        mock_args.model = "gpt-4"
        mock_args.temperature = 0.7
        mock_args.framework = "pytest"
        mock_parse_args.return_value = mock_args

        # Mock TestGenerator instance
        mock_generator_instance = MagicMock()
        mock_test_generator.return_value = mock_generator_instance

        # Mock process_file result
        mock_process_file.return_value = {
            "status": "success",
            "file": "source.py",
            "output": "tests/test_source.py",
        }

        # Run main
        with caplog.at_level(logging.INFO):
            result = main(["source.py"])

        # Verify results
        assert result == 0
        mock_setup_logging.assert_called_once_with(0)
        mock_source.mkdir.assert_not_called()  # Should not create source dir
        mock_test_generator.assert_called_once_with(
            model_name=mock_args.model, temperature=mock_args.temperature
        )
        mock_generator_instance.initialize.assert_called_once()
        mock_process_file.assert_called_once_with(
            mock_source, mock_output, mock_generator_instance, mock_args.framework
        )

    @patch("atg.main.parse_args")
    def test_main_source_not_found(self, mock_parse_args, caplog):
        """Test main when source file doesn't exist."""
        # Setup mocks
        source_path = Path("nonexistent.py")
        mock_args = MagicMock()
        mock_args.source = source_path
        mock_args.verbose = 0
        mock_parse_args.return_value = mock_args

        # Make the source path not exist
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = False
            # Run main
            with caplog.at_level(logging.ERROR):
                result = main([str(source_path)])

        # Verify results
        assert result == 1
        assert "not found" in caplog.text.lower()

    @patch("atg.main.parse_args")
    def test_main_exception(self, mock_parse_args, caplog):
        """Test main when an exception occurs."""
        # Setup mocks to raise an exception
        mock_parse_args.side_effect = Exception("Test error")

        # Run main
        with caplog.at_level(logging.ERROR):
            result = main(["test.py"])

        # Verify results
        assert result == 1
        assert "error" in caplog.text.lower()


if __name__ == "__main__":
    pytest.main(["-v", __file__])
