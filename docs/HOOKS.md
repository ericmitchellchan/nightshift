# Hook Behavior

## How the Stop Hook Works

Claude Code supports lifecycle hooks — shell commands that run in response to agent events. Nightshift uses the **Stop** hook, which fires when an agent attempts to finish its work.

### Flow

```
Agent finishes work
  → Stop hook fires
    → verify-tests.py runs
      → Checks git for changed files
        → No watched files changed? → exit 0 (agent stops)
        → Watched files changed? → Run test command
          → Tests pass → exit 0 (agent stops)
          → Tests fail → exit 2 (agent blocked, must fix)
```

### Exit Codes

| Code | Meaning | Agent Behavior |
|------|---------|----------------|
| 0 | No relevant changes, or tests passed | Agent stops normally |
| 2 | Tests failed | Agent is blocked — receives stderr output and must fix failures before trying again |

Any other exit code is treated as a hook error and logged but does not block the agent.

## Configuration

The hook reads `.nightshift.json` from the project root:

```json
{
  "test_command": "python -m pytest tests/ -x -q --tb=short",
  "watch_extensions": [".py"],
  "test_timeout": 300
}
```

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `test_command` | string | `python -m pytest tests/ -x -q --tb=short` | Shell command to run tests |
| `watch_extensions` | string[] | `[".py"]` | File extensions that trigger test runs |
| `test_timeout` | number | `300` | Seconds before the test run is killed |

### No Config File

If `.nightshift.json` is missing, the script falls back to Python/pytest defaults and prints a warning to stderr.

## File Change Detection

The hook detects changes using two git commands:

1. `git diff --name-only HEAD` — staged and unstaged modifications
2. `git ls-files --others --exclude-standard` — untracked files

Both are filtered against `watch_extensions`. If no watched files appear in either list, tests are skipped entirely.

## Cross-Platform Notes

- On Windows, the test command runs with `shell=True` to support commands like `npm test` or `pnpm run test` that rely on shell PATH resolution.
- On Unix, the command is split into args and run directly (no shell).
- The hook itself is invoked via `python`, which must be on PATH.

## Plugin vs Standalone

**Plugin mode** (recommended): The hook is defined in `hooks/hooks.json` and uses `${CLAUDE_PLUGIN_ROOT}` to locate `verify-tests.py`. No files are copied into your project.

**Standalone mode**: `install.py` copies `verify-tests.py` into your project's `.claude/` directory and adds the hook to `.claude/settings.json`. The script path uses `$CLAUDE_PROJECT_DIR`.

## Customization

### Watching additional extensions

Add extensions to the array:
```json
{
  "watch_extensions": [".py", ".sql", ".yaml"]
}
```

### Multiple test commands

If you need to run multiple test suites, chain them:
```json
{
  "test_command": "python -m pytest tests/unit/ -x -q && python -m pytest tests/integration/ -x -q"
}
```

### Disabling temporarily

Delete or rename `.nightshift.json`. Without the config file, the hook falls back to Python defaults — if your project isn't Python, no `.py` files will be detected and the hook exits cleanly.
