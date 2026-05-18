#!/usr/bin/env python3
"""Generate dual-harness plugin artifacts for the single-plugin repo.

The plugin root is ralph/.

For every agent in src/agents/<name>/ the script writes:
    ralph/agents/<name>.md         <- Claude Code / VS Code Claude-format agent
    ralph/copilot/<name>.agent.md  <- Copilot / VS Code YAML-format agent

The script also writes:
    ralph/.github/plugin/plugin.json <- Copilot manifest derived from
                                        ralph/.claude-plugin/plugin.json with
                                        `agents: ["./copilot/"]`.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_AGENTS = REPO_ROOT / "src" / "agents"
PLUGIN_ROOT = REPO_ROOT / "ralph"
CLAUDE_MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
CLAUDE_AGENTS = PLUGIN_ROOT / "agents"
COPILOT_AGENTS = PLUGIN_ROOT / "copilot"
COPILOT_MANIFEST = PLUGIN_ROOT / ".github" / "plugin" / "plugin.json"

TOP_LEVEL_KEY_RE = re.compile(r"^(?P<key>[A-Za-z][A-Za-z0-9_-]*):(?:\s|$)")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalize_block(text: str) -> str:
    return text.strip()


def _scalar_field(text: str, key: str) -> str | None:
    pattern = re.compile(rf"^{re.escape(key)}:\s*(.+?)\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return None
    value = match.group(1).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _top_level_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for line in text.splitlines():
        if not line or line[:1] in {" ", "\t"}:
            continue
        match = TOP_LEVEL_KEY_RE.match(line)
        if match:
            keys.add(match.group("key"))
    return keys


def _strip_shared_keys(shared_text: str, override_text: str) -> str:
    override_keys = _top_level_keys(override_text)
    if not override_keys:
        return _normalize_block(shared_text)

    kept_lines: list[str] = []
    for line in shared_text.splitlines():
        match = TOP_LEVEL_KEY_RE.match(line)
        if match and match.group("key") in override_keys:
            continue
        kept_lines.append(line)
    return _normalize_block("\n".join(kept_lines))


def _merge_frontmatter(shared_text: str, override_text: str) -> str:
    shared_block = _strip_shared_keys(shared_text, override_text)
    override_block = _normalize_block(override_text)
    if shared_block and override_block:
        return f"{shared_block}\n{override_block}"
    return shared_block or override_block


def _render(frontmatter_yaml: str, body: str) -> str:
    return f"---\n{frontmatter_yaml.strip()}\n---\n\n{body.strip()}\n"


def _build_agent(name: str, *, check: bool) -> bool:
    src = SRC_AGENTS / name
    required = ("agent.yaml", "body.md", "claude.yaml", "copilot.yaml")
    missing = [filename for filename in required if not (src / filename).exists()]
    if missing:
        print(f"ERROR: {name}: missing source files: {missing}", file=sys.stderr)
        return False

    shared_text = _read_text(src / "agent.yaml")
    body = _read_text(src / "body.md")
    claude_overrides = _read_text(src / "claude.yaml")
    copilot_overrides = _read_text(src / "copilot.yaml")

    shared_name = _scalar_field(shared_text, "name")
    description = _scalar_field(shared_text, "description")
    if shared_name != name:
        print(f"ERROR: {name}: agent.yaml `name` ({shared_name!r}) must match dir name", file=sys.stderr)
        return False
    if not description:
        print(f"ERROR: {name}: agent.yaml is missing required `description`", file=sys.stderr)
        return False

    plugin = _scalar_field(shared_text, "plugin")
    if plugin and plugin != "ralph":
        print(f"ERROR: {name}: agent.yaml `plugin` must be 'ralph' if specified", file=sys.stderr)
        return False
    if not CLAUDE_MANIFEST.exists():
        print(f"ERROR: missing {CLAUDE_MANIFEST.relative_to(REPO_ROOT)}", file=sys.stderr)
        return False

    base_text = _strip_shared_keys(shared_text, "plugin:")
    claude_fm = _merge_frontmatter(base_text, claude_overrides)
    copilot_fm = _merge_frontmatter(base_text, copilot_overrides)

    targets = {
        CLAUDE_AGENTS / f"{name}.md": _render(claude_fm, body),
        COPILOT_AGENTS / f"{name}.agent.md": _render(copilot_fm, body),
    }

    ok = True
    for path, content in targets.items():
        rel = path.relative_to(REPO_ROOT)
        if check:
            if not path.exists() or _read_text(path) != content:
                print(f"  OUT OF SYNC: {rel}", file=sys.stderr)
                ok = False
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"  written: {rel}")
    return ok


def _build_copilot_manifest(*, check: bool) -> bool:
    if not CLAUDE_MANIFEST.exists():
        print(f"ERROR: {CLAUDE_MANIFEST.relative_to(REPO_ROOT)}: missing", file=sys.stderr)
        return False

    data = json.loads(_read_text(CLAUDE_MANIFEST))
    copilot_data = {**data, "agents": ["./copilot/"]}
    content = json.dumps(copilot_data, indent=2) + "\n"

    rel = COPILOT_MANIFEST.relative_to(REPO_ROOT)
    if check:
        if not COPILOT_MANIFEST.exists() or _read_text(COPILOT_MANIFEST) != content:
            print(f"  OUT OF SYNC: {rel}", file=sys.stderr)
            return False
    else:
        COPILOT_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        COPILOT_MANIFEST.write_text(content, encoding="utf-8")
        print(f"  written: {rel}")
    return True


def _clean_generated() -> None:
    shutil.rmtree(CLAUDE_AGENTS, ignore_errors=True)
    shutil.rmtree(COPILOT_AGENTS, ignore_errors=True)
    shutil.rmtree(PLUGIN_ROOT / ".github", ignore_errors=True)
    print("Removed generated plugin artifacts.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="Exit 1 if generated files are out of sync.")
    parser.add_argument("--clean", action="store_true", help="Remove generated plugin artifacts.")
    args = parser.parse_args()

    if args.clean:
        _clean_generated()
        return

    if not SRC_AGENTS.exists():
        print(f"ERROR: source dir not found: {SRC_AGENTS}", file=sys.stderr)
        sys.exit(1)

    agents = sorted(
        directory.name
        for directory in SRC_AGENTS.iterdir()
        if directory.is_dir() and not directory.name.startswith(".") and (directory / "agent.yaml").exists()
    )
    verb = "Checking" if args.check else "Building"
    print(f"{verb} {len(agents)} agent(s): {', '.join(agents) or '(none)'}")
    ok_agents = all(_build_agent(name, check=args.check) for name in agents)

    print(f"{verb} 1 Copilot manifest(s): ralph")
    ok_manifests = _build_copilot_manifest(check=args.check)

    if not (ok_agents and ok_manifests):
        if args.check:
            print("\nRun `make build` to regenerate.", file=sys.stderr)
        sys.exit(1)

    if args.check:
        print("All generated files are up to date.")


if __name__ == "__main__":
    main()
