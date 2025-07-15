"""Tests for the keyword mapping module."""
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import pytest

from atg.config import Config
from atg.keywords import KeywordMapper


def test_keyword_mapper_initialization():
    """Test KeywordMapper initialization."""
    config = Config()
    mapper = KeywordMapper(config)

    assert isinstance(mapper.keyword_library, dict)
    assert isinstance(mapper.unmapped_keywords, set)


def test_load_keyword_library_existing_file():
    """Test loading keyword library from existing file."""
    config = Config()

    # Create temporary directory and file
    with TemporaryDirectory() as tmpdir:
        config.set("keyword_library_path", os.path.join(tmpdir, "keywords.json"))

        # Create test library file with correct structure
        test_library = {"click button": {"keyword": "Click Button", "confidence": 1.0}}
        with open(config.get("keyword_library_path"), "w") as f:
            json.dump(test_library, f)

        # Create mapper with fresh config
        mapper = KeywordMapper(config)
        assert mapper.keyword_library == test_library

        # Verify no additional mappings were added
        assert len(mapper.keyword_library) == 1


def test_load_keyword_library_nonexistent_file():
    """Test loading keyword library when file doesn't exist."""
    config = Config()
    config.set("keyword_library_path", "nonexistent.json")

    mapper = KeywordMapper(config)
    assert mapper.keyword_library == {}

    # Verify that empty library doesn't contain any mappings
    assert len(mapper.keyword_library) == 0


def test_save_keyword_library():
    """Test saving keyword library to file."""
    config = Config()

    # Create temporary directory
    with TemporaryDirectory() as tmpdir:
        config.set("keyword_library_path", os.path.join(tmpdir, "keywords.json"))
        mapper = KeywordMapper(config)

        # Add some keywords
        mapper.keyword_library["click button"] = {
            "keyword": "Click Button",
            "confidence": 1.0,
        }
        mapper._save_keyword_library()

        # Verify file was created and has correct content
        assert os.path.exists(config.get("keyword_library_path"))
        with open(config.get("keyword_library_path"), "r") as f:
            saved_data = json.load(f)
            assert saved_data == mapper.keyword_library

        # Verify saved data matches expected structure
        assert isinstance(saved_data, dict)
        assert len(saved_data) == 1
        assert "click button" in saved_data
        assert saved_data["click button"]["keyword"] == "Click Button"
        assert saved_data["click button"]["confidence"] == 1.0


@patch("openai.OpenAI")
def test_map_action_to_keyword(mock_openai):
    """Test mapping action to keyword."""
    # Mock the OpenAI client response
    mock_client = mock_openai.return_value
    mock_chat = mock_client.chat.completions.create.return_value
    mock_chat.choices = [
        type(
            "obj",
            (),
            {
                "message": type(
                    "msg",
                    (),
                    {"content": '{"keyword": "Click Button", "confidence": 0.8}'},
                )
            },
        )
    ]

    config = Config()
    config.set("keyword_library_path", "test_keywords.json")
    config.disable_validation()  # Disable validation for testing
    mapper = KeywordMapper(config)

    # Test existing mapping
    mapper.keyword_library["click button"] = {
        "keyword": "Click Button",
        "confidence": 1.0,
    }

    # Test existing mapping
    keyword, confidence = mapper.map_action_to_keyword("click button")
    assert keyword == "Click Button"
    assert confidence == 1.0

    # Test new mapping - this will use the mock
    keyword, confidence = mapper.map_action_to_keyword("type text")
    assert keyword == "Click Button"
    assert confidence == 0.8

    # Verify the new mapping was added to the library
    assert len(mapper.keyword_library) == 2
    assert "type text" in mapper.keyword_library
    assert mapper.keyword_library["type text"]["keyword"] == "Click Button"
    assert mapper.keyword_library["type text"]["confidence"] == 0.8


def test_get_unmapped_keywords():
    """Test getting unmapped keywords."""
    config = Config()
    mapper = KeywordMapper(config)

    # Add some unmapped keywords
    mapper.unmapped_keywords.add("type text")
    mapper.unmapped_keywords.add("select dropdown")

    assert mapper.get_unmapped_keywords() == {"type text", "select dropdown"}


def test_add_feedback():
    """Test adding user feedback."""
    config = Config()
    mapper = KeywordMapper(config)

    # Add feedback
    mapper.add_feedback("type text", "Type Text", 0.9)

    assert mapper.keyword_library["type text"] == {
        "keyword": "Type Text",
        "confidence": 0.9,
    }
    assert "type text" not in mapper.unmapped_keywords


def test_generate_test_case():
    """Test generating test case line."""
    config = Config()
    mapper = KeywordMapper(config)

    # Test with existing mapping and high confidence
    mapper.keyword_library["click button"] = {
        "keyword": "Click Button",
        "confidence": 1.0,
    }
    config.min_confidence = 0.9

    test_case = mapper.generate_test_case("click button")
    assert test_case == "    Click Button"

    # Test with existing mapping but low confidence
    mapper.keyword_library["type text"] = {"keyword": "Type Text", "confidence": 0.7}
    test_case = mapper.generate_test_case("type text")
    assert test_case == ""  # Empty string since confidence is below threshold

    # Test with no mapping
    test_case = mapper.generate_test_case("select dropdown")
    assert test_case == ""
