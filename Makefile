# Wingman Makefile
# Common commands for development and installation

.PHONY: help install install-dev test clean build dist build-standalone release version

help: ## Show this help message
	@echo "Wingman - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install Wingman in production mode
	pip install -e .

install-dev: ## Install Wingman in development mode with dev dependencies
	pip install -e .
	pip install -e ".[dev]"

test: ## Run tests
	python test_installation.py

test-cli: ## Test CLI commands
	wingman --help
	wingman extract-fields --help
	wingman replace-fields --help
	wingman test-connection --help

clean: ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	python -m build

dist: clean build ## Create distribution packages
	python -m build

install-sf-cli: ## Install Salesforce CLI
	npm install -g @salesforce/cli

setup: install-sf-cli install ## Complete setup (install SF CLI + Wingman)

format: ## Format code with black
	black wingman/

lint: ## Lint code with flake8
	flake8 wingman/

type-check: ## Type check with mypy
	mypy wingman/

check: format lint type-check ## Run all code quality checks

quick-test: ## Quick test with a sample org (requires SF CLI setup)
	@echo "Testing connection to default org..."
	@if sf org list --json | jq -e '.result | (.other + .sandboxes + .nonScratchOrgs + .devHubs + .scratchOrgs) | length > 0' > /dev/null 2>&1; then \
		echo "Found authenticated orgs. Testing connection..."; \
		sf org list; \
	else \
		echo "No authenticated orgs found. Please run 'sf org login web' first."; \
	fi

demo: ## Run a demo (requires authenticated org)
	@echo "Running Wingman demo..."
	@echo "1. Testing connection..."
	@if sf org list --json | jq -e '.result | (.other + .sandboxes + .nonScratchOrgs + .devHubs + .scratchOrgs) | length > 0' > /dev/null 2>&1; then \
		echo "✓ Found authenticated orgs"; \
		echo "2. Running field extraction demo..."; \
		wingman extract-fields --org $$(sf org list --json | jq -r '.result | (.other + .sandboxes + .nonScratchOrgs + .devHubs + .scratchOrgs)[0].alias') --objects Account --max-fields 5; \
	else \
		echo "✗ No authenticated orgs found. Please run 'sf org login web' first."; \
	fi

build-standalone: ## Build standalone executable for current platform
	python3 scripts/build.py

release: ## Create a new release (requires version argument)
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make release VERSION=x.y.z"; \
		echo "Example: make release VERSION=1.0.0"; \
		exit 1; \
	fi
	python3 scripts/version.py $(VERSION)

version: ## Show current version
	@python3 -c "import toml; print(toml.load('pyproject.toml')['project']['version'])"

build-all: ## Build for all platforms (requires Docker)
	@echo "Building for all platforms using Docker..."
	docker run --rm -v "$(PWD)":/workspace -w /workspace python:3.11-slim bash -c "pip install pyinstaller && python scripts/build.py"
	docker run --rm -v "$(PWD)":/workspace -w /workspace python:3.11-slim bash -c "pip install pyinstaller && python scripts/build.py"

package: build-standalone ## Create distribution package
	@echo "Distribution package created in wingman-dist/"

install-standalone: ## Install standalone executable locally
	@if [ -d "wingman-dist" ]; then \
		cp wingman-dist/wingman* ~/.local/bin/ 2>/dev/null || cp wingman-dist/wingman* /usr/local/bin/ 2>/dev/null || echo "Please copy wingman-dist/wingman to your PATH"; \
		chmod +x ~/.local/bin/wingman* 2>/dev/null || chmod +x /usr/local/bin/wingman* 2>/dev/null || true; \
		echo "✓ Standalone executable installed"; \
	else \
		echo "Run 'make build-standalone' first"; \
	fi

