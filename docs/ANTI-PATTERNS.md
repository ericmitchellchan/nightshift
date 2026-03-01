# Anti-Patterns

Things that go wrong with agent orchestration, and how to avoid them.

## 1. Self-Reported Verification

**The problem:** An agent runs tests, reports "all tests pass," and marks the ticket Done. But the tests didn't actually all pass — maybe the agent ran a subset, or summarized "mostly passing" as "passing."

**The fix:** Use a Stop hook (Nightshift) that runs tests independently. The agent can't bypass it. If tests fail, exit code 2 blocks completion.

## 2. Shared Writable Files

**The problem:** Two Tasks both modify `config.py`. Agent A writes its version, Agent B writes its version. One overwrites the other.

**The fix:** No two Tasks share writable files. If both need to change `config.py`, serialize them — one blocks the other.

## 3. Ambiguous File Intent

**The problem:** Task says "update the migration file if it exists, otherwise create one." Agent has to guess whether the file exists, and the guess is sometimes wrong.

**The fix:** Be explicit. "Create `migrations/003_add_schedule.py` from scratch" or "Modify existing `migrations/002_add_games.py` to add the `status` column." Run an exploration phase before writing tickets.

## 4. Missing Context Files

**The problem:** Task says "add a new endpoint" but doesn't mention the existing router structure. Agent creates a new router instead of extending the existing one.

**The fix:** Always include "Files to read" in the Task description. These are read-only references that ground the agent in existing patterns.

## 5. Over-Decomposition

**The problem:** A 3-file feature gets split into 6 Tasks with complex dependency chains. The coordination overhead exceeds the parallelism benefit.

**The fix:** Use agent teams only when work spans 3+ files across clean boundaries. Single-file changes, bug fixes, and config edits don't need orchestration.

## 6. Broad Test Commands

**The problem:** Task says "run tests" but the test suite takes 10 minutes and covers unrelated code. Agents get blocked by pre-existing failures in unrelated tests.

**The fix:** Specify the exact test command in the Task description: `python -m pytest tests/test_scheduler.py -x -q`. Fix or skip known failures before starting the Epic so agents have a clean baseline.

## 7. Skipping the Stop Hook

**The problem:** Agent encounters test failures and tries to bypass the hook (e.g., renaming the config file, using `--no-verify`, or just declaring "tests are environment-specific").

**The fix:** The Stop hook runs independently of the agent's actions within the session. Exit code 2 is non-negotiable. Agents are instructed in CLAUDE.md: "If tests fail, fix them — do not try to bypass the Stop hook."

## 8. Mixing Orchestration Concerns

**The problem:** The test verification hook also tries to handle git account switching, Jira routing, and knowledge layer boundaries. It becomes fragile and hard to debug.

**The fix:** Nightshift handles one thing: test verification. Project routing, git accounts, Jira instances, and knowledge layers stay in the global CLAUDE.md where they belong.

## 9. No Supervisor Task

**The problem:** All agents finish their individual Tasks and the Epic is marked Done. But no one ran the full test suite or checked that the components integrate correctly.

**The fix:** Always include a final supervisor Task that is blocked by all other Tasks. It runs the full test suite, verifies integration, and comments on the Epic with a summary.

## 10. Stale CLAUDE.md

**The problem:** The project's conventions changed (new test framework, different directory structure) but CLAUDE.md still reflects the old setup. Agents follow outdated instructions.

**The fix:** Update CLAUDE.md when conventions change. Keep it under 100 lines. If it doesn't match reality, agents will produce code that doesn't match reality either.
