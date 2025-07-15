"""Test case scaffolding generator for ATG.

This module provides functionality to generate test case templates and scaffolding
based on documentation and requirements.
"""
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import os
import json

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from atg.config import Config
from atg.keywords import KeywordMapper


class TestCaseGenerator:
    """Generates test case scaffolding based on documentation and requirements."""

    def __init__(self, config: Config, keyword_mapper: Optional[KeywordMapper] = None):
        """Initialize the test case generator.

        Args:
            config: Configuration object
            keyword_mapper: Optional KeywordMapper instance for keyword resolution
        """
        self.config = config
        self.keyword_mapper = keyword_mapper or KeywordMapper(config)
        self.templates_dir = Path(__file__).parent / "templates"
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, str]:
        """Load test case templates from the templates directory.

        Returns:
            Dictionary mapping template names to their content
        """
        templates = {}
        if not self.templates_dir.exists():
            self.templates_dir.mkdir(parents=True, exist_ok=True)
            return templates

        for template_file in self.templates_dir.glob("*.j2"):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    templates[template_file.stem] = f.read()
            except Exception as e:
                print(f"Warning: Failed to load template {template_file.name}: {e}")

        return templates

    def generate_test_case(
        self,
        test_name: str,
        description: str,
        steps: List[Dict[str, str]],
        framework: str = "robot",
        output_dir: Optional[Union[str, Path]] = None,
    ) -> str:
        """Generate a test case file.

        Args:
            test_name: Name of the test case
            description: Test case description
            steps: List of test steps, each with 'action' and 'expected_result'
            framework: Test framework to use (e.g., 'robot', 'pytest')
            output_dir: Directory to save the generated test case

        Returns:
            Path to the generated test case file
        """
        # Get the appropriate template for the framework
        template = self.templates.get(f"test_case_{framework}")
        if not template:
            raise ValueError(f"No template found for framework: {framework}")

        # Process steps to include keyword mappings
        processed_steps = []
        for step in steps:
            action = step.get("action", "")
            expected = step.get("expected_result", "")

            # Get keyword mapping if available
            keyword, confidence = self.keyword_mapper.map_action_to_keyword(action)

            processed_steps.append(
                {
                    "action": action,
                    "expected_result": expected,
                    "keyword": keyword or action,
                    "confidence": confidence,
                }
            )

        # Render the template with the test case data
        test_case = self._render_template(
            f"test_case_{framework}",
            test_name=test_name,
            description=description,
            steps=processed_steps,
        )

        # Determine output path
        if not output_dir:
            output_dir = Path.cwd() / "tests"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename based on test name
        if framework == "robot":
            filename = f"{test_name.lower().replace(' ', '_')}.robot"
        else:
            filename = f"test_{test_name.lower().replace(' ', '_')}.py"

        output_path = output_dir / filename

        # Write the test case to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(test_case)

        return str(output_path)

    def _render_template(self, template_name: str, **context: Any) -> str:
        """Render a template with the given context.

        Args:
            template_name: Name of the template to render
            **context: Variables to use in the template

        Returns:
            Rendered template string

        Raises:
            ValueError: If the template is not found
        """
        # Create Jinja2 environment
        env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        try:
            template = env.get_template(f"{template_name}.j2")
            return template.render(**context)
        except Exception as e:
            raise ValueError(f"Failed to render template {template_name}: {e}")


__all__ = ["TestCaseGenerator"]
