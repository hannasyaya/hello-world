# Exercise 1: Discover AI agents with the AI agent inventory

**Objective:** Discover the AI agents that run in your environment in Microsoft Defender XDR, and find the ones that need attention first.
**Time:** 30 minutes

## Scenario

The CISO at Contoso asks you: *"How many AI agents do we have, who owns them, and which ones can anyone on the internet talk to?"* Nobody in IT has a list. Makers built agents in Copilot Studio, and developers published agents from Microsoft Foundry. Your job is to build the list from Defender XDR.

## Concepts

| Term | Meaning |
|---|---|
| **AI agent inventory** | The **Assets > AI agents** page in the Defender portal. It lists the agents that Defender discovers from Copilot Studio, Microsoft Foundry, and other connected platforms, with their owners, status, configuration, and posture. |
| **Agent identity** | A Microsoft Entra identity (Entra Agent ID) that the agent uses to get tokens and access resources. |
| **`AIAgentsInfo`** | The advanced hunting table with a snapshot of each agent's configuration: creator, owners, authentication, knowledge, tools, and topics. |

---

## Task 1: Browse the AI agent inventory (live tenant)

1. Go to [https://security.microsoft.com](https://security.microsoft.com).
2. Select **Assets > AI agents**. (Depending on your tenant's preview ring, the page can also be under **Assets > Cloud apps > AI agents**.)
3. Look at the columns: **Name, Platform, Status, Owner, Created by, Last modified, Authentication**, and the **risk or posture** indicators.
4. Filter the list:
   - **Platform = Copilot Studio**, then **Platform = Microsoft Foundry**. How many agents does each platform have?
   - **Status = Published**. Only published agents are available to users.
5. Open **HR Benefits Assistant**. The agent details panel shows:
   - **Overview**: platform, environment, creator, owners, and publish date
   - **Configuration**: authentication, channels, and generative orchestration
   - **Knowledge and tools**: data sources and actions
   - **Identity**: the linked Entra agent identity, if there is one
   - **Recommendations and alerts**: posture findings and active alerts

   Write down what you find in the table at the end of this exercise.
6. Open the **Recommendations** tab. Look for recommendations such as *"Agent does not require user authentication"* or *"Agent uses maker credentials for connectors"*.

> **Question 1.1:** Why is an agent that has **no authentication** *and* a knowledge source with confidential data more dangerous than either problem alone?

## Task 2: Hunt for agents with KQL (live tenant)

1. Go to **Investigation & response > Hunting > Advanced hunting**.
2. Open [`../queries/01-discover-ai-agents.kql`](../queries/01-discover-ai-agents.kql). Run the queries one at a time:

| Query | Purpose |
|---|---|
| 1.0 | Shows the columns of `AIAgentsInfo`. This table is in preview, so change the column names in the other queries if they differ. |
| 1.1 | Current inventory, one row per agent, using `arg_max`. |
| 1.2 | Agents grouped by status and authentication type. |
| 1.3 | **Published agents that don't require sign-in** |
| 1.4 | **Orphaned agents**: no owner has an enabled account. Joins to `IdentityInfo`. |
| 1.5 | Knowledge sources and tools of each agent |
| 1.6 | New or changed agents in the last 7 days |
| 1.7 | Agent identity node types in the exposure graph. You use these labels in Exercises 2 and 3. |

3. **Detection rule:** save query 1.3 as a **custom detection rule** that runs every 24 hours. Set the alert severity to **Medium**, and map `AIAgentId` as the impacted asset. Any new public agent now raises an alert.

> **Question 1.2:** Why does every query start with `summarize arg_max(Timestamp, *) by AIAgentId`?

## Task 3: Find the agent identities in Microsoft Entra

1. Go to the [Entra admin center](https://entra.microsoft.com) > **Entra ID > Agent ID > All agent identities**.
2. Find the identities for **DevOps Copilot** and **Invoice Processing Agent**.
3. On each identity, look at **Blueprint**. This is the parent agent identity blueprint.
4. Compare with the Copilot Studio agents. Which ones have **no** agent identity, and what do they use to authenticate to data?

## Simulation mode (no licenses needed)

```bash
cd sc500-ai-agent-security-lab/simulation
python3 agent_exposure.py inventory
```

Or run query **S1** and query **S2** in [`../simulation/exposure-graph-sim.kql`](../simulation/exposure-graph-sim.kql). Highlight the **LET BLOCK** plus one query, then select **Run**.

## Record your findings

| Agent | Platform | Owner status | Authentication | Agent identity | Top concern |
|---|---|---|---|---|---|
| HR Benefits Assistant | | | | | |
| Invoice Processing Agent | | | | | |
| DevOps Copilot | | | | | |
| IT Helpdesk Agent | | | | | |
| Marketing Content Agent | | | | | |

## Checkpoint

You have finished this exercise when you can:

- [ ] Say how many agents run in the tenant, and on which platforms
- [ ] Name the agents that allow anonymous access, and the agents that are orphaned
- [ ] Say which agents have a dedicated Entra agent identity
- [ ] Show a saved custom detection rule for new unauthenticated agents

To check your answers, see the [answer key](../answer-key.md#exercise-1).
