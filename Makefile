.PHONY: help build validate clean

help: ## Show available targets.
	@echo Usage: make '<target>'
	@echo.
	@echo Targets:
	@echo   build       Generate root agents, copilot agents, and Copilot manifest
	@echo   validate    Validate generated files, manifests, marketplace, and README sync
	@echo   clean       Remove generated plugin artifacts

build: ## Generate root agents, Copilot agents, and Copilot manifest.
	@python scripts/build_agents.py

validate: ## Validate generated files, manifests, marketplace, and README sync.
	@python scripts/validate.py

clean: ## Remove generated plugin artifacts.
	@python scripts/build_agents.py --clean
