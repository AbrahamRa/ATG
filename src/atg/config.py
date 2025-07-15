"""Configuration management for ATG."""
import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration manager for ATG."""

    def __init__(self):
        """Initialize the configuration with default values."""
        # Default configuration
        self._config = {
            "openai_api_key": os.environ.get("OPENAI_API_KEY"),
            "model_name": "gpt-4",
            "temperature": 0.7,
            "test_framework": "pytest",
            "output_dir": "tests/generated",
            "keyword_library_path": None,  # Will be set by user or tests
        }

    def get(self, key: str, default=None) -> any:
        """Get a configuration value.

        Args:
            key: The configuration key to retrieve.
            default: Default value if key doesn't exist.

        Returns:
            The configuration value or default if not found.
        """
        value = self._config.get(key, default)
        if key == "keyword_library_path":
            return value
        return value

    def set(self, key: str, value: any) -> None:
        """Set a configuration value.

        Args:
            key: The configuration key to set.
            value: The value to set.
        """
        # For keyword_library_path, ensure we store a string
        if key == "keyword_library_path":
            if value is not None:
                value = str(value)
        self._config[key] = value

    def load_from_env(self) -> None:
        """Load configuration from environment variables."""
        self._config["openai_api_key"] = os.environ.get("OPENAI_API_KEY")

        if model_name := os.environ.get("ATG_MODEL_NAME"):
            self._config["model_name"] = model_name

        if temp := os.environ.get("ATG_TEMPERATURE"):
            try:
                self._config["temperature"] = float(temp)
            except (ValueError, TypeError):
                pass

        if framework := os.environ.get("ATG_TEST_FRAMEWORK"):
            self._config["test_framework"] = framework

    def validate(self) -> bool:
        """Validate the current configuration.

        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        if not self._config["openai_api_key"]:
            return False
        return True

    def disable_validation(self) -> None:
        """Temporarily disable validation for testing purposes."""
        self._config["_validation_disabled"] = True

    def _is_validation_disabled(self) -> bool:
        """Check if validation is disabled."""
        return self._config.get("_validation_disabled", False)


# Global configuration instance
config = Config()

# Load configuration from environment variables on import
config.load_from_env()
