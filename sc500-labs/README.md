# SC-500 Labs

Hands-on labs for **SC-500**: securing AI agents with Microsoft Defender XDR, Microsoft Entra Agent ID, and Microsoft Security Exposure Management.

Every lab runs in one of two modes:

- **Live tenant**: use the real portals (you need trial licenses, listed in each lab's setup).
- **Simulation**: no licenses needed. You run the lab offline with Python 3.9+ or a KQL query window, and get the same results.

## Labs

| # | Lab | Skills | Time |
|---|---|---|---|
| 01 | [Discover and assess AI agent exposure with Microsoft Defender XDR](labs/01-ai-agent-exposure/README.md) | AI agent inventory, blast radius, attack paths | ~2 h |

More labs are planned. To add one, see [Add a lab](#add-a-lab).

## Repository layout

```
sc500-labs/
├── labs/
│   └── NN-short-name/        One folder per lab (README, exercises, queries, simulation)
├── templates/lab-template/   Starting point for a new lab
└── .github/workflows/        CI: runs every lab's simulation tests
```

## Quick start

```bash
git clone https://github.com/<you>/sc500-labs.git
cd sc500-labs
cd labs/01-ai-agent-exposure/simulation
python3 agent_exposure.py inventory
```

To run the tests for every lab:

```bash
for t in labs/*/simulation/tests; do python3 -m unittest discover -s "$t" || exit 1; done
```

## Add a lab

1. Copy `templates/lab-template/` to `labs/NN-short-name/`, using the next free number.
2. Fill in the README: objectives, scenario, exercises, timing.
3. If the lab has a simulation, put its tests in `simulation/tests/` so CI runs them.
4. Add a row to the [Labs](#labs) table.

> [!NOTE]
> Many of the features in these labs are in **preview**. Portal menu names and table schemas can change, so each lab shows you how to check the current names instead of assuming them.
