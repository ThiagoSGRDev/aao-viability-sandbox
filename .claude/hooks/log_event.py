#!/usr/bin/env python3
"""Sanitized hook logger (viability test). Records ONLY an allowlist of fields:
timestamp, event name, agent_type, tool_name and the payload KEY NAMES (never values).
Never writes prompts, paths, file contents or session ids. Does not push anything."""
import json, os, sys, time

ev = sys.argv[1] if len(sys.argv) > 1 else "unknown"
try:
    p = json.load(sys.stdin)
    if not isinstance(p, dict):
        p = {}
except Exception:
    p = {}

root = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
d = os.path.join(root, "status")
os.makedirs(d, exist_ok=True)
now = int(time.time())
agent = p.get("agent_type") if isinstance(p.get("agent_type"), str) else "coordinator"
tool = p.get("tool_name") if isinstance(p.get("tool_name"), str) else None

rec = {"ts": now, "event": ev, "agent": agent, "tool": tool, "payload_keys": sorted(p.keys())}
with open(os.path.join(d, "events.jsonl"), "a") as f:
    f.write(json.dumps(rec) + "\n")

STATE = {"SessionStart": "idle", "SubagentStart": "working", "PreToolUse": "working",
         "SubagentStop": "completed", "Notification": "blocked", "Stop": "idle"}
sp = os.path.join(d, "status.json")
try:
    with open(sp) as f:
        st = json.load(f)
except Exception:
    st = {"source": "hook", "agents": {}}
st["generated_at"] = now
a = st["agents"].setdefault(agent, {})
a["state"] = STATE.get(ev, "unknown")
a["updated_at"] = now
a["last_event"] = ev
with open(sp, "w") as f:
    json.dump(st, f, indent=2)
