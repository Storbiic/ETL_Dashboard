# ETL Dashboard Development Makefile
# Provides convenient commands for common development tasks

.PHONY: help install install-dev test test-unit test-integration test-coverage clean format lint type-check security docker-build docker-up docker-down docker-test deploy-staging

# Default target
help:
	@echo "ETL Dashboard Development Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  install          Install production dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo ""
	@echo "Code Quality:"
	@echo "  format          Format code with black and isort"
	@echo "  lint            Run flake8 linting"
	@echo "  type-check      Run mypy type checking"
	@echo "  security        Run security checks (bandit, safety)"
	@echo "  quality         Run all code quality checks"
	@echo ""
	@echo "Testing:"
	@echo "  test            Run all tests"
	@echo "  test-unit       Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-coverage   Run tests with coverage report"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build    Build Docker images"
	@echo "  docker-up       Start Docker Compose services"
	@echo "  docker-down     Stop Docker Compose services"
	@echo "  docker-test     Run tests in Docker environment"
	@echo ""
	@echo "Deployment:"
	@echo "  deploy-staging  Deploy to staging environment"
	@echo ""
	@echo "Utilities:"
	@echo "  clean           Clean up temporary files"
	@echo "  dev             Start development server"

# Installation
install:
	pip install --upgrade pip
	pip install -r requirements.txt

install-dev: install
	pip install black isort flake8 mypy bandit safety pytest pytest-cov pytest-xdist pytest-mock

# Code Quality
format:
	@echo "🔧 Formatting code with black..."
	black backend/ frontend/ tests/
	@echo "📦 Sorting imports with isort..."
	isort backend/ frontend/ tests/
	@echo "✅ Code formatting complete!"

lint:
	@echo "🔍 Running flake8 linting..."
	flake8 backend/ frontend/ tests/ --max-line-length=88 --extend-ignore=E203,W503

type-check:
	@echo "🔬 Running mypy type checking..."
	mypy backend/ --ignore-missing-imports --no-strict-optional

security:
	@echo "🛡️ Running security checks..."
	bandit -r backend/ -f json -o bandit-report.json || true
	safety check --json --output safety-report.json || true
	@echo "Security reports saved to bandit-report.json and safety-report.json"

quality: format lint type-check security
	@echo "✅ All code quality checks complete!"

# Testing
test:
	@echo "🧪 Running all tests..."
	pytest tests/ -v

test-unit:
	@echo "🧪 Running unit tests..."
	pytest tests/ -v -m "unit"

test-integration:
	@echo "🧪 Running integration tests..."
	pytest tests/ -v -m "integration"

test-coverage:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ --cov=backend --cov=frontend --cov-report=html --cov-report=term-missing --cov-fail-under=70

# Docker
docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-up:
	@echo "🐳 Starting Docker Compose services..."
	docker-compose up -d

docker-down:
	@echo "🐳 Stopping Docker Compose services..."
	docker-compose down -v

docker-test:
	@echo "🐳 Running tests in Docker environment..."
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
	docker-compose -f docker-compose.test.yml down -v

# Development
dev:
	@echo "🚀 Starting development server..."
	python run_dev.py

# Deployment
deploy-staging:
	@echo "🚀 Deploying to staging environment..."
	@echo "This would trigger staging deployment..."
	# Add actual staging deployment commands here

# Utilities
clean:
	@echo "🧹 Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -f bandit-report.json
	rm -f safety-report.json
	@echo "✅ Cleanup complete!"

# Windows-specific targets (if needed)
ifeq ($(OS),Windows_NT)
clean-windows:
	@echo "🧹 Cleaning up temporary files (Windows)..."
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
	for /d /r . %%d in (*.egg-info) do @if exist "%%d" rd /s /q "%%d"
	if exist build rd /s /q build
	if exist dist rd /s /q dist
	if exist htmlcov rd /s /q htmlcov
	if exist .pytest_cache rd /s /q .pytest_cache
	if exist .mypy_cache rd /s /q .mypy_cache
	del /q .coverage 2>nul
	del /q bandit-report.json 2>nul
	del /q safety-report.json 2>nul
	@echo "✅ Windows cleanup complete!"
endif