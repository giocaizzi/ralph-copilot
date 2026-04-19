#!/usr/bin/env python3
"""Generate dual-format agent files from source.

Source layout (edit here):
  agents/<name>/body.md             shared system prompt
  agents/<name>/copilot.yaml        Copilot CLI frontmatter fields
  agents/<name>/claude.yaml         Claude Code frontmatter fields

Generated output (do not edit):
  agents/dist/claude/<name>.md      Claude Code format
  agents/dist/copilot/<name>.agent.md  Copilot CLI format
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
AGENTS_ROOT = REPO_ROOT / "agents"
DIST = REPO_ROOT / "dist"

def _render(frontmatter_yaml: str, body: str) -> str:
    return f"---\n{frontmatter_yaml.strip()}\n---\n\n{body.strip()}\n"


def build_agent(name: str, *, check: bool = False) -> bool:
    src = AGENTS_ROOT / name
    missing = [f for f in ("body.md", "copilot.yaml", "claude.yaml") if not (src / f).exists()]
    if missing:
        print(f"ERROR: {name}: missing source files: {missing}", file=sys.stderr)
        return False

    body = (src / "body.md").read_text()
    copilot_fm = (src / "copilot.yaml").read_text()
    claude_fm = (src / "claude.yaml").read_text()

    targets = {
        DIST / f"{name}.md": _render(claude_fm, body),
        DIST / f"{name}.agent.md": _render(copilot_fm, body),
    }

    ok = True
    for out_path, content in targets.items():
        if check:
            if not out_path.exists() or out_path.read_text() != content:
                print(f"  OUT OF SYNC: {out_path.relative_to(REPO_ROOT)}", file=sys.stderr)
                ok = False
        else:
            out_path.write_text(content)
            print(f"  written: {out_path.relative_to(REPO_ROOT)}")
    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="Validate generated files are up to date (exit 1 if not)")
    args = parser.parse_args()

    DIST.mkdir(parents=True, exist_ok=True)

    agents = sorted(
        d.name for d in AGENTS_ROOT.iterdir()
        if d.is_dir() and not d.name.startswith(".") and d.name != "dist"
        and (d / "body.md").exists()
    )
    if not agents:
        print(f"ERROR: no agents found in {AGENTS_ROOT}", file=sys.stderr)
        sys.exit(1)

    verb = "Checking" if args.check else "Building"
    print(f"{verb} {len(agents)} agent(s): {', '.join(agents)}")

    ok = all(build_agent(name, check=args.check) for name in agents)

    if args.check:
        if ok:
            print("All agent files are up to date.")
        else:
            print("\nRun `make build` to regenerate.", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
