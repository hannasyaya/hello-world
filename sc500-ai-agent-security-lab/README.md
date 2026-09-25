# SC-500 Lab: Discover and assess AI agent exposure with Microsoft Defender XDR

Use **Microsoft Defender XDR** to discover the AI agents that run in your environment, assess the **blast radius** of each agent identity, and analyze the **attack paths** that could lead to unauthorized data or resource access.

## Learning objectives

After you complete this lab, you can:

1. **Discover AI agents** in Microsoft Defender XDR by using the AI agent inventory → [Exercise 1](01-discover-ai-agents/README.md)
2. **Assess the blast radius of agent identities** by examining their permissions, knowledge sources, and blueprint configuration → [Exercise 2](02-assess-blast-radius/README.md)
3. **Analyze attack paths** that could result in unauthorized access if an agent identity is compromised → [Exercise 3](03-analyze-attack-paths/README.md)

## Scenario: Contoso

Contoso's business units built AI agents faster than security could track them. You are the security operations analyst, and you have Defender XDR. Contoso has these agents:

| Agent | Platform | What's wrong (you'll find out) |
|---|---|---|
| HR Benefits Assistant | Copilot Studio | Public, no authentication, reads HR-Confidential data with the maker's credentials |
| Invoice Processing Agent | Microsoft Foundry | Reads untrusted email, and its blueprint grants tenant-wide `Mail.Read` |
| DevOps Copilot | Microsoft Foundry | Contributor on production, and can read a vault that holds another blueprint's secret |
| IT Helpdesk Agent | Copilot Studio | Its agent identity holds the Helpdesk Administrator role |
| Marketing Content Agent | Copilot Studio | Orphaned: its owner has left the company |

## Two ways to run the lab

| Mode | You need | Use it when |
|---|---|---|
| **Live tenant** | M365 E5 trial, Azure subscription, Copilot Studio trial. See [Exercise 0: Setup](00-setup/README.md). | You want to use the real Defender XDR portal. |
| **Simulation** | Python 3.9+ **or** any KQL query window | You have no licenses, you are waiting for data to sync, or you are an instructor preparing the class. |

Every exercise has portal steps, advanced hunting KQL, and a simulation equivalent, so the two modes give the same results.

## Repository layout

```
sc500-ai-agent-security-lab/
├── 00-setup/                  Tenant prerequisites, deploy and clean-up scripts (Azure CLI)
├── 01-discover-ai-agents/     Exercise 1: AI agent inventory
├── 02-assess-blast-radius/    Exercise 2: permissions, knowledge, blueprints
├── 03-analyze-attack-paths/   Exercise 3: attack paths and choke points
├── queries/                   Advanced hunting KQL for the live tenant (AIAgentsInfo, ExposureGraph*)
├── simulation/
│   ├── contoso-agents.json    The simulated environment (agents, nodes, edges)
│   ├── agent_exposure.py      Offline inventory, blast-radius, and attack-path analyzer
│   ├── exposure-graph-sim.kql The same data as KQL datatables, with graph-match queries
│   └── tests/                 Unit tests for the analyzer
└── answer-key.md              Instructor answers and knowledge check
```

## Quick start (simulation)

```bash
cd sc500-ai-agent-security-lab/simulation
python3 agent_exposure.py inventory
python3 agent_exposure.py blast-radius agent-devops
python3 agent_exposure.py attack-paths
python3 -m unittest discover -s tests      # to check the lab files
```

## Timing

| Exercise | Time |
|---|---|
| 0 – Setup (live tenant only) | 45–60 min, plus up to 24 hours for data to sync |
| 1 – Discover AI agents | 30 min |
| 2 – Assess blast radius | 45 min |
| 3 – Analyze attack paths | 45 min |

> [!NOTE]
> The AI agent inventory, Microsoft Entra Agent ID, and the `AIAgentsInfo` table are **preview** features. Portal menu names and table columns can change. Each exercise tells you how to check the current names, for example by running `getschema` and discovery queries, instead of assuming them.
