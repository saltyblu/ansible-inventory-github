.PHONY: help install install-dev test test-unit test-integration test-coverage test-verbose lint type clean

help:
	@echo "Development targets for ansible-inventory-github"
	@echo ""
	@echo "Installation:"
	@echo "  make install         - Install runtime dependencies"
	@echo "  make install-dev     - Install with dev/test dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test            - Run unit tests"
	@echo "  make test-unit       - Run unit tests only"
	@echo "  make test-integration- Run integration tests only"
	@echo "  make test-coverage   - Run tests with coverage report"
	@echo "  make test-verbose    - Run tests with verbose output"
	@echo "  make test-all        - Run tests on all Python/Ansible versions (tox)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            - Run linting (flake8, ansible-lint)"
	@echo "  make type            - Run type checking (mypy)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean           - Remove test artifacts and cache"
	@echo ""

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt -r requirements-dev.txt

# Testing
test: ## Run unit tests with pytest
	pytest tests/unit/

test-unit: ## Run unit tests only
	pytest tests/unit/ -v

test-integration: ## Run integration tests only
	pytest tests/integration/ -v

test-coverage: ## Run tests with coverage report
	pytest --cov=plugins --cov-report=html --cov-report=term-missing tests/unit/

test-verbose: ## Run tests with verbose output
	pytest -vv tests/

test-all: ## Run tests on all Python/Ansible versions with tox
	tox

# Code Quality
lint: ## Run linters (flake8, ansible-lint)
	flake8 plugins/ tests/ --max-line-length=120 --exclude=__pycache__
	ansible-lint plugins/ || true

type: ## Run type checking (mypy)
	mypy plugins/ --ignore-missing-imports

# Cleanup
clean: ## Remove test artifacts and cache
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .mypy_cache
	rm -rf .tox
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

