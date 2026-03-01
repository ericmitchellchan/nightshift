# Nightshift

Test verification hooks and agent orchestration patterns for [Claude Code](https://claude.ai/claude-code).

Nightshift ensures that Claude Code agents can't mark work as complete when tests are failing. It provides a **Stop hook** that detects file changes, runs your test suite, and blocks the agent (exit code 2) if anything fails.

## Quick Start

### As a Claude Code Plugin

```bash
# Install the plugin (registers hooks automatically)
claude plugin add ericmitchellchan/nightshift

# In your project, create a config file
claude /nightshift:init
```

### Standalone (no plugin system)

```bash
# Clone and run the installer
git clone https://github.com/ericmitchellchan/nightshift.git
cd nightshift
python install.py /path/to/your/project
```

## How It Works

1. An agent finishes its work and attempts to stop.
2. The **Stop hook** fires and runs `scripts/verify-tests.py`.
3. The script reads `.nightshift.json` from your project root to find:
   - Which file extensions to watch (e.g., `.py`, `.ts`)
   - What test command to run (e.g., `pytest`, `npm test`)
   - Timeout for the test run
4. If no watched files were modified, the hook exits cleanly (agent stops).
5. If watched files changed, it runs your test suite:
   - **Tests pass** → exit 0 → agent stops normally.
   - **Tests fail** → exit 2 → agent is blocked and must fix the failures.

## Configuration

Create `.nightshift.json` in your project root:

```json
{
  "test_command": "python -m pytest tests/ -x -q --tb=short",
  "watch_extensions": [".py"],
  "test_timeout": 300
}
```

### Examples

**Node.js / TypeScript (Jest)**
```json
{
  "test_command": "npm test",
  "watch_extensions": [".ts", ".tsx", ".js", ".jsx"],
  "test_timeout": 120
}
```

**Rust**
```json
{
  "test_command": "cargo test",
  "watch_extensions": [".rs"],
  "test_timeout": 600
}
```

If no `.nightshift.json` is found, the script falls back to Python/pytest defaults.

## What's Included

| Path | Purpose |
|------|---------|
| `scripts/verify-tests.py` | The Stop hook script |
| `hooks/hooks.json` | Hook definition (auto-registered by plugin system) |
| `skills/init/SKILL.md` | `/nightshift:init` skill for project setup |
| `templates/` | Config and CLAUDE.md templates |
| `docs/` | Guides for hooks, CLAUDE.md authoring, Jira orchestration |
| `install.py` | Standalone installer for manual setup |

## Documentation

- [Hook Behavior](docs/HOOKS.md) — How the Stop hook works, exit codes, customization
- [CLAUDE.md Guide](docs/CLAUDE-MD-GUIDE.md) — Writing effective CLAUDE.md files for agent-driven repos
- [Jira Orchestration](docs/JIRA-ORCHESTRATION.md) — Epic → Task decomposition pattern
- [Anti-Patterns](docs/ANTI-PATTERNS.md) — What not to do

## License

MIT
