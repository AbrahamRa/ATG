"""AI-powered test generation module for ATG.

This module provides functionality for generating test cases using AI models.
"""
from typing import List, Dict, Any, Optional

__all__ = ["TestGenerator"]


class TestGenerator:
    """A class for generating test cases using AI models."""

    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.7):
        """Initialize the TestGenerator with a specific AI model.

        Args:
            model_name: The name of the AI model to use.
            temperature: Controls randomness in the model's output (0.0 to 1.0).
        """
        self.model_name = model_name
        self.temperature = temperature
        self._client = None

    def initialize(self, api_key: Optional[str] = None) -> None:
        """Initialize the AI client with an API key.

        Args:
            api_key: The API key for the AI service. If None, will look for OPENAI_API_KEY environment variable.
        """
        try:
            from openai import OpenAI

            self._client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError(
                "The 'openai' package is required for AI test generation. "
                "Please install it with: pip install openai"
            )

    def generate_test_cases(
        self, requirements: str, test_framework: str = "pytest"
    ) -> List[Dict[str, Any]]:
        """Generate test cases based on the provided requirements.

        Args:
            requirements: The requirements or documentation to generate tests from.
            test_framework: The testing framework to generate tests for (e.g., 'pytest', 'unittest').

        Returns:
            A list of dictionaries containing test case information.
        """
        if not self._client:
            self.initialize()

        prompt = self._build_prompt(requirements, test_framework)

        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates test cases based on requirements.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                max_tokens=2000,
            )

            # Parse the response and return structured test cases
            return self._parse_test_cases(response.choices[0].message.content)

        except Exception as e:
            raise RuntimeError(f"Failed to generate test cases: {str(e)}")

    def _build_prompt(self, requirements: str, test_framework: str) -> str:
        """Build the prompt for the AI model.

        Args:
            requirements: The requirements or documentation to generate tests from.
            test_framework: The testing framework to generate tests for.

        Returns:
            The formatted prompt string.
        """
        return f"""Generate test cases in {test_framework} format based on the following requirements:

{requirements}

Please provide:
1. Test case names that are descriptive and follow {test_framework} naming conventions
2. Test functions with appropriate assertions
3. Any necessary setup/teardown methods
4. Clear comments explaining the test logic
5. Edge cases and error conditions
6. Test data if applicable

Format the response in a clear, readable way with proper code formatting."""

    def _parse_test_cases(self, response: str) -> List[Dict[str, Any]]:
        """Parse the AI response into structured test cases.

        Args:
            response: The raw response from the AI model.

        Returns:
            A list of dictionaries containing test case information.
        """
        # This is a basic implementation that can be enhanced based on the actual response format
        return [{"content": response, "metadata": {}}]
