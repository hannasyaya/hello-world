#!/usr/bin/env python3
"""Kai session briefing: SessionStart hook.

Reads the newest kai-reports/*/risk-register.csv and prints open risks by rating plus any
overdue items. Claude Code adds SessionStart stdout to the session context, so Kai starts
every session knowing what is outstanding.
"""
import csv
import datetime
import glob
import os
import sys


def main():
    base = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    registers = sorted(glob.glob(os.path.join(base, "kai-reports", "*", "risk-register.csv")))
    print("Kai (mini) is online: GRC assistant. Skills: /assess, /policy, /interview.")
    if not registers:
        print("No risk register yet. Run /assess <target> to create one.")
        return 0
    latest = registers[-1]
    today = datetime.date.today().isoformat()
    try:
        with open(latest, newline="", encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if (r.get("status") or "").lower() != "closed"]
    except (OSError, csv.Error):
        return 0
    counts = {}
    for r in rows:
        counts[r.get("rating", "?")] = counts.get(r.get("rating", "?"), 0) + 1
    summary = ", ".join(f"{k}: {counts[k]}" for k in ("High", "Medium", "Low") if k in counts)
    print(f"Latest register: {os.path.relpath(latest, base)}. Open risks: {len(rows)} ({summary}).")
    overdue = [r for r in rows if r.get("due_date") and r["due_date"] < today]
    for r in overdue[:5]:
        print(f"  OVERDUE {r.get('risk_id')} [{r.get('rating')}] {r.get('title')} "
              f"(owner: {r.get('owner')}, due {r.get('due_date')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
