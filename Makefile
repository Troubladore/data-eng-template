# Data Engineering Template - Testing & Development Commands
# Mission-critical testing for data engineering teams

.PHONY: help test-fast test-dev test-local test-all test-pr test-main test-nightly test-debug test-clean test-remote

# Default target
help:
	@echo "🧪 Data Engineering Template Testing Commands"
	@echo ""
	@echo "Development (local work-in-progress):"
	@echo "  test-fast      Lightning fast tests (< 10s) - syntax, variables, structure"
	@echo "  test-dev       Development tests (< 2m) - generation, basic integration"  
	@echo "  test-local     Full local tests (< 10m) - includes Docker services"
	@echo "  test-all       Complete test suite (< 30m) - everything except remote"
	@echo ""
	@echo "CI/CD Pipeline:"
	@echo "  test-pr        PR validation tests - fast feedback for pull requests"
	@echo "  test-main      Main branch tests - comprehensive validation"
	@echo "  test-nightly   Nightly comprehensive tests - stress & recovery"
	@echo ""
	@echo "Debugging & Maintenance:"
	@echo "  test-debug     Verbose testing with artifact preservation"
	@echo "  test-clean     Clean all Docker artifacts, then run tests"
	@echo "  test-remote    Test against published template (GitHub)"
	@echo ""
	@echo "⚡ Quick Start: make test-fast (immediate feedback)"
	@echo "🔍 Before Commit: make test-dev"
	@echo "🚀 Full Validation: make test-local"

# Development Testing (work-in-progress safe)
test-fast:
	@echo "⚡ Running lightning fast tests..."
	uv run pytest tests/ -v -x -m "unit or smoke" --tb=short --disable-warnings

test-dev:
	@echo "🔧 Running development integration tests..."
	uv run pytest tests/ -v -m "integration and not slow" --tb=short

test-local:
	@echo "🏠 Running full local test suite..."
	uv run pytest tests/ -v -m "not remote and not stress" --tb=short

test-all:
	@echo "🌟 Running complete test suite (except remote)..."
	uv run pytest tests/ -v -m "not remote" --tb=short

# CI/CD Pipeline Testing
test-pr:
	@echo "🔍 Running PR validation tests..."
	uv run pytest tests/ -v -x -m "unit or integration" --tb=short --junitxml=test-results-pr.xml

test-main:
	@echo "✅ Running main branch validation tests..."  
	uv run pytest tests/ -v -m "unit or integration or e2e" --tb=short --junitxml=test-results-main.xml

test-nightly:
	@echo "🌙 Running comprehensive nightly tests..."
	uv run pytest tests/ -v -m "stress or remote" --tb=short --junitxml=test-results-nightly.xml

# Debugging & Maintenance  
test-debug:
	@echo "🐛 Running tests with verbose debugging..."
	uv run pytest tests/ -vvs --tb=long --no-header --disable-warnings --capture=no

test-clean:
	@echo "🧹 Cleaning Docker artifacts and running tests..."
	@echo "Stopping all containers..."
	-docker stop $$(docker ps -aq) 2>/dev/null || true
	@echo "Removing all containers..."
	-docker rm $$(docker ps -aq) 2>/dev/null || true
	@echo "Removing all volumes..."
	-docker volume prune -f 2>/dev/null || true
	@echo "Removing all networks..."
	-docker network prune -f 2>/dev/null || true
	@echo "Removing all images..."
	-docker image prune -af 2>/dev/null || true
	@echo "Running tests from clean slate..."
	uv run pytest tests/ -v -m "not remote" --tb=short

test-remote:
	@echo "🌐 Testing against published template..."
	PYTEST_REMOTE_BRANCH=main uv run pytest tests/ -v -m "remote" --tb=short

# Template Generation Testing (specific scenarios)
test-generation:
	@echo "📝 Testing template generation scenarios..."
	uv run pytest -v tests/integration/test_template_generation.py --tb=short

test-devcontainer:
	@echo "🐳 Testing DevContainer integration..."
	uv run pytest -v tests/e2e/test_devcontainer_startup.py --tb=short

test-astronomer:
	@echo "🚀 Testing Astronomer CLI integration..."
	uv run pytest -v tests/e2e/test_astronomer_integration.py --tb=short

test-multi-project:
	@echo "🏗️ Testing multi-project isolation..."
	uv run pytest -v tests/integration/test_multi_project_isolation.py --tb=short

# Maintenance commands
lint-tests:
	@echo "🔍 Linting test code..."
	ruff check tests/ --fix

format-tests:
	@echo "✨ Formatting test code..."
	ruff format tests/

# Development setup
install-test-deps:
	@echo "📦 Installing test dependencies..."
	uv add --dev pytest pytest-xdist pytest-timeout pytest-mock cookiecutter docker

# Quick validation for developers
quick:
	@echo "⚡ Quick validation (fastest possible feedback)..."
	uv run pytest tests/ -v -x -m "smoke" --tb=line --disable-warnings -q

# Guidance-specific testing
test-guidance:
	@echo "📝 Testing CLAUDE.md documentation..."
	uv run pytest tests/ -v -m "guidance" --tb=short

# Status check
test-status:
	@echo "📊 Test Environment Status:"
	@echo "Python: $$(python --version 2>&1)"
	@echo "Pytest: $$(pytest --version 2>&1 | head -1)"
	@echo "Docker: $$(docker --version 2>&1)"
	@echo "Cookiecutter: $$(cookiecutter --version 2>&1)"
	@echo ""
	@echo "Docker Status:"
	@docker system df 2>/dev/null || echo "Docker not accessible"
	@echo ""
	@echo "Available Test Markers:"
	@pytest --markers 2>/dev/null | grep -E "^@pytest.mark" || echo "Run 'pytest --markers' for full list"