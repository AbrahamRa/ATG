"""Tests for the test case scaffolding generator."""
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from atg.config import Config
from atg.keywords import KeywordMapper
from atg.scaffolding import TestCaseGenerator


@pytest.fixture
def config():
    """Create a test configuration."""
    config = Config()
    config.disable_validation()
    return config


@pytest.fixture
def keyword_mapper(config):
    """Create a mock keyword mapper."""
    mapper = KeywordMapper(config)
    # Mock the map_action_to_keyword method
    mapper.map_action_to_keyword = MagicMock(return_value=("Click Element", 0.9))
    return mapper


def test_test_case_generator_init(config, keyword_mapper):
    """Test TestCaseGenerator initialization."""
    # Test with default keyword mapper
    generator = TestCaseGenerator(config)
    assert generator.config == config
    assert isinstance(generator.keyword_mapper, KeywordMapper)

    # Test with provided keyword mapper
    generator = TestCaseGenerator(config, keyword_mapper)
    assert generator.keyword_mapper == keyword_mapper


def test_load_templates():
    """Test template loading."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test template
        template_dir = Path(temp_dir) / "templates"
        template_dir.mkdir()

        test_template = template_dir / "test_case_robot.j2"
        test_template.write_text("Test template content")

        # Create generator with custom template directory
        config = Config()
        config.disable_validation()
        generator = TestCaseGenerator(config)

        # Replace templates_dir for testing
        generator.templates_dir = template_dir

        # Test template loading
        templates = generator._load_templates()
        assert "test_case_robot" in templates
        assert templates["test_case_robot"] == "Test template content"


def test_generate_test_case_robot(config, keyword_mapper, tmp_path):
    """Test Robot Framework test case generation."""
    # Create generator with test templates
    generator = TestCaseGenerator(config, keyword_mapper)

    # Create a temporary template file
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    template_file = template_dir / "test_case_robot.j2"
    template_file.write_text(
        """*** Test Cases ***
{{ test_name }}
    [Documentation]    {{ description }}
    {% for step in steps %}{{ step.keyword }}
    {% endfor %}"""
    )

    # Update the generator to use our test template directory
    generator.templates_dir = template_dir

    # Generate test case
    test_steps = [
        {
            "action": "Click the login button",
            "expected_result": "Login page should be displayed",
        },
        {"action": "Enter username", "expected_result": "Username should be entered"},
    ]

    output_file = generator.generate_test_case(
        test_name="Test Login",
        description="Test the login functionality",
        steps=test_steps,
        framework="robot",
        output_dir=tmp_path,
    )

    # Verify output file
    assert os.path.exists(output_file)
    assert "test_login.robot" in output_file

    # Verify content
    with open(output_file, "r") as f:
        content = f.read()

    assert "Test Login" in content
    assert "Test the login functionality" in content
    for step in test_steps:
        assert step["action"] not in content  # Should use mapped keywords instead
    assert "Click Element" in content  # From our mock


def test_generate_test_case_unsupported_framework(config, tmp_path):
    """Test error handling for unsupported test frameworks."""
    generator = TestCaseGenerator(config)

    with pytest.raises(ValueError, match="No template found for framework: invalid"):
        generator.generate_test_case(
            test_name="Test",
            description="Test",
            steps=[],
            framework="invalid",
            output_dir=tmp_path,
        )


def test_render_template(tmp_path):
    """Test template rendering."""
    # Create a temporary template file
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    # Create a simple template
    template_file = template_dir / "test_template.j2"
    template_file.write_text("Hello {{ name }}!")

    # Create a list template
    list_template = template_dir / "list_template.j2"
    list_template.write_text(
        "Items: {% for item in items %}{{ item }}{% if not loop.last %}, {% endif %}{% endfor %}"
    )

    # Create a dict template
    dict_template = template_dir / "dict_template.j2"
    dict_template.write_text(
        "Config: {% for key, value in config.items() %}{{ key }}={{ value }}{% if not loop.last %}, {% endif %}{% endfor %}"
    )

    # Initialize the generator with the test template directory
    config = Config()
    config.disable_validation()
    generator = TestCaseGenerator(config)
    generator.templates_dir = template_dir

    # Test simple variable substitution
    result = generator._render_template("test_template", name="World")
    assert result == "Hello World!"

    # Test list rendering
    result = generator._render_template("list_template", items=[1, 2, 3])
    assert "1, 2, 3" in result

    # Test dictionary rendering
    result = generator._render_template(
        "dict_template", config={"key": "value", "foo": "bar"}
    )
    assert "key=value" in result
    assert "foo=bar" in result
