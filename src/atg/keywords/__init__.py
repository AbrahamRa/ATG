"""Keyword mapping module for ATG.

This module provides functionality to map extracted actions from documentation
to appropriate Robot Framework keywords.
"""
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import os
import json

from atg.config import Config
from atg.ai import TestGenerator


class KeywordMapper:
    """Maps extracted actions to Robot Framework keywords."""

    def __init__(self, config: Config):
        """Initialize the keyword mapper.

        Args:
            config: Configuration object containing paths and settings
        """
        self.config = config
        self.keyword_library = {}
        self.unmapped_keywords: Set[str] = set()

        # Initialize min_confidence from config
        self.min_confidence = self.config.get("min_confidence", 0.8)

        # Load library if path is set
        library_path = self.config.get("keyword_library_path")
        if library_path:
            self._load_keyword_library()

    def _load_keyword_library(self):
        """Load the keyword library from resource files."""
        library_path = self.config.get("keyword_library_path")
        if library_path:
            library_path = Path(library_path)
            # Ensure parent directory exists
            library_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                if library_path.exists():
                    with open(library_path, "r", encoding="utf-8") as f:
                        self.keyword_library = json.load(f)
                else:
                    # Initialize empty library
                    self.keyword_library = {}
            except Exception as e:
                print(f"Warning: Failed to load keyword library: {e}")
                self.keyword_library = {}
        else:
            # Initialize empty library
            self.keyword_library = {}

    def _save_keyword_library(self):
        """Save the updated keyword library."""
        library_path = self.config.get("keyword_library_path")
        if not library_path:
            return False

        library_path = Path(library_path)
        # Ensure parent directory exists
        library_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            # Create a temporary copy of the library to save
            temp_library = self.keyword_library.copy()
            with open(library_path, "w", encoding="utf-8") as f:
                json.dump(temp_library, f, indent=2)
            return True
        except Exception as e:
            print(f"Warning: Failed to save keyword library: {e}")
            return False

    def map_action_to_keyword(self, action: str) -> Tuple[Optional[str], float]:
        """Map an action to the most appropriate Robot Framework keyword.

        Args:
            action: The action extracted from documentation

        Returns:
            Tuple containing (keyword, confidence) or (None, 0) if no match
        """
        # Check if action is already in library
        if action in self.keyword_library:
            return (
                self.keyword_library[action]["keyword"],
                self.keyword_library[action]["confidence"],
            )

        # Use AI to suggest best keyword match
        try:
            generator = TestGenerator(
                model_name=self.config.get("model_name", "gpt-4"),
                temperature=self.config.get("temperature", 0.7),
            )
            generator.initialize()  # Ensure client is initialized

            # Prepare the prompt with existing library
            library_keywords = list(self.keyword_library.keys())
            prompt = f"""
            You are a Robot Framework test case generator.
            Given the action: "{action}"
            Suggest the most appropriate Robot Framework keyword.
            Return a JSON object with the following structure:
            {{"keyword": "KeywordName", "confidence": 0.0 to 1.0}}
            """

            response = generator.generate_test_cases(prompt, "robot")
            if response and isinstance(response, list) and len(response) > 0:
                # Get the first response
                first_response = response[0]
                if isinstance(first_response, dict) and "content" in first_response:
                    # Parse the JSON response
                    try:
                        result = json.loads(first_response["content"])
                        if (
                            isinstance(result, dict)
                            and "keyword" in result
                            and "confidence" in result
                        ):
                            suggested_keyword = result["keyword"].strip()
                            confidence = float(result["confidence"])

                            # Add to library with confidence score
                            self.keyword_library[action] = {
                                "keyword": suggested_keyword,
                                "confidence": confidence,
                            }
                            if self._save_keyword_library():
                                return suggested_keyword, confidence
                            else:
                                print(
                                    f"Warning: Failed to save keyword mapping for action '{action}'"
                                )
                                return None, 0.0
                    except (json.JSONDecodeError, ValueError):
                        # If JSON parsing fails, fall back to simple text response
                        suggested_keyword = first_response["content"].strip()
                        confidence = (
                            0.8  # Default confidence for AI-generated suggestions
                        )

                        self.keyword_library[action] = {
                            "keyword": suggested_keyword,
                            "confidence": confidence,
                        }
                        if self._save_keyword_library():
                            return suggested_keyword, confidence
                        else:
                            print(
                                f"Warning: Failed to save keyword mapping for action '{action}'"
                            )
                            return None, 0.0

            return None, 0.0

        except Exception as e:
            self.unmapped_keywords.add(action)
            print(
                f"Warning: Failed to generate keyword for action '{action}': {str(e)}"
            )
            return None, 0.0

    def get_unmapped_keywords(self) -> Set[str]:
        """Get set of unmapped keywords that need human review."""
        return self.unmapped_keywords

    def add_feedback(self, action: str, keyword: str, confidence: float):
        """Add user feedback to improve keyword mapping.

        Args:
            action: The original action
            keyword: The correct keyword mapping
            confidence: User confidence in the mapping (0.0 to 1.0)
        """
        self.keyword_library[action] = {"keyword": keyword, "confidence": confidence}
        self._save_keyword_library()
        if action in self.unmapped_keywords:
            self.unmapped_keywords.remove(action)

    def generate_test_case(self, action: str) -> str:
        """Generate a test case line for the given action.

        Args:
            action: The action to generate a test case for

        Returns:
            A Robot Framework test case line or empty string if no mapping
        """
        keyword, confidence = self.map_action_to_keyword(action)
        if keyword and confidence >= self.min_confidence:
            return f"    {keyword}"
        return ""
