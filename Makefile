.PHONY: build validate

build: ## Generate dual-format agent files from agents/
	python scripts/build_agents.py

validate: ## Validate generated agent files are up to date
	python scripts/build_agents.py --check