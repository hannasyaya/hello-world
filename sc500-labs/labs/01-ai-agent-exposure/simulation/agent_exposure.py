#!/usr/bin/env python3
"""Offline companion for the SC-500 AI agent security lab.

Loads a simulated environment (contoso-agents.json) and reproduces the three
analyses you perform in Microsoft Defender XDR:

  inventory     - AI agent inventory with posture findings (Exercise 1)
  blast-radius  - what an attacker reaches if an agent identity is compromised (Exercise 2)
  attack-paths  - paths from entry points, through agents, to critical assets (Exercise 3)

Only the Python standard library is used.
"""
import argparse
import json
import sys
from collections import deque
from pathlib import Path

DEFAULT_MODEL = Path(__file__).with_name("contoso-agents.json")

# Edges an attacker follows after gaining control of a node. Edges that describe
# how someone reaches an agent (canChatWith, canInvoke, ...) are only used for attack paths.
PRIVILEGE_EDGES = {
    "runsAs", "usesConnection", "usesKnowledge", "canRead", "canActAs",
    "hasPermission", "hasRoleOn", "contains", "authenticatesAs",
    "memberOf", "canResetPasswordOf",
}
ENTRY_EDGES = {"canChatWith", "canInvoke", "canInjectPromptInto"}

TYPE_WEIGHT = {
    "dataStore": 5, "azureResource": 3, "knowledgeSource": 2, "credential": 4,
    "agentIdentityBlueprint": 5, "agentIdentity": 3, "managedIdentity": 3,
    "directoryRole": 4, "user": 2, "connection": 1,
}


class Environment:
    def __init__(self, data):
        self.data = data
        self.nodes = {n["id"]: n for n in data["nodes"]}
        self.agents = {a["id"]: a for a in data["agents"]}
        self.out = {}
        for e in data["edges"]:
            self.out.setdefault(e["from"], []).append(e)

    @classmethod
    def load(cls, path):
        with open(path, encoding="utf-8") as f:
            return cls(json.load(f))

    def name(self, node_id):
        return self.nodes[node_id]["name"]

    def is_critical(self, node_id):
        return bool(self.nodes[node_id].get("critical"))

    def resolve_agent(self, key):
        """Accept an agent id or a case-insensitive agent name."""
        if key in self.agents:
            return key
        for aid, a in self.agents.items():
            if a["name"].lower() == key.lower():
                return aid
        raise KeyError(f"Unknown agent: {key!r}. Try: {', '.join(self.agents)}")

    # ---- Exercise 1 -------------------------------------------------------

    def inventory(self):
        disabled = set(self.data.get("disabledUsers", []))
        rows = []
        for a in self.agents.values():
            findings = []
            if a["userAuthentication"].lower() == "none":
                findings.append("No user authentication")
            if any("maker credentials" in t for t in a["tools"]):
                findings.append("Tool runs with maker credentials")
            if a["owners"] and all(o in disabled for o in a["owners"]):
                findings.append("Orphaned (all owners disabled)")
            if a["identity"] is None:
                findings.append("No dedicated Entra agent identity")
            else:
                for e in self.out.get(a["identity"], []):
                    perm = e.get("permission", "")
                    if "application" in perm or perm in ("Owner", "Contributor"):
                        findings.append(f"High-privilege grant: {perm} on {self.name(e['to'])}")
                    elif e["label"] == "memberOf":
                        findings.append(f"Holds directory role: {self.name(e['to'])}")
            if any(self.is_critical(k) for k in a["knowledgeSources"]):
                findings.append("Knowledge source holds critical data")
            if a["lastActivity"] < "2026-06-01":
                findings.append("Inactive > 90 days")
            rows.append({**a, "findings": findings})
        return rows

    # ---- Exercise 2 -------------------------------------------------------

    def blast_radius(self, start):
        """Breadth-first walk of privilege edges from a node. Returns {node_id: (depth, via_edge)}."""
        seen = {start: (0, None)}
        queue = deque([start])
        while queue:
            cur = queue.popleft()
            for e in self.out.get(cur, []):
                if e["label"] not in PRIVILEGE_EDGES or e["to"] in seen:
                    continue
                seen[e["to"]] = (seen[cur][0] + 1, e)
                queue.append(e["to"])
        del seen[start]
        return seen

    def score(self, reached):
        total = 0
        for nid in reached:
            node = self.nodes[nid]
            w = TYPE_WEIGHT.get(node["type"], 1)
            total += w * (3 if node.get("critical") else 1)
        return total

    def blueprint_of(self, identity_id):
        for e in self.data["edges"]:
            if e["label"] == "canActAs" and e["to"] == identity_id:
                return e["from"]
        return None

    def siblings(self, blueprint_id):
        return [e["to"] for e in self.out.get(blueprint_id, []) if e["label"] == "canActAs"]

    # ---- Exercise 3 -------------------------------------------------------

    def attack_paths(self, max_hops=8):
        """All simple paths entry point -> agent -> ... -> critical asset."""
        paths = []
        entries = [n for n, v in self.nodes.items() if v["type"] == "entryPoint"]

        def dfs(node, path, edges):
            if len(edges) > max_hops:
                return
            if self.is_critical(node) and len(edges) > 1:
                paths.append((list(path), list(edges)))
            for e in self.out.get(node, []):
                allowed = ENTRY_EDGES if not edges else PRIVILEGE_EDGES
                if e["label"] not in allowed or e["to"] in path:
                    continue
                path.append(e["to"])
                edges.append(e)
                dfs(e["to"], path, edges)
                path.pop()
                edges.pop()

        for ep in entries:
            dfs(ep, [ep], [])
        paths.sort(key=lambda p: (len(p[1]), p[0]))
        return paths

    def choke_points(self, paths):
        """Non-endpoint nodes that appear on the most attack paths."""
        counts = {}
        for nodes, _ in paths:
            for nid in set(nodes[1:-1]):
                counts[nid] = counts.get(nid, 0) + 1
        return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))


def edge_text(e):
    return f"{e['label']}" + (f" [{e['permission']}]" if e.get("permission") else "")


def cmd_inventory(env, args):
    rows = env.inventory()
    if args.json:
        print(json.dumps(rows, indent=2))
        return
    print(f"AI agent inventory - {env.data['tenant']} ({len(rows)} agents)\n")
    for r in rows:
        print(f"* {r['name']}  [{r['platform']} | {r['status']} | env: {r['environment']}]")
        print(f"    owners: {', '.join(r['owners'])}   identity: {r['identity'] or '-'}")
        print(f"    auth: {r['userAuthentication']}   channels: {', '.join(r['channels'])}")
        print(f"    knowledge: {', '.join(env.name(k) for k in r['knowledgeSources'])}")
        for f in r["findings"]:
            print(f"    ! {f}")
        print()


def cmd_blast_radius(env, args):
    aid = env.resolve_agent(args.agent)
    agent = env.agents[aid]
    reached = env.blast_radius(aid)
    result = {
        "agent": agent["name"],
        "identity": agent["identity"],
        "reachable": [
            {"id": n, "name": env.name(n), "type": env.nodes[n]["type"],
             "critical": env.is_critical(n), "hops": d, "via": edge_text(e)}
            for n, (d, e) in sorted(reached.items(), key=lambda kv: (kv[1][0], kv[0]))
        ],
        "score": env.score(reached),
    }
    bp = env.blueprint_of(agent["identity"]) if agent["identity"] else None
    if bp:
        result["blueprint"] = {
            "name": env.name(bp),
            "agentIdentities": [env.name(s) for s in env.siblings(bp)],
            "blueprintBlastRadiusScore": env.score(env.blast_radius(bp)),
        }
    if args.json:
        print(json.dumps(result, indent=2))
        return
    print(f"Blast radius for '{agent['name']}' (identity: {agent['identity'] or 'none'})\n")
    for r in result["reachable"]:
        flag = "CRITICAL " if r["critical"] else ""
        print(f"  hop {r['hops']}: {flag}{r['name']} ({r['type']}) via {r['via']}")
    crit = sum(r["critical"] for r in result["reachable"])
    print(f"\n  reachable: {len(result['reachable'])}   critical: {crit}   score: {result['score']}")
    if bp:
        b = result["blueprint"]
        print(f"\n  Blueprint: {b['name']}")
        print(f"    agent identities sharing it: {', '.join(b['agentIdentities'])}")
        print(f"    blast radius if the blueprint credential leaks: score {b['blueprintBlastRadiusScore']}")


def cmd_attack_paths(env, args):
    paths = env.attack_paths(max_hops=args.max_hops)
    if args.json:
        print(json.dumps([
            {"hops": len(e), "path": [env.name(n) for n in p], "edges": [edge_text(x) for x in e]}
            for p, e in paths], indent=2))
        return
    print(f"{len(paths)} attack paths to critical assets\n")
    for i, (p, e) in enumerate(paths, 1):
        print(f"[{i}] {len(e)} hops -> {env.name(p[-1])}")
        print(f"    {env.name(p[0])}")
        for node, edge in zip(p[1:], e):
            print(f"      --{edge_text(edge)}--> {env.name(node)}")
        print()
    print("Choke points (fix these first):")
    for nid, c in env.choke_points(paths)[:5]:
        print(f"  {c:>2} paths  {env.name(nid)} ({env.nodes[nid]['type']})")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default=str(DEFAULT_MODEL), help="environment JSON file")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("inventory")
    br = sub.add_parser("blast-radius")
    br.add_argument("agent", help="agent id or name, e.g. agent-devops")
    ap = sub.add_parser("attack-paths")
    ap.add_argument("--max-hops", type=int, default=8)
    args = p.parse_args(argv)

    env = Environment.load(args.model)
    {"inventory": cmd_inventory, "blast-radius": cmd_blast_radius,
     "attack-paths": cmd_attack_paths}[args.cmd](env, args)


if __name__ == "__main__":
    sys.exit(main())
