# AGENTS.md

Four Copilot custom agents (`agents/*.agent.md`) implementing the Ralph loop. No code, just Markdown prompts. Usage and design: [README.md](README.md).

## Make targets

- `make help` lists targets.
- `make lint` runs shellcheck + `bash -n` on tracked `*.sh` files (none yet).
- `make test` smoke-checks that every `agents/*.agent.md` has YAML frontmatter with a `name:`.
- `make check` = lint + test; CI runs it in the required `check` job, alongside gitleaks.

## Rules

- Change `main` only through a squash-merged PR with a Conventional Commit title; see the [GitHub standard](https://github.com/giocaizzi/.github/blob/main/docs/standard.md).
- Agent `name:` values (`RalphPlanner`, `RalphCoordinator`, `RalphExecutor`, `RalphReviewer`) are referenced by `agents:` and `handoffs:` in the other files; rename them together.
