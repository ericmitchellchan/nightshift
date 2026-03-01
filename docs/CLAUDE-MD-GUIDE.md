# Writing Effective CLAUDE.md Files

A `CLAUDE.md` file tells Claude Code how to work in your repo. It's the single most impactful thing you can do to improve agent output quality.

## Why It Matters

Without a CLAUDE.md, agents guess at conventions, run wrong test commands, create files in wrong directories, and produce code that doesn't match your style. With one, they follow your patterns from the first line of code.

## Structure

A good CLAUDE.md covers these sections (in order):

### 1. Project Overview
One or two sentences. What does this project do?

```markdown
## Project Overview
Shot Clock is a sports analytics service that collects NBA game data and generates betting insights.
```

### 2. Tech Stack
Language, framework, key dependencies. Agents use this to pick the right patterns.

```markdown
## Tech Stack
- Python 3.11, FastAPI, SQLAlchemy 2.0
- PostgreSQL 15 (RDS)
- UV for dependency management
```

### 3. Repository Structure
Key directories. Don't list every file — just the important ones.

```markdown
## Repository Structure
- `src/` — Application code
  - `src/models/` — SQLAlchemy models
  - `src/services/` — Business logic
  - `src/api/` — FastAPI routes
- `tests/` — Pytest test suite
- `migrations/` — Alembic migrations
```

### 4. Development Setup
How to install and run locally. Agents need this to verify their work.

```markdown
## Development Setup
uv sync
cp .env.example .env  # fill in DATABASE_URL
uv run python -m src.main
```

### 5. Testing
The exact command to run tests. Must match `.nightshift.json`.

```markdown
## Testing
python -m pytest tests/ -x -q --tb=short
```

### 6. Code Conventions
Naming, formatting, import ordering — whatever you care about.

```markdown
## Code Conventions
- snake_case for functions and variables
- PascalCase for classes
- Group imports: stdlib → third-party → local
- No wildcard imports
```

### 7. Agent Instructions
Rules for automated agents. Be explicit.

```markdown
## Agent Instructions
- Read existing code before modifying it.
- Run tests before declaring work complete.
- Do not add features beyond what was asked.
- If tests fail, fix them.
```

## Tips

**Be specific, not aspirational.** Write what the project *actually* does, not what you wish it did.

**Keep it under 100 lines.** Agents load this into context on every session. Long files waste tokens. Link to external docs for details.

**Update it when conventions change.** A stale CLAUDE.md is worse than none — agents will follow outdated instructions.

**Include the test command.** This is the most important line in the file. Agents need to verify their work.

**Don't duplicate global rules.** If you use a global CLAUDE.md (in `~/.claude/CLAUDE.md`), don't repeat those rules in the project CLAUDE.md. Project rules take precedence on conflict.
