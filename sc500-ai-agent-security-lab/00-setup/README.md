# Exercise 0: Set up the lab environment

**Time:** 45–60 minutes of work, then up to 24 hours for the data to reach Defender XDR
**Skip this exercise** if you use **Simulation mode** only. Go to [Exercise 1](../01-discover-ai-agents/README.md).

> [!IMPORTANT]
> Use a **developer or trial tenant** and a **lab subscription**. This lab gives identities too much access on purpose. Never run it in production.

> [!NOTE]
> AI agent inventory, Microsoft Entra Agent ID, and agent attack paths are **preview** features. Menu names and locations can change. If a step doesn't match your portal, search for the feature name in the portal search bar.

## Prerequisites

| Requirement | Why you need it |
|---|---|
| Microsoft 365 E5 (or E5 Security) trial, including Microsoft Defender XDR and Defender for Cloud Apps | AI agent inventory, advanced hunting |
| Microsoft Security Exposure Management (included in the Defender portal) | Exposure graph, blast radius, attack paths |
| Azure subscription where you have **Owner** | Deploy resources, Microsoft Foundry, Defender for Cloud |
| Microsoft Copilot Studio trial | Build the Copilot Studio agents |
| Roles: **Security Administrator**, **Power Platform Administrator**, **Application Administrator** (or Global Administrator in a dev tenant) | Turn on the connectors and view agent identities |
| Azure CLI 2.60+ and Python 3.9+ | Setup script and offline analyzer |

## Task 1: Deploy the Azure resources

```bash
az login
az account set --subscription "<lab-subscription-id>"
cd sc500-ai-agent-security-lab/00-setup
chmod +x deploy-lab-resources.sh cleanup.sh
./deploy-lab-resources.sh --location eastus --enable-defender-cspm
```

The script creates:

| Resource | Misconfiguration you will find later |
|---|---|
| `mi-agent-devops` (user-assigned managed identity) | **Contributor** on the whole resource group and **Key Vault Secrets User** on the vault |
| `kv-sc500ops-*` (Key Vault) | Stores `finance-blueprint-client-secret`, a credential that belongs to *another* agent identity |
| `stsc500payroll*` (Storage account) | Holds payroll data. `mi-agent-invoice` can read every container in it. |

## Task 2: Build the agents

Build the agents from the scenario. You don't have to build all five. At a minimum, build agents **1** and **3**.

1. **HR Benefits Assistant** (Copilot Studio)
   1. Go to [copilotstudio.microsoft.com](https://copilotstudio.microsoft.com). Create an agent.
   2. Add a **SharePoint** knowledge source that points to a site with sample "confidential" HR files.
   3. Go to **Settings > Security > Authentication**. Select **No authentication**.
   4. Publish the agent to the **Demo website** channel.
2. **Marketing Content Agent** (Copilot Studio). Add a public website as its knowledge source and publish it. Then set its owner to a test user and **disable that user** in Microsoft Entra ID. The agent is now orphaned.
3. **DevOps Copilot** (Microsoft Foundry)
   1. In the [Foundry portal](https://ai.azure.com), create a project and an agent.
   2. Give the agent tools that call Azure Resource Manager and Key Vault with the **`mi-agent-devops`** managed identity.
   3. Publish the agent. Publishing creates a Microsoft Entra **agent identity** for it.
4. **Invoice Processing Agent** (Microsoft Foundry). Create and publish a second agent in a separate project. Foundry creates an **agent identity blueprint** for the project and an **agent identity** from that blueprint.
5. **Optional: inheritable permissions on the blueprint**
   1. In the [Microsoft Entra admin center](https://entra.microsoft.com), go to **Entra ID > Agent ID > Agent identity blueprints**. Open the blueprint for the Invoice project.
   2. Add the Microsoft Graph application permission `Mail.Read` as an **inheritable permission**, and grant admin consent.
   3. Every agent identity created from this blueprint now inherits the permission. This is what you investigate in Exercise 2.

## Task 3: Connect the agent platforms to Defender XDR

1. **Copilot Studio agents**
   1. Go to the [Defender portal](https://security.microsoft.com) > **Settings > Cloud Apps > Copilot Studio AI Agents**. Turn on **AI agent protection**, and make sure the Microsoft 365 app connector is connected.
   2. Go to the [Power Platform admin center](https://admin.powerplatform.microsoft.com) > **Security > Threat protection**. Turn on **Microsoft Defender – Copilot Studio AI Agents**.
2. **Foundry agents**
   1. In **Microsoft Defender for Cloud > Environment settings**, open the subscription.
   2. Make sure **Defender CSPM** is **On**, including the **AI security posture management** extension.
3. **Microsoft Entra**. Exposure Management connects to Microsoft Entra ID automatically. Make sure **Exposure Management > Data connectors** shows no errors.

## Task 4: Mark your critical assets

Attack paths only end at **critical** assets, so mark them before you start.

1. In the Defender portal, go to **Exposure management > Exposure insights > Critical asset management**.
2. Check that the built-in rules classify Key Vaults and your Global Administrators as critical.
3. Select **Create a new classification**. Name it `SC500 lab crown jewels`, with this condition: *Resource tags contain `lab=sc500-ai-agents`* (or *Resource name starts with `stsc500payroll`*). Set **Criticality level** to **High**.
4. In the SharePoint admin center, apply the **Highly Confidential** sensitivity label to the HR site.

## Task 5: Wait for the data to arrive

| Data | Typical delay |
|---|---|
| Copilot Studio agents in the AI agent inventory | 1–4 hours after you turn on the connector |
| `AIAgentsInfo` in advanced hunting | Up to 24 hours |
| Exposure graph nodes, edges, and attack paths | Up to 24 hours |

**While you wait:** work through the Simulation mode steps in each exercise.

## Clean up

```bash
./cleanup.sh
```

Also delete the Copilot Studio agents, the Foundry projects, and any blueprint permissions that you added.
