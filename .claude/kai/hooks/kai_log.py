#!/usr/bin/env python3
"""Kai audit trail: PostToolUse hook for the Agent (sub-agent) tool.

Appends one JSON line per sub-agent run to .claude/kai/logs/activity.jsonl, so you can see
which specialist did what and when. The log directory is git-ignored.
"""
import datetime
import json
import os
import sys


def main():
    try:
        data = json.load(sys.stdin)
        tool_input = data.get("tool_input") or {}
        record = {
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "session": data.get("session_id"),
            "tool": data.get("tool_name"),
            "agent": tool_input.get("subagent_type", "general-purpose"),
            "task": tool_input.get("description"),
        }
        base = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
        log_dir = os.path.join(base, ".claude", "kai", "logs")
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "activity.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass  # logging must never interrupt work
    return 0


if __name__ == "__main__":
    sys.exit(main())
