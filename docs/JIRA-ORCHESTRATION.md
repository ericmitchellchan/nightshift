# Jira Orchestration Pattern

How to decompose a feature into agent-executable tasks using Jira as the control plane.

## Overview

The pattern uses Jira's hierarchy to coordinate multiple Claude Code agents working in parallel on a single codebase:

```
Epic (the container)
  ├── Task 1 (agent A — files X, Y)
  ├── Task 2 (agent B — files Z, W)
  ├── Task 3 (agent C — files V)  ← blocked by Task 1
  └── Task 4 (supervisor)         ← blocked by Tasks 1, 2, 3
```

Each Task is one agent, one deliverable, with explicit file ownership so agents never conflict.

## Ticket Types

| Type | Who Creates | Purpose |
|------|-------------|---------|
| Epic | Human or orchestrator | Container for the feature. Decomposes into Tasks. |
| Task | Orchestrator or human | Unit of work. One agent, one deliverable. |
| Bug | Human or agent | Something broken found during work. |
| Request | Agent | Out-of-scope observation. "I noticed X but it's not my job." |

## Task Anatomy

Every Task description must include:

1. **Objective** — 1-2 sentences. What does this Task accomplish?
2. **Files to modify** — Explicit list. No two Tasks share writable files.
3. **Files to read** — Read-only references for context. Multiple Tasks can read the same files.
4. **Acceptance criteria** — Concrete, testable conditions.
5. **Verification command** — The exact test command to run.

### Example

```markdown
## Objective
Add the game scheduler service that fetches today's NBA schedule from the ESPN API.

## Files to modify
- src/services/scheduler.py (create)
- tests/test_scheduler.py (create)

## Files to read
- src/models/game.py (Game model schema)
- src/config.py (API keys, base URLs)

## Acceptance criteria
- [ ] scheduler.fetch_today_games() returns list of Game objects
- [ ] Handles ESPN API errors gracefully (retry with backoff)
- [ ] Tests cover: success, API error, empty schedule, malformed response

## Verification
python -m pytest tests/test_scheduler.py -x -q --tb=short
```

## Waves

Tasks are organized into waves using Jira's "Blocks" link:

- **Wave 1**: Tasks with no blockers. Can run in parallel.
- **Wave 2**: Tasks blocked by Wave 1. Start when their blockers resolve.
- **Wave N**: Supervisor/integration task. Blocked by all prior waves.

### Setting up dependencies

Use Jira's issue linking:
- Task 4 is **blocked by** Tasks 1, 2, 3
- Tasks 1, 2, 3 **block** Task 4

Agents check their blockers before starting. If a blocker is unresolved, the agent waits.

## File Ownership Rules

The most important rule: **no two Tasks share writable files.**

- If two Tasks need to modify the same file, they must be serialized (one blocks the other).
- Read-only references are fine — multiple Tasks can read `config.py` without conflict.
- Be explicit: say "create from scratch" or "modify existing file" — never "audit if exists, otherwise build."

## Supervisor Task

The final Task in an Epic is usually a supervisor that:
1. Runs the full test suite (not just individual test files)
2. Verifies integration between components created by other Tasks
3. Updates documentation or config files that reference the new feature
4. Comments on the Epic with a summary of all changes

## Agent Behavior

### When an agent receives a Task:
1. Read the full description (objective, files, criteria).
2. Check blockers — if any are unresolved, stop and report.
3. Read all context files before writing any code.
4. Implement the changes within the specified files only.
5. Run the verification command.
6. Comment on the Jira ticket with: files changed, test results, any issues found.
7. Transition the ticket to Done.

### When an agent finds out-of-scope work:
- Create a **Request** ticket (not a Task).
- Link it to the current Task.
- Do NOT act on it — stay focused on the assigned Task.

## Lessons Learned

From the Shot Clock pilot (SC-1 Epic, 5 Tasks):

**What worked:**
- File ownership prevented merge conflicts across 4 parallel agents.
- Wave-based dependencies (SC-5 blocked by SC-2/3/4) provided clean sequencing.
- Agents discovering existing work auto-resolved instead of creating conflicts.
- Jira comments with change lists + test results created a full audit trail.

**What needs improvement:**
- Verification was self-reported. Nightshift's Stop hook solves this.
- Exploration phase before decomposition helps — know what files exist before writing tickets.
- Standardize the test command (different agents discovered different test counts due to working directory differences).
- Fix or skip known test failures so agents have a clean baseline.
