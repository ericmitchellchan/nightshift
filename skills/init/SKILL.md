# /nightshift:init

Scaffold Nightshift configuration for the current project.

## Instructions

When this skill is invoked:

1. **Detect the project type** by inspecting files in `$CLAUDE_PROJECT_DIR`:
   - `requirements.txt`, `pyproject.toml`, `setup.py` → Python
   - `package.json` → Node.js (check for `pnpm-lock.yaml` vs `package-lock.json`)
   - `Cargo.toml` → Rust
   - If ambiguous, ask the user.

2. **Create `.nightshift.json`** in the project root with appropriate defaults:

   **Python:**
   ```json
   {
     "test_command": "python -m pytest tests/ -x -q --tb=short",
     "watch_extensions": [".py"],
     "test_timeout": 300
   }
   ```

   **Node.js (npm):**
   ```json
   {
     "test_command": "npm test",
     "watch_extensions": [".ts", ".tsx", ".js", ".jsx"],
     "test_timeout": 120
   }
   ```

   **Node.js (pnpm):**
   ```json
   {
     "test_command": "pnpm run test",
     "watch_extensions": [".ts", ".tsx", ".js", ".jsx"],
     "test_timeout": 120
   }
   ```

   **Rust:**
   ```json
   {
     "test_command": "cargo test",
     "watch_extensions": [".rs"],
     "test_timeout": 600
   }
   ```

3. **Check for CLAUDE.md** in the project root:
   - If it exists, do not modify it. Print: "CLAUDE.md already exists — skipping template."
   - If it does not exist, copy `${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.md.template` and fill in `{{PROJECT_NAME}}` and `{{TEST_COMMAND}}` with the detected values.

4. **Add `.nightshift.json` to .gitignore** if it's not already listed (the config is project-specific and may contain local paths).
   - Actually, `.nightshift.json` should be committed so all agents share the same config. Do NOT add to .gitignore.

5. **Print summary:**
   ```
   Nightshift initialized:
     - Created .nightshift.json (test_command: <command>)
     - Watch extensions: <extensions>
     - Test timeout: <seconds>s
   ```

## User-Invocable

This skill is triggered by the user typing `/nightshift:init`.
