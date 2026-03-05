# Development & Setup Guide

This guide explains how to set up the development environment and work with the ansible-inventory-github collection.

## Prerequisites

- **Python 3.9+** (Supported: 3.9, 3.10, 3.11, 3.12)
- **pip** (Python package manager)
- **Ansible 2.10+** (Tested with 2.10 up to 11.x)
- **tox** (optional, for testing multiple Python/Ansible versions)
- **Git**

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/saltyblu/ansible-inventory-github.git
cd ansible-inventory-github
```

### 2. Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Project with Dependencies

```bash
# Install runtime and dev dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Or use the Make target
make install-dev
```

## Development Workflow

### Running Tests

```bash
# Run unit tests
make test

# Run all tests with verbose output
make test-verbose

# Run specific test suite
make test-unit
make test-integration

# Run with coverage (generates HTML report)
make test-coverage

# Run tests on all Python/Ansible versions with tox
make test-all
```

### Code Quality & Linting

```bash
# Check code quality (flake8, ansible-lint)
make lint

# Run type checking (mypy)
make type
```

### Managing Dependencies

Dependencies are defined in standard `requirements.txt` files:

```bash
# Install/update dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Upgrade all packages
pip install --upgrade -r requirements.txt -r requirements-dev.txt

# Add a new runtime dependency
pip install package-name
pip freeze | grep package-name >> requirements.txt

# Add a new dev dependency
pip install package-name
pip freeze | grep package-name >> requirements-dev.txt
```

### Python Version Management

The project is compatible with Python 3.9+. If you need to switch Python versions:

```bash
# Check available Python versions
python3 --version

# Create venv with specific Python version
python3.11 -m venv venv
source venv/bin/activate
```

## Project Structure

```
ansible-inventory-github/
├── plugins/
│   └── inventory/
│       └── github_repositories_inventory.py  # Main plugin
├── tests/
│   ├── unit/
│   │   └── plugins/inventory/
│   │       └── test_github_repositories_inventory.py
│   ├── integration/
│   │   └── inventory/
│   │       └── github_repositories.yml
│   ├── conftest.py
│   └── README.md
├── galaxy.yml             # Ansible Collection metadata
├── pyproject.toml         # Minimal project config (pytest only)
├── tox.ini                # Multi-version testing
├── requirements.txt       # Runtime dependencies
├── requirements-dev.txt   # Dev/test dependencies
├── Makefile               # Development targets
└── README.md
```

## Key Components

### 1. GitHubRepositoryFetcher

Handles GitHub API interactions:

```python
from plugins.inventory.github_repositories_inventory import GitHubRepositoryFetcher

fetcher = GitHubRepositoryFetcher('token')
repos = fetcher.fetch_repositories('filter', 'org')
```

### 2. InventoryModule

Main Ansible inventory plugin. Supports dependency injection for testing:

```python
from plugins.inventory.github_repositories_inventory import InventoryModule

# Production usage
inventory = InventoryModule()

# Testing with mocks
inventory = InventoryModule(logger=mock_logger, fetcher=mock_fetcher)
```

## Configuration Files

### galaxy.yml

Ansible Collection metadata - defines collection name, version, and dependencies.

### pyproject.toml

Minimal configuration for pytest (Ansible Collections standard).

### tox.ini

Automates testing across multiple Python and Ansible versions:

```bash
# Run tests on all versions
tox

# Run specific environment
tox -e py311-ansible-11

# Run linting
tox -e lint
```

### Makefile

Convenient development targets:

```bash
make help      # Show all available targets
make test      # Run tests
make lint      # Check code quality
make type      # Type checking
make test-all  # Test with tox
```

## Ansible Best Practices Compliance

This project follows Ansible Collection best practices:

1. **Collection Structure**: Per [Ansible Collection docs](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html)
2. **Dependency Management**: Standard `requirements.txt` files
3. **Testing**: Comprehensive unit and integration tests
4. **Documentation**: Docstrings, README, and guides
5. **Type Hints**: Type annotations where appropriate
6. **Version Compatibility**: Python 3.9+, Ansible 2.10+

## Contributing

1. Create a feature branch: `git checkout -b feature/xyz`
2. Make changes and install dev deps: `make install-dev`
3. Run tests: `make test`
4. Check code quality: `make lint`
5. Run across versions: `make test-all`
6. Commit with descriptive message: `git commit -am 'Add feature xyz'`
7. Push and create a pull request

## Common Tasks

### Run a Single Test

```bash
pytest tests/unit/plugins/inventory/test_github_repositories_inventory.py::TestGitHubRepositoryFetcher::test_initialization
```

### Run Tests Matching a Pattern

```bash
pytest -k "test_fetch_repositories"
```

### Generate Coverage Report

```bash
make test-coverage
# Open htmlcov/index.html to view report
```

### Test with Specific Python Version

```bash
# Using tox
tox -e py310

# Or manually with venv
python3.10 -m venv venv-py310
source venv-py310/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

### Test with Specific Ansible Version

```bash
# Using tox
tox -e ansible-11

# Or manually
pip install 'ansible>=11,<12'
pytest
```

### Create a Distribution Package

```bash
# Build the Ansible Collection
ansible-galaxy collection build
```

## Troubleshooting

### Virtual Environment Issues

```bash
# Remove and recreate venv
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### Python Version Not Found

```bash
# List available Python versions
python3 --version
which python3.11

# Install specific Python version (macOS with Homebrew)
brew install python@3.11
```

### Pytest Import Errors

```bash
# Reinstall with clean environment
pip uninstall -y ansible PyGithub pytest
pip install -r requirements.txt -r requirements-dev.txt
```

### Tox Configuration Issues

```bash
# Clear tox cache
rm -rf .tox/

# Run with verbose output
tox -vv
```

## Resources

- [Ansible Collections Documentation](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html)
- [Ansible Plugin Development](https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Tox Documentation](https://tox.readthedocs.io/)


## Project Structure

```
ansible-inventory-github/
├── plugins/
│   └── inventory/
│       └── github_repositories_inventory.py  # Main plugin
├── tests/
│   ├── unit/
│   │   └── plugins/inventory/
│   │       └── test_github_repositories_inventory.py
│   ├── integration/
│   │   └── inventory/
│   │       └── github_repositories.yml
│   ├── conftest.py
│   └── README.md
├── gallery.yml           # Ansible Collection metadata
├── pyproject.toml        # Poetry configuration
├── Makefile              # Development targets
└── README.md
```

## Key Components

### 1. GitHubRepositoryFetcher

Handles GitHub API interactions:

```python
from plugins.inventory.github_repositories_inventory import GitHubRepositoryFetcher

fetcher = GitHubRepositoryFetcher('token')
repos = fetcher.fetch_repositories('filter', 'org')
```

### 2. InventoryModule

Main Ansible inventory plugin. Supports dependency injection for testing:

```python
from plugins.inventory.github_repositories_inventory import InventoryModule

# Production usage
inventory = InventoryModule()

# Testing with mocks
inventory = InventoryModule(logger=mock_logger, fetcher=mock_fetcher)
```

## Configuration Files

### pyproject.toml

Contains all project metadata and dependencies:

- **[tool.poetry]**: Project definition
- **[tool.poetry.dependencies]**: Runtime dependencies
- **[tool.poetry.group.dev.dependencies]**: Development dependencies
- **[tool.pytest.ini_options]**: Pytest configuration
- **[tool.ruff]**: Ruff linter configuration
- **[tool.black]**: Black formatter configuration
- **[tool.mypy]**: Type checker configuration

### Makefile

Convenient development targets:

```bash
make help    # Show all available targets
make test    # Run tests
make lint    # Check code quality
make format  # Format code
```

## Ansible Best Practices Compliance

This project follows Ansible best practices:

1. **Collection Structure**: Organized as Per Ansible documentation
2. **Dependency Management**: Uses Python industry standard (Poetry)
3. **Testing**: Comprehensive unit and integration tests
4. **Documentation**: Docstrings, README, and guides
5. **Type Hints**: Type annotations where appropriate
6. **Code Quality**: Automated linting and formatting

## Contributing

1. Create a feature branch: `git checkout -b feature/xyz`
2. Make changes and run tests: `make test`
3. Check code quality: `make lint`
4. Format code: `make format`
5. Commit with descriptive message: `git commit -am 'Add feature xyz'`
6. Push and create a pull request

## Common Tasks

### Run a Single Test

```bash
poetry run pytest tests/unit/plugins/inventory/test_github_repositories_inventory.py::TestGitHubRepositoryFetcher::test_initialization
```

### Run Tests Matching a Pattern

```bash
poetry run pytest -k "test_fetch_repositories"
```

### Generate Coverage Report

```bash
make test-coverage
# Open htmlcov/index.html to view report
```

### Update Dependencies to Latest

```bash
# Update poetry.lock while respecting version constraints
poetry update

# Show outdated packages
poetry show --outdated
```

### Create a Distribution Package

```bash
# Build the Ansible Collection
ansible-galaxy collection build
```

## Troubleshooting

### Poetry Lock Issues

If you encounter lock file conflicts:

```bash
# Remove and regenerate lock file
rm poetry.lock
poetry install --with dev
```

### Python Version Mismatch

```bash
# Set Poetry to use your Python 3.11+
poetry env use python3.11
poetry install --with dev
```

### Import Errors

```bash
# Reinstall with clean environment
poetry cache clear . --all
poetry install --with dev --no-cache
```

## Resources

- [Ansible Collections Documentation](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html)
- [Ansible Plugin Development](https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Pytest Documentation](https://docs.pytest.org/)
