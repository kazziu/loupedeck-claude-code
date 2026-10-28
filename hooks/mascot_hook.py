"""Claude Code hook -> session state for the Loupedeck mascot.

Runs (async, without a shell) on every Claude Code event:
    <python> mascot_hook.py <EventName>   + the event JSON on stdin
Writes ~/.config/loupedeck-cc/sessions/<session_id>.json:
    {"event", "state", "tool", "cwd", "ts", "detail"}
The ClaudeMascot plugin combines all sessions (priority: attention > oops > compact > done > hello > working).
The script must never get in Claude Code's way: no exceptions, always exit 0, standard library only.
"""
import json
import os
import sys
import time

STATE_BY_EVENT = {
    "SessionStart": "hello",
    "UserPromptSubmit": "working",
    "UserPromptExpansion": "working",
    "PreToolUse": "working",
    "PostToolUse": "working",
    "PostToolBatch": "working",
    "SubagentStart": "working",
    "SubagentStop": "working",
    "PostCompact": "working",
    "PreModelSwitch": "working",
    "PostModelSwitch": "working",
    "TaskCreated": "working",
    "TaskCompleted": "working",
    "PostToolUseFailure": "oops",
    "PermissionDenied": "oops",
    "StopFailure": "oops",
    "PermissionRequest": "attention",
    "Elicitation": "attention",
    "Notification": "attention",
    "PreCompact": "compact",
    "Stop": "done",
    "TeammateIdle": "done",
    "SessionEnd": "gone",
}


def main():
    event = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except Exception:
        data = {}
    event = data.get("hook_event_name") or event
    state = STATE_BY_EVENT.get(event)
    if not state:
        return
    sid = "".join(c for c in str(data.get("session_id") or "unknown") if c.isalnum() or c in "-_")[:64]
    base = os.path.join(os.path.expanduser("~"), ".config", "loupedeck-cc", "sessions")
    os.makedirs(base, exist_ok=True)
    path = os.path.join(base, sid + ".json")
    if state == "gone":
        try:
            os.remove(path)
        except OSError:
            pass
        return
    if event == "Notification" and data.get("notification_type") not in (None, "permission_prompt", "idle_prompt",
                                                                         "elicitation_dialog"):
        state = "working"
    record = {
        "event": event,
        "state": state,
        "tool": data.get("tool_name"),
        "cwd": data.get("cwd"),
        "detail": data.get("notification_type") or data.get("trigger") or data.get("source"),
        "ts": time.time(),
    }
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(record, f)
    os.replace(tmp, path)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
