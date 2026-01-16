.PHONY: help install dev prod stop clean test test-unit test-integration test-cov logs shell db-clean format lint check health docker-build docker-dev docker-prod docker-stop docker-clean

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ General

help: ## Display this help message
	@echo "$(BLUE)Banking App API - Makefile Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(GREEN)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Local Development

install: ## Install Python dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

dev: ## Run the app locally in development mode
	@echo "$(BLUE)Starting development server...$(NC)"
	@export ENVIRONMENT=development && uvicorn main:app --reload --host 0.0.0.0 --port 8000

prod-local: ## Run the app locally in production mode
	@echo "$(BLUE)Starting production server (local)...$(NC)"
	@export ENVIRONMENT=production && uvicorn main:app --host 0.0.0.0 --port 8000

venv: ## Create virtual environment
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	python3 -m venv banking_env
	@echo "$(GREEN)✓ Virtual environment created$(NC)"
	@echo "Activate with: source banking_env/bin/activate"

##@ Docker Commands

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker-compose build
	@echo "$(GREEN)✓ Docker image built$(NC)"

docker-dev: ## Run app in Docker (development mode)
	@echo "$(BLUE)Starting Docker container (development)...$(NC)"
	docker-compose -f docker-compose.dev.yml up --build

docker-dev-d: ## Run app in Docker (development mode, detached)
	@echo "$(BLUE)Starting Docker container (development, detached)...$(NC)"
	docker-compose -f docker-compose.dev.yml up -d --build
	@echo "$(GREEN)✓ Container started in background$(NC)"
	@echo "View logs with: make logs"

docker-prod: ## Run app in Docker (production mode)
	@echo "$(BLUE)Starting Docker container (production)...$(NC)"
	docker-compose up --build

docker-prod-d: ## Run app in Docker (production mode, detached)
	@echo "$(BLUE)Starting Docker container (production, detached)...$(NC)"
	docker-compose up -d --build
	@echo "$(GREEN)✓ Container started in background$(NC)"
	@echo "View logs with: make logs-prod"

docker-stop: ## Stop Docker containers
	@echo "$(YELLOW)Stopping Docker containers...$(NC)"
	docker-compose -f docker-compose.dev.yml stop || true
	docker-compose stop || true
	@echo "$(GREEN)✓ Containers stopped$(NC)"

docker-down: ## Stop and remove Docker containers
	@echo "$(YELLOW)Stopping and removing Docker containers...$(NC)"
	docker-compose -f docker-compose.dev.yml down || true
	docker-compose down || true
	@echo "$(GREEN)✓ Containers removed$(NC)"

docker-clean: ## Remove Docker containers, volumes, and images
	@echo "$(RED)Cleaning Docker resources...$(NC)"
	docker-compose -f docker-compose.dev.yml down -v --rmi all || true
	docker-compose down -v --rmi all || true
	@echo "$(GREEN)✓ Docker resources cleaned$(NC)"

docker-restart: docker-stop docker-dev-d ## Restart Docker containers

logs: ## View Docker logs (development)
	docker-compose -f docker-compose.dev.yml logs -f

logs-prod: ## View Docker logs (production)
	docker-compose logs -f

shell: ## Open shell in Docker container
	docker-compose -f docker-compose.dev.yml exec banking-api /bin/bash

##@ Testing

test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	pytest -v

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	pytest tests/unit/ -v

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	pytest tests/integration/ -v

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	pytest --cov=app --cov=main --cov-report=term --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✓ Coverage report generated$(NC)"
	@echo "HTML report: htmlcov/index.html"

test-cov-report: ## Generate coverage report to text files
	@echo "$(BLUE)Generating coverage reports...$(NC)"
	pytest --cov=app --cov=main --cov-report=term --cov-report=html --cov-report=term-missing > coverage_report.txt 2>&1
	pytest --cov=app --cov=main --cov-report=term-missing:skip-covered --cov-report=html -v --tb=no -q 2>&1 | tee coverage_report_detailed.txt
	@echo "$(GREEN)✓ Coverage reports generated$(NC)"
	@echo "  - coverage_report.txt"
	@echo "  - coverage_report_detailed.txt"
	@echo "  - COVERAGE_SUMMARY.txt"
	@echo "  - htmlcov/index.html"

test-watch: ## Run tests in watch mode (requires pytest-watch)
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	ptw --runner "pytest -v"

##@ Database

db-clean: ## Remove database file (fresh start)
	@echo "$(YELLOW)Removing database...$(NC)"
	rm -f data/banking.db
	@echo "$(GREEN)✓ Database removed$(NC)"

db-reset: db-clean ## Reset database (remove and recreate)
	@echo "$(BLUE)Database will be recreated on next app start$(NC)"

##@ Code Quality

format: ## Format code with black
	@echo "$(BLUE)Formatting code...$(NC)"
	black app/ tests/ main.py
	@echo "$(GREEN)✓ Code formatted$(NC)"

lint: ## Lint code with flake8
	@echo "$(BLUE)Linting code...$(NC)"
	flake8 app/ tests/ main.py --max-line-length=120 --exclude=banking_env
	@echo "$(GREEN)✓ Linting complete$(NC)"

check: format lint ## Format and lint code
	@echo "$(GREEN)✓ Code check complete$(NC)"

##@ Health & Monitoring

health: ## Check API health
	@echo "$(BLUE)Checking API health...$(NC)"
	@curl -s http://localhost:8000/health | python -m json.tool || echo "$(RED)API not responding$(NC)"

health-ready: ## Check API readiness (with DB)
	@echo "$(BLUE)Checking API readiness...$(NC)"
	@curl -s http://localhost:8000/health/ready | python -m json.tool || echo "$(RED)API not ready$(NC)"

docs: ## Open API documentation in browser
	@echo "$(BLUE)Opening API documentation...$(NC)"
	@which xdg-open > /dev/null && xdg-open http://localhost:8000/docs || echo "Open http://localhost:8000/docs in your browser"

##@ Cleanup

clean: ## Clean up generated files
	@echo "$(YELLOW)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.coverage" -delete 2>/dev/null || true
	rm -rf htmlcov/ 2>/dev/null || true
	rm -rf .coverage 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-all: clean docker-clean db-clean ## Clean everything (Docker, DB, generated files)
	@echo "$(GREEN)✓ Full cleanup complete$(NC)"

##@ Production

prod-setup: ## Setup production environment
	@echo "$(BLUE)Setting up production environment...$(NC)"
	@if [ ! -f .env.production ]; then \
		echo "$(RED)Error: .env.production not found$(NC)"; \
		echo "Create it from .env.example and configure SECRET_KEY"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ Production environment ready$(NC)"

graceful-shutdown-test: ## Test graceful shutdown
	@echo "$(BLUE)Testing graceful shutdown...$(NC)"
	@chmod +x test_graceful_shutdown.sh
	@./test_graceful_shutdown.sh

##@ Information

status: ## Show status of containers and services
	@echo "$(BLUE)Docker Containers:$(NC)"
	@docker-compose -f docker-compose.dev.yml ps 2>/dev/null || echo "No dev containers running"
	@docker-compose ps 2>/dev/null || echo "No prod containers running"
	@echo ""
	@echo "$(BLUE)Database:$(NC)"
	@if [ -f data/banking.db ]; then \
		echo "$(GREEN)✓ Database exists$(NC) ($(shell du -h data/banking.db 2>/dev/null | cut -f1))"; \
	else \
		echo "$(YELLOW)⚠ Database not found$(NC)"; \
	fi
	@echo ""
	@echo "$(BLUE)Coverage Reports:$(NC)"
	@if [ -f COVERAGE_SUMMARY.txt ]; then \
		echo "$(GREEN)✓ Coverage reports exist$(NC)"; \
	else \
		echo "$(YELLOW)⚠ No coverage reports$(NC)"; \
	fi

info: ## Show project information
	@echo "$(BLUE)Banking App API$(NC)"
	@echo "Version: 1.0.0"
	@echo ""
	@echo "$(BLUE)Endpoints:$(NC)"
	@echo "  API:        http://localhost:8000"
	@echo "  Health:     http://localhost:8000/health"
	@echo "  Ready:      http://localhost:8000/health/ready"
	@echo "  Docs:       http://localhost:8000/docs"
	@echo "  ReDoc:      http://localhost:8000/redoc"
	@echo ""
	@echo "$(BLUE)Quick Commands:$(NC)"
	@echo "  make dev           - Run locally"
	@echo "  make docker-dev    - Run in Docker"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage"
	@echo "  make help          - Show all commands"
