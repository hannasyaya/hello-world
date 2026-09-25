# Answer key (instructor)

The answers are based on the simulated Contoso environment (`simulation/contoso-agents.json`). Results in a live tenant depend on what you built.

## Exercise 1

| Agent | Platform | Owner status | Authentication | Agent identity | Top concern |
|---|---|---|---|---|---|
| HR Benefits Assistant | Copilot Studio | Active | **None**, public website | None, uses a maker connection | Anonymous users can read HR-Confidential data through the maker's credentials |
| Invoice Processing Agent | Foundry | Active | Autonomous, app-only | `ai-invoice-01` | Tenant-wide Graph application permissions inherited from the blueprint |
| DevOps Copilot | Foundry | Active | OBO + managed identity | `mi-agent-devops` | Contributor on `rg-production` and read access to vault secrets |
| IT Helpdesk Agent | Copilot Studio | Active | Entra ID | `ai-helpdesk-01` | Holds the Helpdesk Administrator directory role |
| Marketing Content Agent | Copilot Studio | **Orphaned** | Entra ID | None | No accountable owner, and inactive for more than 90 days |

**Q1.1:** When authentication is off, anyone can use the agent. When knowledge or connectors run with the maker's credentials, the agent has access to confidential data. Together, anyone on the internet gets that data, and the only thing in the way is the model's willingness to answer. Prompt injection gets past that easily. Either problem alone is much less severe: authentication alone limits who can ask, and a knowledge source that uses the end user's credentials respects that user's permissions.

**Q1.2:** `AIAgentsInfo` is a **snapshot** table. It stores a new row every time the configuration changes or is refreshed. Without `arg_max`, agents are counted more than once, and you might read an out-of-date configuration.

## Exercise 2

Output of `python3 agent_exposure.py blast-radius <agent>`:

| Agent / identity | Direct permissions | Sensitive knowledge | Blueprint (child identities) | Critical assets reachable | Max hops | Score | Rank |
|---|---|---|---|---|---|---|---|
| DevOps Copilot / `mi-agent-devops` | Contributor (RG), Key Vault Secrets User | No | None, but it can **reach** the Finance blueprint | **4** (vault, VM, mailboxes, sites) | 6 | **74** | **1** |
| Invoice Processing Agent / `ai-invoice-01` | Mail.Read, Sites.Read.All (application, inherited) | Finance (Confidential) | Finance Agents Blueprint (3 identities) | 2 | 2 | 35 | **2** |
| IT Helpdesk Agent / `ai-helpdesk-01` | Helpdesk Administrator role | No | IT Operations Agents Blueprint (1 identity) | 1 (payroll storage) | 4 | 20 | 3 |
| HR Benefits Assistant / maker connection | Maker's SharePoint access | **HR-Confidential** | – | 1 | 2 | 7 | 4* |
| Marketing Content Agent | None | Public only | – | 0 | – | 2 | 5 |

\* The HR agent has a **small** blast radius but the **highest likelihood**, because it has an anonymous entry point. Blast radius measures *impact*. Risk combines impact and likelihood. A strong answer names DevOps Copilot (impact) and HR Benefits Assistant (likelihood and ease of exploitation) as the two to harden first. Invoice Processing Agent is also a valid answer.

**Q2.1:** `mi-agent-devops` can read the secrets in `kv-contoso-ops`. The vault stores the **Finance Agents Blueprint** client secret. The blueprint can act as `ai-invoice-01`, `ai-invoice-02`, and `ai-expense-01`, and those identities inherit `Mail.Read` for the whole tenant. Blast radius is **transitive**: one secret-read role adds another identity's entire blast radius to this one.

**Blueprint insight:** if the Finance blueprint credential leaks, the attacker gets the combined access of all 3 child identities (score 39), which is more than any single identity (35). Inheritable permissions make every future child identity overprivileged too.

## Exercise 3

`python3 agent_exposure.py attack-paths` returns **11 paths**:

| Entry point | Paths | Shortest |
|---|---|---|
| Anonymous internet user → HR Benefits Assistant | 2 | 2 hops to HR-Confidential |
| External email (prompt injection) → Invoice Processing Agent | 2 | 3 hops to all mailboxes or all sites |
| Compromised developer → DevOps Copilot | 6 | 3 hops to the Key Vault, 7 hops to mailboxes through the blueprint |
| Any employee → IT Helpdesk Agent | 1 | 5 hops to payroll storage (password reset → user → storage) |
| Any employee → Marketing Content Agent | 0 | No path |

**Choke points:**

| Node | Paths through it |
|---|---|
| DevOps Copilot / `mi-agent-devops` | 6 |
| `kv-contoso-ops`, blueprint secret, Finance Agents Blueprint, `ai-invoice-01` | 4 each |

**Challenge:** if you remove `mi-agent-devops → kv-contoso-ops`, **6** paths are left. The fix closes 5 paths: the direct vault path and the four 7-hop paths through the blueprint.

**Q3.1:** Secrets are **credentials**, so reading one turns into *authenticating as* another principal. The attacker moves sideways into a different identity with different permissions. The graph shows this as a `contains` → `can authenticate as` pair of edges. Always assume a secret-read role grants the full permissions of every identity whose secret is in that vault.

**Chained-path fixes (Task 4):**

1. Require Conditional Access and compliant devices to invoke the agent. Use user-delegated (on-behalf-of) tokens where possible.
2. Give the managed identity only the roles that the agent's tools need.
3. Remove *Key Vault Secrets User*, or scope it to single secrets in a dedicated vault.
4. Don't store another identity's credential in a shared operations vault.
5. Replace the blueprint's client secret with a certificate or federated or managed identity credential, and rotate it.
6. Use a separate blueprint for each workload, so that fewer child identities share one credential.
7. Remove the inheritable `Mail.Read`, and scope mailbox access with Exchange RBAC for Applications.

## Knowledge check

1. **Where do you see all the Copilot Studio and Foundry agents in your tenant, with their owners and authentication settings?**
   a) Entra ID > Enterprise apps  b) **Defender portal > Assets > AI agents**  c) Purview Data Map  d) Azure Resource Graph
2. **An agent identity blueprint has 12 child agent identities, and you grant it the inheritable permission `Files.Read.All`. What is the blast radius of the blueprint credential?**
   **The union of all 12 identities' access, including `Files.Read.All` for every identity.** The blueprint can request tokens for every child.
3. **Which advanced hunting query pattern returns one row per agent, with its current configuration?**
   `AIAgentsInfo | summarize arg_max(Timestamp, *) by AIAgentId`
4. **True or false: a Copilot Studio agent without an agent identity has no blast radius.**
   **False.** Knowledge sources and connectors that run with **maker credentials** give the agent the maker's access.
5. **Which KQL operator lets you find multi-hop paths in `ExposureGraphEdges`?**
   `make-graph` together with `graph-match`
6. **What makes a node a "choke point"?**
   It lies on many attack paths. If you fix it, you close all of those paths at once.
7. **Name two entry points into an agent that traditional attack paths don't model.**
   Anonymous or unauthenticated chat, and **indirect prompt injection** through content that the agent processes (email, documents, web pages).
