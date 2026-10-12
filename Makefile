.PHONY: help lint test check

SH_FILES := $(shell git ls-files '*.sh')

help: ## List targets.
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make <target>\n\nTargets:\n"} /^[a-zA-Z_-]+:.*##/ { printf "  %-8s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

lint: ## Lint shell scripts (shellcheck + bash -n).
	@for f in $(SH_FILES); do bash -n "$$f" && shellcheck "$$f" || exit 1; done

test: ## Smoke test: every agent file has a name in its frontmatter.
	@for f in agents/*.agent.md; do head -1 "$$f" | grep -qx -- '---' && grep -q '^name: ' "$$f" || { echo "bad frontmatter: $$f"; exit 1; }; done

check: lint test ## Standard gate: lint + test.
