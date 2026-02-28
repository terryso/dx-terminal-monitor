# DX Terminal Monitor - Test Commands
# Usage: make <target>

.PHONY: test test-unit test-integration test-api test-cov test-quick install clean

# Default: run all tests
test:
	pytest

# Run only unit tests (fast, no external dependencies)
test-unit:
	pytest tests/unit/ -v

# Run integration tests
test-integration:
	pytest tests/integration/ -v

# Run API tests (requires network)
test-api:
	pytest -m api -v

# Run tests with coverage report
test-cov:
	pytest --cov=. --cov-report=html --cov-report=term
	@echo "Coverage report: htmlcov/index.html"

# Quick test: skip slow and API tests
test-quick:
	pytest -m "not slow and not api" -v

# Run tests in parallel (requires pytest-xdist)
test-parallel:
	pytest -n auto

# Install test dependencies
install:
	pip install -r requirements-test.txt

# Clean up test artifacts
clean:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
