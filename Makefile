# Makefile - Test and development commands

.PHONY: help install test test-unit test-integration test-models test-client test-coverage clean lint format

# Default target
help:
	@echo "CallWhiz SDK Development Commands"
	@echo "================================"
	@echo "install         Install package in development mode"
	@echo "test            Run all tests"
	@echo "test-unit       Run unit tests only"
	@echo "test-integration Run integration tests only"
	@echo "test-models     Run model tests only" 
	@echo "test-client     Run client tests only"
	@echo "test-coverage   Run tests with coverage report"
	@echo "test-quick      Run quick tests without coverage"
	@echo "lint            Run code linting"
	@echo "format          Format code with black"
	@echo "clean           Clean build artifacts"
	@echo "build           Build package for distribution"

# Installation
install:
	pip install -e ".[dev]"

# Testing
test:
	pytest tests/ -v --cov=src --cov-report=term-missing

test-unit:
	pytest tests/unit/ -v --cov=src --cov-report=term-missing

test-integration:
	@echo "⚠️  Make sure your API server is running!"
	pytest tests/integration/ -v -m integration

test-models:
	pytest tests/unit/test_models.py -v

test-client:
	pytest tests/unit/test_client.py -v

test-exceptions:
	pytest tests/unit/test_exceptions.py -v

test-coverage:
	pytest tests/unit/ --cov=src --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo "📄 Coverage report: htmlcov/index.html"

test-quick:
	pytest tests/unit/ -v --tb=short

# Code quality
lint:
	ruff check src/ tests/
	mypy src/

format:
	black src/ tests/

# Build and distribution
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -name "*.pyc" -delete

build: clean
	python -m build