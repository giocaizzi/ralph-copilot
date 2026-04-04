# Copilot Ralph Loop

A lightweight Copilot implementation of the autonomous agent loop [**Ralph Wiggum as a "software engineer"** pattern by Geoffrey Huntley](https://ghuntley.com/ralph/), using custom agents with automatic handoffs.

<p align="center"><img src="assets/ralph-copilot.png" height="200" alt="Ralph Copilot"></p>

Based on only four `agent.md` markdown files, this pattern enables an **autonomous coding loop** with **fresh context every iteration**, using the filesystem as memory and `git` for version control.
It is optimized for Copilot premium-request efficiency by increasing the amount of work done inside one coordinator request via subagent parallelism.

## What is Ralph Loop?

**Ralph loop = Fresh context + Filesystem memory & Git versioning**

An autonomous coding pattern where:

0. User provides requirements to a `RalphPlanner` agent, which creates a `PRD.md` with a list of specific tasks and a file to track progress `PROGRESS.md`
1. User reviews `PRD.md` and starts the loop with `RalphCoordinator`, which dispatches up to 5 `RalphExecutor` agents in parallel
2. Coordinator schedules only tasks whose `Depends on` entries are already complete
3. Each `RalphExecutor` executes one task with **fresh context**, commits, and updates only its task status in `PROGRESS.md`
4. Each task is immediately reviewed by `RalphReviewer` (PASS/FAIL per task)
5. FAIL tasks are re-run with fix instructions; PASS tasks are marked done
6. Loop continues until all tasks are done

### Execution Flow

```mermaid
sequenceDiagram
    participant H as 👤 User
    participant P as 🤖 Planner
    participant C as 🤖 Coordinator
    participant E1 as 🤖 Executor #1..#5
    participant R as 🤖 Reviewer
    participant FS as 📝 Filesystem

    H->>P: Requirements
    P->>FS: Write PRD.md + PROGRESS.md
    P-->>H: Handoff button: Start Ralph Loop

    H->>C: Start loop

    loop Until all tasks complete
        C->>FS: Read PRD.md + PROGRESS.md
        C->>C: Build ready queue from Depends on
        C->>+E1: Spawn up to 5 subagents (ready tasks)
        E1->>FS: Read PRD.md + PROGRESS.md
        E1->>E1: Implement one task
        E1->>FS: Update own task row in PROGRESS.md
        E1->>FS: git commit
        E1->>+R: Spawn subagent (verify same task)
        R->>FS: Read code + acceptance criteria
        R-->>-E1: Verdict (pass / fail + notes)
        E1-->>-C: Task summary + review verdict
        C->>C: PASS => done, FAIL => requeue
    end

    C-->>H: COMPLETE
```

## Features

- 🤝 **Automatic handoffs** - Agents pass control automatically with fresh context
- 📝 **Progress file and filesystem memory** - Fresh context every iteration via `PROGRESS.md` and `git`
- 🌐 **Language agnostic** - Works with any programming language/stack
- ⚛️ **Parallel atomic tasks** - Up to 5 task iterations in flight, each committed independently
- 🔄 **Context reset** - Avoids context pollution, uses filesystem as memory
- 🔍 **Built-in review** - Reviewer subagent verifies every task before task completion
- 💸 **Premium-request efficient** - More work per coordinator request via parallel subagents
- ✅ **Code that lasts** - Maintainable code with tests and quality checks at every iteration

## Compatibility

- 🖥️ **VS Code Copilot** - save agents in the workspace `.github/agents` or [customize your settings.json](#Installation)
- 🤖 **Copilot CLI** - save agents in workspace `.github/agents` or in global `~/.copilot/agents`

## Setup

### Installation

1. Clone repository and copy agent files to your project:

```bash
git clone git@github.com:giocaizzi/ralph-copilot.git
cp ralph-copilot/agents/*.agent.md <your_project>/.github/agents/
```

2. Restart VSCode/Copilot CLI

3. Verify agents are available:
   - Open Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
   - Type "Select Agent"
   - Should see: `RalphPlanner`, `RalphCoordinator`

> 💡 **Tip — use Ralph globally across all your projects**
>
> *VSCode*:
> Instead of copying agent files per project, point VS Code to your local clone of this repo once via
> [![VS Code setting chat.agentFilesLocations](https://img.shields.io/badge/VS%20Code-chat.agentFilesLocations-007ACC?style=flat&logo=visualstudiocode&logoColor=white)](vscode://settings/chat.agentFilesLocations)
> and the agents will be available everywhere.
>
> ```jsonc
> // settings.json
> "chat.agentFilesLocations": {
>     "/your/path/to/ralph-copilot": true
> }
> ```
>
> *Copilot CLI*
> Save your agents in the global folder `~/.copilot/agents`

## Usage

### Quick Start

1. **Create PRD** with `RalphPlanner` agent:

   ```
   Open VSCode Chat
   Select: RalphPlanner
   Prompt: "Create a PRD for [your feature]"
   ```

2. **Review PRD.md** - Edit as needed
   - Ensure every task has `Depends on: [...]`

3. **Start Loop** with `RalphCoordinator` agent:

   ```
   Select: RalphCoordinator
   Click: "Start Ralph Loop" handoff button
   ```

4. **Let it run** - Agents will:
   - Select dependency-ready tasks from PRD.md
   - Run up to 5 executors in parallel
   - Update task-level status in PROGRESS.md
   - Commit changes per task
   - Review each task immediately (PASS/FAIL)
   - Requeue failed tasks automatically
   - Repeat until done

5. **Monitor progress** in PROGRESS.md and git history

## Credits

Based on:

- [**Ralph Wiggum as a "software engineer"** pattern by Geoffrey Huntley](https://ghuntley.com/ralph/)
- [Ralph](https://github.com/snarktank/ralph)
- [VSCode Custom Agents Docs](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
- [Claude Code Ralph Loop](https://github.com/anthropics/claude-code/blob/main/plugins/ralph-wiggum/README.md)
