# Test Case Scaffolding Generator

The Test Case Scaffolding Generator is a powerful tool that helps you quickly generate test case templates in various testing frameworks. It supports multiple test frameworks and provides a consistent way to create well-structured test cases.

## Supported Test Frameworks

1. **Robot Framework** - For acceptance testing and robotic process automation (RPA)
2. **pytest** - For unit and functional testing in Python
3. **Cucumber (Gherkin)** - For behavior-driven development (BDD)
4. **JUnit** - For unit testing in Java

## Features

- Generate test case templates with a single function call
- Support for multiple test frameworks
- Customizable templates
- Integration with keyword mapping system
- Consistent test structure across the project
- Built-in best practices for each framework

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from atg.scaffolding import TestCaseGenerator
from atg.config import Config

# Initialize the generator
config = Config()
generator = TestCaseGenerator(config)

# Generate a test case
generator.generate_test_case(
    test_name="Login Test",
    description="Test the login functionality",
    steps=[
        {"action": "Navigate to login page", "expected_result": "Login page should be displayed"},
        {"action": "Enter valid credentials", "expected_result": "User should be logged in"},
        {"action": "Click login button", "expected_result": "Dashboard should be displayed"}
    ],
    framework="robot",  # or 'pytest', 'cucumber', 'junit'
    output_dir="./tests"
)
```

### Available Frameworks

#### 1. Robot Framework

```python
generator.generate_test_case(
    test_name="Login Test",
    framework="robot",
    # ... other parameters
)
```

#### 2. pytest

```python
generator.generate_test_case(
    test_name="Login Test",
    framework="pytest",
    # ... other parameters
)
```

#### 3. Cucumber (Gherkin)

```python
generator.generate_test_case(
    test_name="Login Test",
    framework="cucumber",
    # ... other parameters
)
```

#### 4. JUnit

```python
generator.generate_test_case(
    test_name="Login Test",
    framework="junit",
    # ... other parameters
)
```

## Template Customization

You can customize the templates by modifying the template files in the `templates` directory. The generator uses Jinja2 for template rendering.

### Available Template Variables

- `test_name`: The name of the test case
- `description`: Detailed description of the test case
- `steps`: List of test steps with actions and expected results
- `framework`: The target test framework
- `timestamp`: Current timestamp
- `author`: Current user (if available)

## Best Practices

1. **Descriptive Test Names**: Use clear and descriptive names for your test cases
2. **Modular Design**: Keep test cases focused on a single functionality
3. **Reusable Keywords**: Extract common actions into reusable keywords/functions
4. **Data-Driven Testing**: Use external data sources for test data when possible
5. **Proper Assertions**: Include meaningful assertions to verify test results

## Examples

### Robot Framework Example

```robot
*** Test Cases ***
Login Test
    [Documentation]    Test the login functionality
    [Setup]    Open Browser    ${URL}    ${BROWSER}

    # Test Steps
    Navigate To Login Page
    Enter Credentials    ${USERNAME}    ${PASSWORD}
    Click Login Button
    Verify Dashboard Is Displayed

    [Teardown]    Close Browser
```

### pytest Example

```python
def test_login():
    """Test the login functionality."""
    # Setup
    browser = webdriver.Chrome()

    try:
        # Test Steps
        navigate_to_login_page(browser)
        enter_credentials(browser, "testuser", "password")
        click_login_button(browser)

        # Assertions
        assert "Dashboard" in browser.title
        assert is_element_displayed(browser, "welcome-message")

    finally:
        # Teardown
        browser.quit()
```

## Troubleshooting

### Template Not Found

If you get a "Template not found" error, make sure:
1. The template file exists in the `templates` directory
2. The template file has the correct `.j2` extension
3. The template file is readable

### Rendering Errors

If you encounter rendering errors:
1. Check the template syntax (Jinja2)
2. Verify all required variables are provided
3. Check for special characters that might need escaping

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Add tests for your changes
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
