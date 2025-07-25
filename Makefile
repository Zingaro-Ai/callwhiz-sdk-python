# Makefile - Test and development commands for CallWhiz SDK v2.0.0

.PHONY: help install test test-unit test-integration test-models test-client test-coverage clean lint format check-api

# Default target
help:
	@echo "CallWhiz SDK v2.0.0 Development Commands"
	@echo "========================================"
	@echo "install         Install package in development mode"
	@echo "test            Run all tests"
	@echo "test-unit       Run unit tests only"
	@echo "test-integration Run integration tests only (requires API server)"
	@echo "test-models     Run model tests only" 
	@echo "test-client     Run client tests only"
	@echo "test-exceptions Run exception tests only"
	@echo "test-coverage   Run tests with coverage report"
	@echo "test-quick      Run quick tests without coverage"
	@echo "test-credits    Run credits API tests"
	@echo "check-api       Check if API server is running"
	@echo "lint            Run code linting"
	@echo "format          Format code with black"
	@echo "type-check      Run type checking with mypy"
	@echo "clean           Clean build artifacts"
	@echo "build           Build package for distribution"
	@echo "publish-test    Publish to test PyPI"
	@echo "publish         Publish to PyPI"

# Installation
install:
	pip install -e ".[dev]"

# Testing
test:
	pytest tests/ -v --cov=callwhiz --cov-report=term-missing

test-unit:
	pytest tests/unit/ -v --cov=callwhiz --cov-report=term-missing

test-integration:
	@echo "⚠️  Make sure your API server is running on port 9000!"
	@echo "🚀 Starting integration tests..."
	pytest tests/integration/ -v -m integration

test-models:
	pytest tests/unit/test_models.py -v

test-client:
	pytest tests/unit/test_client.py -v

test-exceptions:
	pytest tests/unit/test_exceptions.py -v

test-coverage:
	pytest tests/unit/ --cov=callwhiz --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo "📄 Coverage report: htmlcov/index.html"

test-quick:
	pytest tests/unit/ -v --tb=short

test-credits:
	@echo "💰 Testing credits API functionality..."
	pytest tests/integration/ -v -k "credits" -m integration

# API Health Check
check-api:
	@echo "🔍 Checking if API server is running..."
	@curl -s http://localhost:9000/health > /dev/null && echo "✅ API server is running on port 9000" || echo "❌ API server not found on port 9000"

# Code quality
lint:
	@echo "🔍 Running linting..."
	ruff check callwhiz/ tests/

format:
	@echo "🎨 Formatting code..."
	black callwhiz/ tests/

type-check:
	@echo "🔍 Running type checking..."
	mypy callwhiz/

# Combined quality check
quality: format lint type-check
	@echo "✅ Code quality checks completed"

# Build and distribution
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -delete
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

build: clean
	@echo "📦 Building package..."
	python -m build

# Publishing
publish-test: build
	@echo "🚀 Publishing to test PyPI..."
	python -m twine upload --repository testpypi dist/*

publish: build
	@echo "🚀 Publishing to PyPI..."
	python -m twine upload dist/*

# Development helpers
dev-setup:
	@echo "🛠️  Setting up development environment..."
	pip install -e ".[dev]"
	pre-commit install

example-agent:
	@echo "🤖 Creating example agent..."
	python -c "from callwhiz import CallWhiz; client = CallWhiz(api_key='cw_test_demo'); print('Add your API key to test!')"

# Quick development cycle
dev: format lint test-quick
	@echo "✅ Development cycle completed"

# Full test cycle for CI
ci: format lint type-check test-coverage
	@echo "✅ CI cycle completed"

# Version management
version:
	@echo "📋 Current version:"
	@python -c "import callwhiz; print(f'v{callwhiz.__version__}')"

# Documentation helpers
docs-serve:
	@echo "📚 Serving documentation..."
	@echo "Not implemented yet - add your docs server here"

# Local testing with real API
test-local: check-api test-integration
	@echo "✅ Local testing completed"

# Install and test in one command
install-test: install test
	@echo "✅ Install and test completed"