# Exercise 2: Assess the blast radius of agent identities

**Objective:** For each agent identity, work out what an attacker can reach if the identity is compromised. Look at three things: the identity's **permissions**, the agent's **knowledge sources**, and the **blueprint** it comes from.
**Time:** 45 minutes

## Scenario

Your inventory lists five agents. Your team has time to harden only two this sprint. The CISO wants to know which two agents cause the most damage if an attacker takes over their identity, and why.

## Concepts

**Blast radius** is the set of resources that an attacker can reach, directly or through other resources, from a compromised identity. For an AI agent, it comes from three places:

```
                    +-----------------------------+
                    |  Agent identity blueprint   |  holds the credential and the
                    |  (Finance Agents Blueprint) |  inheritable permissions
                    +--------------+--------------+
               can act as          |           can act as
         +-------------------------+-------------------------+
         v                         v                         v
   ai-invoice-01            ai-invoice-02             ai-expense-01    <- agent identities
         |
         +-- 1. PERMISSIONS ------> Graph Mail.Read (app) -> every mailbox
         |                          Graph Sites.Read.All  -> every site
         +-- 2. KNOWLEDGE ---------> SharePoint: Finance
         +-- 3. TOOLS/CONNECTIONS -> ERP API
```

| Blast radius source | What to check | Warning signs |
|---|---|---|
| **Permissions** | Graph application permissions, Entra directory roles, Azure RBAC roles | `*.All` application permissions, Owner or Contributor at resource group or subscription scope, privileged directory roles, Key Vault secret access |
| **Knowledge sources** | SharePoint sites, Dataverse, files, websites, connected data | Sites with sensitivity labels, knowledge used with **maker credentials** (anyone who chats with the agent sees what the maker sees) |
| **Blueprint** | Credential type, number of child agent identities, inheritable permissions | Client secrets instead of certificates or managed identity, many child identities, broad inheritable permissions |

> [!IMPORTANT]
> **Blueprint rule:** an agent identity blueprint can request tokens for **every** agent identity created from it. So the blast radius of a blueprint is the **union** of the blast radius of all its child identities, plus anything you grant as an inheritable permission.

---

## Task 1: Look at the agent's permissions and knowledge in the Defender portal

1. Go to **Assets > AI agents**. Open **Invoice Processing Agent**.
2. Open the **Identity** or **Permissions** section. Select the linked agent identity to open its **identity page** (Assets > Identities).
3. Write down:
   - The **Microsoft Graph application permissions** (for example, `Mail.Read`, `Sites.Read.All`), and whether each one is **inherited from the blueprint**
   - The **Azure role assignments** and their **scope**
   - The **Entra directory roles**
4. Back on the agent page, open **Knowledge**. Write down each source and its sensitivity label.
5. Repeat for **DevOps Copilot** (identity `mi-agent-devops`) and **IT Helpdesk Agent**.

## Task 2: Use the blast radius map in Exposure Management

1. On the identity page for `mi-agent-devops`, select **View blast radius** (or go to **Exposure management > Attack surface > Explore**, search for the identity, and select **Blast radius**).
2. The graph shows everything the identity can reach. Expand the nodes in this order:
   - **Resource group** → the resources it contains (you should see the **VM** and the **storage account**)
   - **Key Vault** → **secrets**
3. Look for nodes that have the **critical asset** crown icon.

> **Question 2.1:** The DevOps Copilot identity has only two role assignments. Why does its blast radius include **all Exchange mailboxes**?

## Task 3: Measure the blast radius with KQL

Open [`../queries/02-assess-blast-radius.kql`](../queries/02-assess-blast-radius.kql).

| Query | Purpose |
|---|---|
| 2.0 | Lists the edge types in *your* graph. Use these labels in the other queries. |
| 2.1 | First-hop permissions of one identity |
| 2.2 | **Blast radius** up to 4 hops, with criticality |
| 2.3 | Ranks all agent identities by how many critical assets they can reach |
| 2.4 | Finds broad roles (Owner, Contributor, Key Vault secrets, Storage data roles) |
| 2.5 | Finds credentials that can authenticate as more than one identity (blueprint-style concentration) |
| 2.6 | Actual sign-in activity. Compare what the identity *can* do with what it *does*. |

In query 2.2, set `AgentIdentityName` to each agent identity, run it, and fill in the scorecard below.

## Task 4: Look at the blueprint configuration

1. In the Entra admin center, go to **Agent ID > Agent identity blueprints**. Open **Finance Agents Blueprint** (or the blueprint for your Foundry project).
2. Write down:
   - **Credentials**: secret, certificate, or federated or managed identity credential. When does each expire?
   - **Agent identities**: how many identities come from this blueprint?
   - **Inheritable permissions**: which permissions does every child identity get?
   - **Owners and sponsors**: who can add credentials to the blueprint?
3. Ask: *"If I steal this blueprint's credential, which identities can I impersonate?"*

## Simulation mode

```bash
cd labs/01-ai-agent-exposure/simulation
python3 agent_exposure.py blast-radius agent-devops
python3 agent_exposure.py blast-radius agent-invoice
python3 agent_exposure.py blast-radius agent-helpdesk
python3 agent_exposure.py blast-radius agent-hr-benefits
python3 agent_exposure.py blast-radius agent-marketing
```

KQL alternative: queries **S3**, **S4**, and **S5** in [`../simulation/exposure-graph-sim.kql`](../simulation/exposure-graph-sim.kql).

## Blast radius scorecard

| Agent / identity | Direct permissions | Sensitive knowledge | Blueprint (child identities) | Critical assets reachable | Max hops | Rank |
|---|---|---|---|---|---|---|
| DevOps Copilot / `mi-agent-devops` | | | | | | |
| Invoice Processing Agent / `ai-invoice-01` | | | | | | |
| IT Helpdesk Agent / `ai-helpdesk-01` | | | | | | |
| HR Benefits Assistant / maker connection | | | | | | |
| Marketing Content Agent | | | | | | |

## Task 5: Propose ways to reduce the blast radius

For each of your two top-ranked agents, write **one** change that reduces the blast radius without breaking the agent. For example:

- Replace `Mail.Read` (all mailboxes) with **Exchange RBAC for Applications** or an **application access policy** scoped to `invoices@contoso.com`.
- Replace **Contributor** on the resource group with a custom role on the one resource that the agent manages.
- Move the blueprint secret out of a vault that another agent can read, or replace the secret with a **certificate or managed identity credential**.
- Remove the inheritable permission from the blueprint. Grant the permission only to the one identity that needs it.

## Checkpoint

- [ ] You ranked all five agents by blast radius and can explain the ranking
- [ ] You can explain why a blueprint increases the blast radius
- [ ] You wrote at least two concrete ways to reduce the blast radius

To check your answers, see the [answer key](../answer-key.md#exercise-2).
