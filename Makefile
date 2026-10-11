.PHONY: help lint test check

help: ## List targets.
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make <target>\n\nTargets:\n"} /^[a-zA-Z_-]+:.*##/ { printf "  %-8s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

lint: ## Lint (none configured).
	@echo "no lint configured"

test: ## Tests (none configured).
	@echo "no tests configured"

check: lint test ## Standard gate: lint + test.
