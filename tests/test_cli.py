"""Tests for the command-line interface."""
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from atg.main import main as cli_main


def test_cli_help(capsys):
    """Test the CLI help output."""
    with patch.object(sys, "argv", ["atg", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            cli_main()
        assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert "ATG - Automated Test Generator" in captured.out
    assert "--help" in captured.out


def test_cli_version(capsys):
    """Test the version flag."""
    with patch.object(sys, "argv", ["atg", "--version"]):
        with pytest.raises(SystemExit) as exc_info:
            cli_main()
        assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert "atg" in captured.out


@patch("atg.main.TestGenerator")
@patch("atg.main.get_parser_for_file")
@patch("builtins.open", new_callable=MagicMock)
@patch("json.dump")
@patch("atg.main.Path")
def test_cli_single_file(
    mock_path, mock_json_dump, mock_open, mock_get_parser, mock_test_generator, tmp_path
):
    """Test CLI with a single input file."""
    # Setup mock for input file
    mock_file = MagicMock()
    mock_file.is_file.return_value = True
    mock_file.exists.return_value = True
    mock_file.suffix = ".py"

    # Setup mock for output directory
    mock_output = MagicMock()
    mock_output.is_dir.return_value = True

    # Configure Path mock to return appropriate values
    def path_side_effect(path):
        if str(path) == "test_file.py":
            return mock_file
        return mock_output

    mock_path.side_effect = path_side_effect

    # Setup parser mock
    mock_parser = MagicMock()
    mock_parser.parse.return_value = "Test content"
    mock_get_parser.return_value = mock_parser

    # Setup generator mock
    mock_generator = MagicMock()
    mock_generator.generate_test_cases.return_value = [
        {"content": "def test_example():\n    assert True"}
    ]
    mock_test_generator.return_value = mock_generator

    # Run CLI
    with patch.object(sys, "argv", ["atg", "test_file.py"]):
        result = cli_main()

    # Verify results
    assert result == 0  # Success exit code
    mock_parser.parse.assert_called_once()
    mock_generator.generate_test_cases.assert_called_once()


@patch("atg.main.TestGenerator")
@patch("atg.main.get_parser_for_file")
@patch("builtins.open", new_callable=MagicMock)
@patch("json.dump")
def test_cli_directory(
    mock_json_dump, mock_open, mock_get_parser, mock_test_generator, tmp_path
):
    """Test CLI with a directory input."""
    # Setup test directory with files
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    file1 = test_dir / "file1.py"
    file1.write_text("def func1(): pass")

    file2 = test_dir / "file2.py"
    file2.write_text("def func2(): pass")

    # Setup mocks
    mock_parser = MagicMock()
    mock_parser.parse.return_value = "Test content"
    mock_get_parser.return_value = mock_parser

    mock_generator = MagicMock()
    mock_generator.generate_test_cases.return_value = [
        {"content": "def test_func():\n    assert True"}
    ]
    mock_test_generator.return_value = mock_generator

    # Run CLI
    with patch.object(sys, "argv", ["atg", str(test_dir), "-o", str(tmp_path), "-v"]):
        result = cli_main()

    # Verify results
    assert result == 0
    assert mock_parser.parse.call_count == 2  # Called for each file
    assert mock_generator.generate_test_cases.call_count == 2


@patch("atg.main.Path")
def test_cli_missing_source(mock_path, capsys):
    """Test CLI with missing source file."""
    # Setup mock to simulate missing file
    mock_file = MagicMock()
    mock_file.exists.return_value = False
    mock_path.return_value = mock_file

    with patch.object(sys, "argv", ["atg", "nonexistent_file.py"]):
        result = cli_main()

    assert result == 1  # Non-zero exit code for error


@patch("atg.main.TestGenerator")
@patch("atg.main.get_parser_for_file")
@patch("atg.main.Path")
def test_cli_api_error(mock_path, mock_get_parser, mock_test_generator, tmp_path):
    """Test handling of API errors."""
    # Setup mock for input file
    mock_file = MagicMock()
    mock_file.is_file.return_value = True
    mock_file.exists.return_value = True
    mock_file.suffix = ".py"

    # Setup mock for output directory
    mock_output = MagicMock()
    mock_output.is_dir.return_value = True

    # Configure Path mock to return appropriate values
    def path_side_effect(path):
        if str(path) == "test_file.py":
            return mock_file
        return MagicMock()

    mock_path.side_effect = path_side_effect

    # Setup parser mock
    mock_parser = MagicMock()
    mock_parser.parse.return_value = "Test content"
    mock_get_parser.return_value = mock_parser

    # Setup generator to raise error
    mock_generator = MagicMock()
    mock_generator.generate_test_cases.side_effect = Exception("API error")
    mock_test_generator.return_value = mock_generator

    # Run CLI
    with patch.object(sys, "argv", ["atg", "test_file.py"]):
        result = cli_main()

    # Verify error handling
    assert result == 1  # Non-zero exit code for error


@patch("atg.main.process_file")
@patch("atg.main.Path")
@patch.dict("os.environ", {"OPENAI_API_KEY": "test-api-key"})
def test_cli_quiet_mode(mock_path, mock_process_file, capsys):
    """Test quiet mode suppresses output."""
    # Setup mock for input file
    mock_file = MagicMock()
    mock_file.is_file.return_value = True
    mock_file.exists.return_value = True
    mock_file.suffix = ".py"

    # Setup mock for output directory
    mock_output = MagicMock()
    mock_output.is_dir.return_value = True

    # Configure Path mock to return appropriate values
    def path_side_effect(path):
        if str(path) == "test.py":
            return mock_file
        return mock_output

    mock_path.side_effect = path_side_effect

    # Setup mock for process_file to return a dictionary
    mock_process_file.return_value = {
        "status": "success",
        "file": "test.py",
        "output": "test_output.py",
    }

    # Run CLI with quiet flag
    with patch.object(sys, "argv", ["atg", "test.py", "--quiet"]):
        result = cli_main()

    # Verify the function completed successfully
    assert result == 0


@patch("atg.main.TestGenerator")
@patch("atg.main.get_parser_for_file")
@patch("builtins.open", new_callable=MagicMock)
@patch("json.dump")
def test_cli_custom_model_and_temperature(
    mock_json_dump, mock_open, mock_get_parser, mock_test_generator, tmp_path
):
    """Test CLI with custom model and temperature."""
    # Setup test file
    test_file = tmp_path / "test_file.py"
    test_file.write_text("def example(): pass")

    # Setup mocks
    mock_parser = MagicMock()
    mock_parser.parse.return_value = "Test content"
    mock_get_parser.return_value = mock_parser

    mock_generator = MagicMock()
    mock_generator.generate_test_cases.return_value = [
        {"content": "def test_example(): pass"}
    ]
    mock_test_generator.return_value = mock_generator

    # Run CLI with custom model and temperature
    with patch.object(
        sys,
        "argv",
        [
            "atg",
            str(test_file),
            "--model",
            "gpt-3.5-turbo",
            "--temperature",
            "0.9",
            "--framework",
            "unittest",
        ],
    ):
        result = cli_main()

    # Verify custom parameters were used
    assert result == 0
    mock_test_generator.assert_called_once_with(
        model_name="gpt-3.5-turbo", temperature=0.9
    )
    mock_generator.generate_test_cases.assert_called_once_with(
        "Test content", "unittest"
    )
