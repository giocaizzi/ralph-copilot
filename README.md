# Ralph Loop

An implementation of the autonomous agent loop [**Ralph Wiggum as a "software engineer"** pattern by Geoffrey Huntley](https://ghuntley.com/ralph/), using custom agents with automatic handoffs.

Works with **VS Code Copilot**, **Copilot CLI**, and **Claude Code**.

<p align="center"><img src="assets/ralph-copilot.png" height="200" alt="Ralph Copilot"></p>

Based on four agents, this pattern enables an **autonomous coding loop** with **fresh context every iteration**, using the filesystem as memory and `git` for version control.

## What is Ralph Loop?

**Ralph loop = Fresh context + Filesystem memory & Git versioning**

An autonomous coding pattern where:

0. User provides requirements to a `RalphPlanner` agent, which creates a `PRD.md` with a list of specific tasks and a file to track progress `PROGRESS.md`
1. User reviews `PRD.md` and starts the loop with `RalphCoordinator` agent who dispatches tasks to `RalphExecutor` agents.
2. `RalphExecutor` agent picks a task from `PRD.md`
3. Executes it with **fresh context**, code is tested and quality checks ensured
4. `git` commits and updates `PROGRESS.md`
5. Code is reviewed by `RalphReviewer`
6. Loops until all tasks complete

### Execution Flow

```mermaid
sequenceDiagram
    participant H as 👤 User
    participant P as 🤖 Planner
    participant C as 🤖 Coordinator
    participant E as 🤖 Executor
    participant R as 🤖 Reviewer
    participant FS as 📝 Filesystem

    H->>P: Requirements
    P->>FS: Write PRD.md + PROGRESS.md
    P-->>H: Handoff button: Start Ralph Loop

    H->>C: Start loop

    loop Until all tasks complete
        C->>FS: Read PRD.md + PROGRESS.md
        C->>+E: Spawn subagent (task + criteria)
        E->>FS: Read PRD.md + PROGRESS.md
        E->>E: Implement task
        E->>+R: Spawn subagent (verify task)
        R->>FS: Read code + acceptance criteria
        R-->>-E: Verdict (pass / fail + notes)
        E->>FS: Update PROGRESS.md
        E->>FS: git commit
        E-->>-C: Completion summary
    end

    C-->>H: COMPLETE
```

## Features

- 🤝 **Automatic handoffs** - Agents pass control automatically with fresh context
- 📝 **Progress file and filesystem memory** - Fresh context every iteration via `PROGRESS.md` and `git`
- 🌐 **Language agnostic** - Works with any programming language/stack
- ⚛️ **Atomic tasks** - One task per iteration, committed immediately
- 🔄 **Context reset** - Avoids context pollution, uses filesystem as memory
- 🔍 **Built-in review** - Reviewer subagent verifies every task before moving on
- ✅ **Code that lasts** - Maintainable code with tests and quality checks at every iteration

## Compatibility

| Harness | Format | Install method |
|---|---|---|
| VS Code Copilot | `.md` | plugin or manual |
| Claude Code | `.md` | `/plugin install` |
| Copilot CLI | `.agent.md` | plugin or manual |

Both formats are generated into `dist/` from a single source via `make build`.

## Setup

### Plugin install (recommended)

**Claude Code:**

```
/plugin install giocaizzi/ralph-copilot
```

**Copilot CLI:**

```bash
copilot plugin install giocaizzi/ralph-copilot
```

### Manual install

Clone and copy agent files to your project's `.github/agents/` directory:

```bash
git clone git@github.com:giocaizzi/ralph-copilot.git

# VS Code Copilot or Claude Code
cp ralph-copilot/dist/*.md <your_project>/.github/agents/

# Copilot CLI
cp ralph-copilot/dist/*.agent.md <your_project>/.github/agents/
```

Restart your agent harness and verify agents are available — you should see `RalphPlanner` and `RalphCoordinator`.

> 💡 **Use Ralph globally across all projects**
>
> *VS Code Copilot / Claude Code:* Point VS Code to your local clone once via
> [![VS Code setting chat.agentFilesLocations](https://img.shields.io/badge/VS%20Code-chat.agentFilesLocations-007ACC?style=flat&logo=visualstudiocode&logoColor=white)](vscode://settings/chat.agentFilesLocations):
>
> ```jsonc
> // settings.json
> "chat.agentFilesLocations": {
>     "/your/path/to/ralph-copilot": true
> }
> ```
>
> *Copilot CLI:* Save agents to the global folder `~/.copilot/agents`

## Usage

### Quick Start

1. **Create PRD** with `RalphPlanner` agent:

   ```
   Open VSCode Chat
   Select: RalphPlanner
   Prompt: "Create a PRD for [your feature]"
   ```

2. **Review PRD.md** - Edit as needed

3. **Start Loop** with `RalphCoordinator` agent:

   ```
   Select: RalphCoordinator
   Click: "Start Ralph Loop" handoff button
   ```

4. **Let it run** - Agents will:
   - Pick tasks from PRD.md
   - Execute them
   - Update PROGRESS.md
   - Commit changes
   - Review, test and run quality checks
   - Repeat until done

5. **Monitor progress** in PROGRESS.md and git history

## Credits

Based on:

- [**Ralph Wiggum as a "software engineer"** pattern by Geoffrey Huntley](https://ghuntley.com/ralph/)
- [Ralph](https://github.com/snarktank/ralph)
- [VS Code Custom Agents Docs](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
- [Claude Code Custom Agents Docs](https://docs.anthropic.com/en/docs/claude-code/custom-agents)
- [Claude Code Ralph Loop](https://github.com/anthropics/claude-code/blob/main/plugins/ralph-wiggum/README.md)
