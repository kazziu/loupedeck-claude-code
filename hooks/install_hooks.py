"""Adds (or removes) the mascot hooks in ~/.claude/settings.json. Idempotent, with a backup.

Usage:  python install_hooks.py            # install / update
        python install_hooks.py --remove   # remove only our entries
The hooks are async and run without a shell (command + args), so they do not slow Claude Code down.
Interpreter: the same python that runs this installer (sys.executable).
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "mascot_hook.py")
MARK = "mascot_hook.py"
EVENTS = ["SessionStart", "SessionEnd", "UserPromptSubmit", "PreToolUse", "PostToolUse", "PostToolUseFailure",
          "PermissionRequest", "PermissionDenied", "Notification", "Stop", "StopFailure", "SubagentStart",
          "SubagentStop", "PreCompact", "PostCompact"]


def ours(entry):
    return any(MARK in " ".join([h.get("command", "")] + list(h.get("args", []))) for h in entry.get("hooks", []))


def main():
    remove = "--remove" in sys.argv
    path = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")
    settings = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            settings = json.load(f)
        shutil.copy(path, f"{path}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
    hooks = settings.setdefault("hooks", {})
    for event in list(hooks):
        hooks[event] = [e for e in hooks[event] if not ours(e)]
        if not hooks[event]:
            del hooks[event]
    if not remove:
        for event in EVENTS:
            hooks.setdefault(event, []).append({"hooks": [{
                "type": "command", "command": sys.executable, "args": [HOOK, event],
                "async": True, "timeout": 10}]})
    if not hooks:
        settings.pop("hooks")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(("removed" if remove else f"installed {len(EVENTS)} hooks") + f" -> {path}")


if __name__ == "__main__":
    main()
