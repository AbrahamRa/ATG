"""Tests for the AI module."""
import pytest
from unittest.mock import MagicMock, patch, ANY
from pathlib import Path

from atg.ai import TestGenerator
from atg.config import config


class TestTestGenerator:
    """Test the TestGenerator class."""

    def test_initialization(self):
        """Test TestGenerator initialization."""
        generator = TestGenerator(model_name="test-model", temperature=0.5)
        assert generator.model_name == "test-model"
        assert generator.temperature == 0.5
        assert generator._client is None

    @patch("openai.OpenAI")
    def test_initialize(self, mock_openai):
        """Test initializing the OpenAI client."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        generator = TestGenerator()
        generator.initialize(api_key="test-api-key")

        mock_openai.assert_called_once_with(api_key="test-api-key")
        assert generator._client == mock_client

    @patch("openai.OpenAI")
    def test_generate_test_cases(self, mock_openai):
        """Test generating test cases."""
        # Setup mock client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()

        mock_message.content = """```python
def test_example():
    assert 1 + 1 == 2
```"""
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        mock_openai.return_value = mock_client

        # Test
        generator = TestGenerator()
        generator.initialize(api_key="test-api-key")

        requirements = "Test requirements"
        test_cases = generator.generate_test_cases(requirements, "pytest")

        # Verify
        assert len(test_cases) == 1
        assert "def test_example" in test_cases[0]["content"]
        mock_client.chat.completions.create.assert_called_once()

    def test_build_prompt(self):
        """Test building the prompt for the AI model."""
        generator = TestGenerator()
        requirements = "Test requirements"
        test_framework = "pytest"

        prompt = generator._build_prompt(requirements, test_framework)

        assert requirements in prompt
        assert test_framework in prompt
        assert "Generate test cases" in prompt

    def test_parse_test_cases(self):
        """Test parsing the AI response into test cases."""
        generator = TestGenerator()
        response = """
        ```python
        def test_one():
            assert 1 == 1

        def test_two():
            assert 2 == 2
        ```
        """

        test_cases = generator._parse_test_cases(response)

        assert (
            len(test_cases) == 1
        )  # Current implementation wraps in a single test case
        assert "def test_one" in test_cases[0]["content"]
        assert "def test_two" in test_cases[0]["content"]


class TestConfig:
    """Test the configuration management."""

    def test_config_defaults(self):
        """Test default configuration values."""
        assert config.get("model_name") == "gpt-4"
        assert config.get("temperature") == 0.7
        assert config.get("test_framework") == "pytest"

    def test_config_set_get(self):
        """Test setting and getting configuration values."""
        config.set("test_key", "test_value")
        assert config.get("test_key") == "test_value"

    @patch.dict(
        "os.environ",
        {
            "OPENAI_API_KEY": "test-env-key",
            "ATG_MODEL_NAME": "test-model",
            "ATG_TEMPERATURE": "0.5",
        },
    )
    def test_load_from_env(self):
        """Test loading configuration from environment variables."""
        config.load_from_env()
        assert config.get("openai_api_key") == "test-env-key"
        assert config.get("model_name") == "test-model"
        assert config.get("temperature") == 0.5

    def test_validate(self):
        """Test configuration validation."""
        # Test with no API key
        config.set("openai_api_key", None)
        assert not config.validate()

        # Test with API key
        config.set("openai_api_key", "test-key")
        assert config.validate()
