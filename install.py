"""
Nightshift standalone installer.

Usage:
    python install.py /path/to/your/project

Copies the Stop hook into the project's .claude/settings.json and creates
a default .nightshift.json if one doesn't exist.

Use this when the Claude Code plugin system isn't available.
"""
import json
import os
import shutil
import sys


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VERIFY_SCRIPT = os.path.join(SCRIPT_DIR, "scripts", "verify-tests.py")


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def install_hook(project_dir):
    """Copy verify-tests.py into .claude/ and configure settings.json."""
    claude_dir = os.path.join(project_dir, ".claude")
    ensure_dir(claude_dir)

    # Copy verify-tests.py
    dest_script = os.path.join(claude_dir, "verify-tests.py")
    shutil.copy2(VERIFY_SCRIPT, dest_script)
    print(f"  Copied verify-tests.py → {dest_script}")

    # Update settings.json
    settings_path = os.path.join(claude_dir, "settings.json")
    settings = {}
    if os.path.isfile(settings_path):
        with open(settings_path, "r") as f:
            settings = json.load(f)

    hook_command = 'python "$CLAUDE_PROJECT_DIR/.claude/verify-tests.py"'

    # Check if hook already exists
    stop_hooks = settings.get("hooks", {}).get("Stop", [])
    for group in stop_hooks:
        for hook in group.get("hooks", []):
            if hook.get("command", "") == hook_command:
                print("  Stop hook already configured — skipping.")
                return

    # Add the hook
    if "hooks" not in settings:
        settings["hooks"] = {}
    if "Stop" not in settings["hooks"]:
        settings["hooks"]["Stop"] = []

    settings["hooks"]["Stop"].append({
        "hooks": [
            {
                "type": "command",
                "command": hook_command,
                "timeout": 300,
            }
        ]
    })

    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
    print(f"  Updated {settings_path}")


def create_config(project_dir):
    """Create .nightshift.json with defaults if it doesn't exist."""
    config_path = os.path.join(project_dir, ".nightshift.json")
    if os.path.isfile(config_path):
        print(f"  .nightshift.json already exists — skipping.")
        return

    # Detect project type
    config = {
        "test_command": "python -m pytest tests/ -x -q --tb=short",
        "watch_extensions": [".py"],
        "test_timeout": 300,
    }

    if os.path.isfile(os.path.join(project_dir, "Cargo.toml")):
        config = {
            "test_command": "cargo test",
            "watch_extensions": [".rs"],
            "test_timeout": 600,
        }
    elif os.path.isfile(os.path.join(project_dir, "package.json")):
        pm = "pnpm run test" if os.path.isfile(os.path.join(project_dir, "pnpm-lock.yaml")) else "npm test"
        config = {
            "test_command": pm,
            "watch_extensions": [".ts", ".tsx", ".js", ".jsx"],
            "test_timeout": 120,
        }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")
    print(f"  Created {config_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python install.py /path/to/your/project")
        sys.exit(1)

    project_dir = os.path.abspath(sys.argv[1])
    if not os.path.isdir(project_dir):
        print(f"Error: {project_dir} is not a directory.")
        sys.exit(1)

    print(f"Installing Nightshift in {project_dir}...")
    install_hook(project_dir)
    create_config(project_dir)
    print("Done.")


if __name__ == "__main__":
    main()
