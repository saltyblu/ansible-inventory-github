# Testing Guide for ansible-inventory-github

This guide explains how to test the ansible-inventory-github collection's GitHub repositories inventory plugin.

Following Ansible Collection best practices: https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html

## Setup

### Install Test Dependencies

This project uses standard Python package management with `pip`:

```bash
# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Or use the Make target
make install-dev
```

### Project Structure

```
tests/
├── unit/
│   └── plugins/inventory/
│       └── test_github_repositories_inventory.py
├── integration/
│   └── inventory/
│       └── github_repositories.yml
├── conftest.py           # Pytest configuration and fixtures
└── README.md            # This file
```

## Running Tests

All test commands use standard `pytest`. Use `make` targets for convenience.

### Run All Tests

```bash
make test
# or
pytest tests/unit/
```

### Run Only Unit Tests

```bash
make test-unit
# or
pytest tests/unit/ -v
```

### Run Integration Tests

```bash
make test-integration
# or
pytest tests/integration/ -v
```

For live GitHub API integration tests, set environment variables first:

```bash
export GITHUB_TOKEN=<your-token>
export GITHUB_TEST_ORG=saltyblu
export GITHUB_TEST_FILTER='*-deployment'
pytest tests/integration/test_github_repositories_integration.py -v
```

### Run with Coverage Report

```bash
make test-coverage
# or
pytest --cov=plugins --cov-report=html --cov-report=term-missing tests/unit/
```

### Run Specific Test

```bash
pytest tests/unit/plugins/inventory/test_github_repositories_inventory.py::TestGitHubRepositoryFetcher::test_initialization
```

### Run Tests Matching a Pattern

```bash
pytest -k "test_fetch_repositories"
```

### Run with Verbose Output

```bash
make test-verbose
# or
pytest -vv tests/
```

## Multi-Version Testing with Tox

Test across multiple Python and Ansible versions:

```bash
# Test all matrix combinations
make test-all
# or
tox

# Test specific Python version
tox -e py311

# Test specific Ansible version
tox -e ansible-11

# List all environments
tox -l
```

## Code Quality & Linting

```bash
# Run linters (flake8, ansible-lint)
make lint

# Run type checking (mypy)
make type
```

## Test Organization

### Unit Tests (`tests/unit/`)

Unit tests focus on testing individual components in isolation:

- **`TestGetLogger`**: Tests for the `get_logger` helper function
- **`TestGitHubRepositoryFetcher`**: Tests for the `GitHubRepositoryFetcher` class
  - Initialization with and without custom logger
  - Setting custom GitHub client (for mocking)
  - Fetching repositories with various options
  - Error handling
- **`TestInventoryModuleParseMethods`**: Tests for inventory parsing logic
  - Regex-based grouping
  - Error handling
- **`TestInventoryModuleIntegration`**: Integration tests with mocked components

### Integration Tests (`tests/integration/`)

Integration tests test the full inventory plugin workflow (to be added):

- Full inventory parsing with YAML configuration
- GitHub API integration (with mocked responses)
- Inventory group and host management

## Mocking Strategy

The refactored code makes mocking easier through **Dependency Injection**:

```python
# Create mocks
mock_logger = Mock(spec=logging.Logger)
mock_fetcher = Mock(spec=GitHubRepositoryFetcher)

# Inject them
inventory = InventoryModule(logger=mock_logger, fetcher=mock_fetcher)
```

### Key Mocking Points

1. **GitHub Client**: Use `fetcher.set_github_client(mock_client)` to mock GitHub API calls
2. **Logger**: Pass a `Mock` logger to avoid logging overhead in tests
3. **Fetcher**: Inject a mocked `GitHubRepositoryFetcher` to test inventory parsing logic independently

## Example Test

```python
def test_fetch_repositories_returns_list():
    """Test that fetch_repositories returns a list of repositories."""
    fetcher = GitHubRepositoryFetcher('test_token', Mock())

    # Mock GitHub client
    mock_github = Mock()
    mock_repo = Mock()
    mock_repo._rawData = {'name': 'repo1', 'id': 1}
    mock_search_result = [mock_repo]
    mock_github.search_repositories.return_value = mock_search_result

    fetcher.set_github_client(mock_github)

    result = fetcher.fetch_repositories(
        repository_filter='*',
        org='test-org'
    )

    assert len(result) == 1
```

## Writing New Tests

When adding new tests:

1. **Use descriptive test names** that explain what is being tested
2. **Separate setup, action, and assertion** phases
3. **Use docstrings** to explain the test's purpose
4. **Mock external dependencies** (GitHub API, file I/O, etc.)
5. **Test edge cases** (empty results, errors, invalid input)

### Test Template

```python
def test_feature_description(self):
    """Test that [feature] does [expected behavior]."""
    # Setup
    fetcher = GitHubRepositoryFetcher('token', Mock())

    # Action
    result = fetcher.some_method()

    # Assertion
    assert result is not None
```

## Troubleshooting

### Virtual Environment Not Activated

Make sure your virtual environment is activated:

```bash
# Create venv if needed
python3 -m venv venv

# Activate venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

### Import Errors for `ansible` or `github`

Ensure dependencies are installed:

```bash
# Reinstall dependencies
pip install -r requirements.txt -r requirements-dev.txt
```

### Pytest Not Found

```bash
pip install pytest pytest-cov pytest-mock
```

### Python Version Mismatch

The project requires Python 3.9+. Check your version:

```bash
python3 --version

# If needed, create venv with specific Python version
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### Mock Not Matching Spec

Ensure the mock spec matches the actual class:

```python
from unittest.mock import Mock
from plugins.inventory.github_repositories_inventory import GitHubRepositoryFetcher

mock_fetcher = Mock(spec=GitHubRepositoryFetcher)
```

## Continuous Integration

CI/CD can run tests using:

```bash
# Run tests with coverage
pytest --cov=plugins --cov-report=xml --junitxml=test-results.xml

# Run on all versions with tox
tox

# Run specific Ansible version
tox -e ansible-11
```

This generates:
- Coverage reports (in `coverage.xml`)
- Test results (in `test-results.xml`)

## Resources

- [Ansible Collections Documentation](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Tox Documentation](https://tox.readthedocs.io/)


