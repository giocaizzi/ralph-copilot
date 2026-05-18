#!/usr/bin/env python3
"""Validate repo invariants for the single-plugin layout rooted at ralph/."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
PLUGIN_ROOT = REPO_ROOT / "ralph"
CLAUDE_MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
COPILOT_MANIFEST = PLUGIN_ROOT / ".github" / "plugin" / "plugin.json"
CLAUDE_AGENTS = PLUGIN_ROOT / "agents"
README = REPO_ROOT / "README.md"


class Reporter:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def fail(self, message: str) -> None:
        self.errors.append(message)

    def section(self, title: str) -> None:
        print(f"\n> {title}")

    def ok(self, message: str) -> None:
        print(f"  OK {message}")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_native_validator(reporter: Reporter) -> None:
    reporter.section("Native Claude validator")
    claude = shutil.which("claude")
    if claude is None:
        reporter.ok("skipped (claude CLI not installed)")
        return

    targets = [CLAUDE_MANIFEST, MARKETPLACE]
    for target in targets:
        result = subprocess.run([claude, "plugin", "validate", str(target)], capture_output=True, text=True)
        if result.returncode != 0:
            output = (result.stdout + result.stderr).strip()
            reporter.fail(f"{target.relative_to(REPO_ROOT)}: native validator failed\n{output}")
            continue
        reporter.ok(str(target.relative_to(REPO_ROOT)))


def check_repo_specific_manifests(reporter: Reporter) -> None:
    reporter.section("Manifest sync")
    if not CLAUDE_MANIFEST.exists():
        reporter.fail(f"{CLAUDE_MANIFEST.relative_to(REPO_ROOT)}: missing")
        return

    manifest = _load_json(CLAUDE_MANIFEST)
    if "skills" in manifest:
        reporter.fail(f"{CLAUDE_MANIFEST.relative_to(REPO_ROOT)}: must not declare `skills`")
    if "agents" in manifest:
        reporter.fail(f"{CLAUDE_MANIFEST.relative_to(REPO_ROOT)}: must not declare `agents`")

    if not COPILOT_MANIFEST.exists():
        reporter.fail(f"{COPILOT_MANIFEST.relative_to(REPO_ROOT)}: missing - run `make build`")
        return

    copilot = _load_json(COPILOT_MANIFEST)
    if copilot.get("version") != manifest.get("version"):
        reporter.fail(
            f"{COPILOT_MANIFEST.relative_to(REPO_ROOT)}: version drift vs plugin.json ({copilot.get('version')!r} vs {manifest.get('version')!r})"
        )
    if copilot.get("agents") != ["./copilot/"]:
        reporter.fail(f"{COPILOT_MANIFEST.relative_to(REPO_ROOT)}: expected `agents` to be ['./copilot/']")
        return
    reporter.ok("ralph")


def check_marketplace(reporter: Reporter) -> None:
    reporter.section("Marketplace sync")
    if not MARKETPLACE.exists():
        reporter.fail(f"{MARKETPLACE.relative_to(REPO_ROOT)}: missing")
        return

    market = _load_json(MARKETPLACE)
    listed = market.get("plugins", [])
    if len(listed) != 1 or listed[0].get("name") != "ralph":
        reporter.fail("marketplace.json must list exactly one plugin named 'ralph'")
        return

    entry = listed[0]
    manifest = _load_json(CLAUDE_MANIFEST)
    if entry.get("version") != manifest.get("version"):
        reporter.fail(f"version drift: marketplace={entry.get('version')!r} plugin={manifest.get('version')!r}")
    if entry.get("source") not in {"./ralph", "ralph"}:
        reporter.fail(f"marketplace source {entry.get('source')!r} should be './ralph'")
    if market.get("name") != "ralph":
        reporter.fail(f"marketplace name {market.get('name')!r} should be 'ralph'")
    reporter.ok(f"ralph @ {manifest.get('version')}")


def check_build_sync(reporter: Reporter) -> None:
    reporter.section("Generated artifact sync")
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "build_agents.py"), "--check"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        reporter.fail(output or "build sync check failed")
        return
    reporter.ok("generated agents and manifests are in sync")


def check_readmes(reporter: Reporter) -> None:
    reporter.section("README sync")
    if not README.exists():
        reporter.fail("README.md is missing")
        return

    root_text = README.read_text(encoding="utf-8")
    required_refs = (
        ".claude-plugin/marketplace.json",
        "src/agents/<agent>/",
        "ralph/.claude-plugin/plugin.json",
        "ralph/agents/",
        "ralph/copilot/",
        "ralph/.github/plugin/",
        "make build",
        "ralph/agents/*.md",
        "ralph/copilot/*.agent.md",
    )
    for ref in required_refs:
        if ref not in root_text:
            reporter.fail(f"README.md missing layout reference for {ref}")

    for agent_file in sorted(CLAUDE_AGENTS.glob("*.md")):
        if f"`{agent_file.stem}`" not in root_text:
            reporter.fail(f"README.md missing agent reference for `{agent_file.stem}`")
    reporter.ok("README")


def main() -> None:
    reporter = Reporter()
    check_native_validator(reporter)
    check_repo_specific_manifests(reporter)
    check_marketplace(reporter)
    check_build_sync(reporter)
    check_readmes(reporter)

    print()
    if reporter.errors:
        print(f"FAIL: {len(reporter.errors)} error(s)", file=sys.stderr)
        for error in reporter.errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    print("All checks passed.")


if __name__ == "__main__":
    main()