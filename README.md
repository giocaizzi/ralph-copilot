# Copilot Ralph Loop

A Copilot implementation of the Ralph Wiggum autonomous agent loop, using custom agents with automatic handoffs.

<p align="center"><img src="assets/ralph-copilot.png" height="200" alt="Ralph Copilot"></p>

Based off only four `agent.md` markdown files, this pattern enables an **autonomous coding loop** with **fresh context every iteration**, using the filesystem as memory and git for version control.

## What is Ralph Loop?

**Ralph loop = Fresh context + Filesystem memory & Git versioning**

An autonomous coding pattern where:

0. A human provides requirements to a Planner agent, which creates a `PRD.md` and `PROGRESS.md`
1. Agent picks a task from `PRD.md`
2. Executes it with fresh context
3. `git` commits and updates `PROGRESS.md`
4. Loops until all tasks complete

### Execution Flow

```mermaid
sequenceDiagram
    participant H as 👤 Human
    participant P as Planner
    participant C as Coordinator
    participant E as Executor
    participant R as Reviewer
    participant FS as 📁 Filesystem

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
- 📊 **Progress file** - Fresh context every iteration via `PROGRESS.md` and `git`
- 🌐 **Language agnostic** - Works with any programming language/stack
- ⚛️ **Atomic tasks** - One task per iteration, committed immediately
- 🔄 **Context reset** - Avoids context pollution, uses filesystem as memory
- 🔍 **Built-in review** - Reviewer subagent verifies every task before moving on

## Setup

### Installation

1. Clone repository and copy agent files to your project:

```bash
git clone git@github.com:giocaizzi/ralph-copilot.git
cp ralph-copilot/agents/*.agent.md <your_project>/.github/agents/
```

2. Restart VSCode or reload window

3. Verify agents are available:
   - Open Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
   - Type "Select Agent"
   - Should see: `RalphPlanner`, `RalphCoordinator`

> **Tip — use Ralph globally across all your projects**
>
> Instead of copying agent files per project, point VS Code to your local clone of this repo once via
> [![VS Code Setting](https://img.shields.io/badge/VS%20Code-chat.agentFilesLocations-007ACC?style=flat&logo=visualstudiocode&logoColor=white)](vscode://settings/chat.agentFilesLocations)
> and the agents will be available everywhere.
>
> ```jsonc
> // settings.json
> "chat.agentFilesLocations": {
>     "/your/path/to/ralph-copilot": true
> }
> ```

## Usage

### Quick Start

1. **Create PRD** with Planner agent:

   ```
   Open VSCode Chat
   Select: Planner agent
   Prompt: "Create a PRD for [your feature]"
   ```

2. **Review PRD.md** - Edit as needed

3. **Start Loop** with Coordinator:

   ```
   Select: Coordinator agent
   Click: "Start Ralph Loop" handoff button
   ```

4. **Let it run** - Agents will:
   - Pick tasks from PRD.md
   - Execute them
   - Update PROGRESS.md
   - Commit changes
   - Repeat until done

5. **Monitor progress** in PROGRESS.md and git history

## Credits

Based on:

- **Ralph Wiggum** pattern by Geoffrey Huntley

## Links

- [VSCode Custom Agents Docs](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
- [Original Ralph Pattern](https://github.com/snarktank/ralph)
- [Claude Code Ralph Loop](https://github.com/anthropics/claude-code/blob/main/plugins/ralph-wiggum/README.md)
