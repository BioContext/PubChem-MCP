# Contributing to PubChem-MCP

We welcome contributions to PubChem-MCP! This document provides guidelines and instructions for contributing.

## Development Setup

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/YOUR-USERNAME/PubChem-MCP.git
cd PubChem-MCP
```

3. Set up the development environment:
```bash
# Create a virtual environment using uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

## Making Changes

1. Create a new branch for your changes:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and add tests if applicable
3. Run tests to ensure everything works:
```bash
pytest
```

4. Format your code:
```bash
black .
isort .
```

## Submitting Changes

1. Push your changes to your fork:
```bash
git push origin feature/your-feature-name
```

2. Open a pull request on the main repository

## Code Guidelines

- Follow PEP 8 style guidelines
- Include docstrings for all functions and classes
- Add appropriate type hints
- Write tests for new functionality

Thank you for your contributions! 