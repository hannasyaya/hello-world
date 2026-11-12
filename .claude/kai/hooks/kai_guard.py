#!/usr/bin/env python3
"""Kai guardrail: PreToolUse hook for Bash.

- DENY a scanning tool (nmap, nuclei, sqlmap, ...) when any of its targets is not listed
  in .claude/kai/scope.txt (the rules of engagement).
- ASK before destructive cloud/IaC/file commands (az ... delete, terraform destroy, rm -rf, ...).

This is a guardrail against mistakes, not a security boundary: a determined user or model can
get around simple command parsing. It never blocks on its own errors (fail-open).
"""
import json
import os
import re
import shlex
import sys

SCANNERS = {
    "nmap", "masscan", "rustscan", "zmap", "nuclei", "nikto", "sqlmap", "hydra",
    "ffuf", "gobuster", "dirb", "feroxbuster", "wpscan", "amass", "subfinder",
}
DESTRUCTIVE = [
    (r"\baz\b[^;&|]*\s(delete|purge)\b", "Azure CLI delete/purge"),
    (r"\bRemove-(Az|Mg|Entra)\w*", "PowerShell Remove-Az/Mg/Entra cmdlet"),
    (r"\bterraform\s+(destroy|apply\b[^;&|]*-destroy)", "terraform destroy"),
    (r"\bkubectl\s+delete\b", "kubectl delete"),
    (r"\bcleanup\.sh\b", "lab clean-up script (deletes cloud resources)"),
    (r"\brm\s+-(?=[a-zA-Z]*r)(?=[a-zA-Z]*f)[a-zA-Z]+\b", "recursive force delete (rm -rf)"),
    (r"\bgit\s+push\b[^;&|]*(--force\b|-f\b)", "git force push"),
]
SEPARATORS = {";", "&&", "||", "|", "&", "(", ")"}
FILE_EXT = re.compile(r"\.(txt|xml|json|ya?ml|csv|html?|log|gnmap|nmap|md)$", re.I)


def project_dir():
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def load_scope():
    path = os.path.join(project_dir(), ".claude", "kai", "scope.txt")
    try:
        with open(path, encoding="utf-8") as f:
            return [l.strip().lower() for l in f if l.strip() and not l.lstrip().startswith("#")]
    except OSError:
        return []


def looks_like_target(tok):
    if tok.startswith("-") or FILE_EXT.search(tok) or os.path.exists(tok):
        return False
    if tok.lower() == "localhost" or "://" in tok:
        return True
    if re.fullmatch(r"[\d,\-]+", tok):  # port lists such as 80,443 or 1-1024
        return False
    return bool(re.search(r"[a-z0-9]\.[a-z0-9]", tok, re.I)) or "/" in tok


def scan_targets(command):
    """Yield (scanner, target) for every scanner invocation in the command."""
    try:
        lex = shlex.shlex(command, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        tokens = list(lex)
    except ValueError:
        tokens = command.split()
    scanner = None
    for tok in tokens:
        if tok in SEPARATORS:
            scanner = None
        elif os.path.basename(tok) in SCANNERS:
            scanner = os.path.basename(tok)
        elif scanner and looks_like_target(tok):
            yield scanner, tok


def decide(command):
    scope = load_scope()
    out_of_scope = [(s, t) for s, t in scan_targets(command)
                    if not any(entry in t.lower() for entry in scope)]
    if out_of_scope:
        listed = ", ".join(f"{s} -> {t}" for s, t in out_of_scope)
        return "deny", (f"Kai guard: out-of-scope target ({listed}). Only targets in "
                        ".claude/kai/scope.txt may be scanned. Add a target there only with "
                        "written authorization.")
    for pattern, label in DESTRUCTIVE:
        if re.search(pattern, command):
            return "ask", (f"Kai guard: '{label}' changes or destroys resources. GRC assessment "
                           "work is read-only; confirm this is intended.")
    return None, None


def main():
    try:
        data = json.load(sys.stdin)
        command = (data.get("tool_input") or {}).get("command", "")
        decision, reason = decide(command)
    except Exception:  # fail open: a broken guard must not break the session
        return 0
    if decision:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
