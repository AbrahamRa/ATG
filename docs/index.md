# ATG Documentation

Welcome to the documentation for ATG (Automated Test Generator). This tool helps you automatically generate test cases for your Python code.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Usage](#usage)
4. [Configuration](#configuration)
5. [Contributing](#contributing)
6. [License](#license)

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ATG.git
   cd ATG
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Unix/MacOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Quick Start

To generate tests for a Python file:

```bash
python -m src.main path/to/your/file.py
```

## Usage

### Basic Usage

```bash
# Generate tests for a single file
python -m src.main path/to/your/file.py

# Specify output directory
python -m src.main -o tests/generated path/to/your/file.py

# Increase verbosity
python -m src.main -v path/to/your/file.py
```

### Command Line Options

```
usage: main.py [-h] [-v] [-V] [-o OUTPUT] source

ATG - Automated Test Generator

positional arguments:
  source                Source file or directory to generate tests for

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase verbosity (can be used multiple times)
  -V, --version         show program's version number and exit
  -o OUTPUT, --output OUTPUT
                        Output directory for generated tests (default: tests)
```

## Configuration

### .atgconfig

Create a `.atgconfig` file in your project root to customize test generation:

```ini
[settings]
test_framework = pytest  # or unittest
style = google  # or numpy, rest
max_test_cases = 100

[coverage]
target = 80  # Target test coverage percentage

[paths]
tests = tests/
source = src/
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
