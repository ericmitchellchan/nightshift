"""
Nightshift Stop hook — runs tests only if watched files were modified.

Reads .nightshift.json from the project root for configuration:
  {
    "test_command": "python -m pytest tests/ -x -q --tb=short",
    "watch_extensions": [".py"],
    "test_timeout": 300
  }

Exit codes:
  0 — No watched files changed, or tests passed. Agent may stop.
  2 — Tests failed. Agent must fix before completing.
"""
import json
import os
import platform
import subprocess
import sys


# Defaults if no .nightshift.json found
DEFAULTS = {
    "test_command": "python -m pytest tests/ -x -q --tb=short",
    "watch_extensions": [".py"],
    "test_timeout": 300,
}


def load_config(project_dir):
    """Load .nightshift.json from project root, falling back to defaults."""
    config_path = os.path.join(project_dir, ".nightshift.json")
    config = dict(DEFAULTS)
    if os.path.isfile(config_path):
        try:
            with open(config_path, "r") as f:
                user_config = json.load(f)
            config.update(user_config)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[nightshift] Warning: could not parse .nightshift.json: {e}", file=sys.stderr)
    else:
        print("[nightshift] No .nightshift.json found, using defaults (Python/pytest).", file=sys.stderr)
    return config


def get_changed_files(project_dir):
    """Return list of changed/untracked files relative to project root."""
    files = []
    try:
        # Staged + unstaged changes
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True, text=True, timeout=10, cwd=project_dir
        )
        if result.stdout.strip():
            files.extend(result.stdout.strip().split("\n"))

        # Untracked files
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True, text=True, timeout=10, cwd=project_dir
        )
        if untracked.stdout.strip():
            files.extend(untracked.stdout.strip().split("\n"))
    except Exception:
        # Not a git repo or git not available — skip
        return []

    return [f for f in files if f]


def has_watched_changes(changed_files, extensions):
    """Check if any changed files match the watched extensions."""
    return [f for f in changed_files if any(f.endswith(ext) for ext in extensions)]


def run_tests(config, project_dir):
    """Run the configured test command. Returns (success, stdout, stderr)."""
    cmd = config["test_command"]
    timeout = config.get("test_timeout", 300)

    # Use shell=True on Windows for commands like 'npm test' or 'pnpm run test'
    use_shell = platform.system() == "Windows"

    try:
        result = subprocess.run(
            cmd if use_shell else cmd.split(),
            shell=use_shell,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=project_dir,
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"[nightshift] Test command timed out after {timeout}s."
    except FileNotFoundError:
        return False, "", f"[nightshift] Test command not found: {cmd}"


def main():
    project_dir = os.environ.get(
        "CLAUDE_PROJECT_DIR",
        os.getcwd()
    )

    config = load_config(project_dir)
    extensions = config.get("watch_extensions", DEFAULTS["watch_extensions"])

    changed_files = get_changed_files(project_dir)
    watched = has_watched_changes(changed_files, extensions)

    if not watched:
        sys.exit(0)

    # Report what triggered the test run
    ext_str = ", ".join(extensions)
    print(f"[nightshift] {len(watched)} file(s) modified ({ext_str}), running tests...", file=sys.stderr)
    for f in watched[:5]:
        print(f"  - {f}", file=sys.stderr)
    if len(watched) > 5:
        print(f"  ... and {len(watched) - 5} more", file=sys.stderr)

    success, stdout, stderr = run_tests(config, project_dir)

    if stdout:
        print(stdout, file=sys.stderr)
    if stderr:
        print(stderr, file=sys.stderr)

    if not success:
        print("\n[nightshift] TESTS FAILED — agent must fix before completing.", file=sys.stderr)
        sys.exit(2)
    else:
        print("[nightshift] Tests passed.", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
