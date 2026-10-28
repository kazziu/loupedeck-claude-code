"""Claude Code hook -> stan sesji dla maskotki na Loupedecku.

Wywolywany (async, bez powloki) na kazde zdarzenie Claude Code:
    <python> mascot_hook.py <EventName>   + JSON zdarzenia na stdin
Zapisuje ~/.config/loupedeck-cc/sessions/<session_id>.json:
    {"event", "state", "tool", "cwd", "ts", "detail"}
Wtyczka ClaudeMascot sklada stany wszystkich sesji (priorytet: attention > oops > compact > working > done > hello).
Skrypt nie moze nigdy przeszkodzic Claude Code: zadnych wyjatkow, zawsze exit 0, tylko biblioteka standardowa.
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
