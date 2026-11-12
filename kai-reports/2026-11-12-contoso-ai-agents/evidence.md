# Evidence log — contoso-simulation (Contoso AI agents, tenant contoso.onmicrosoft.com)
Collected: 2026-11-12   Method: Read of `sc500-ai-agent-security-lab/simulation/contoso-agents.json` (cited as `json:<line>`) and `agent_exposure.py` (cited as `py:<line>`); read-only runs from `sc500-ai-agent-security-lab/simulation/` of `python3 agent_exposure.py inventory`, `python3 agent_exposure.py attack-paths`, `python3 agent_exposure.py --json attack-paths`, `python3 agent_exposure.py blast-radius <id>` for all 5 agent ids; one read-only Python import of `Environment.attack_paths()` / `choke_points()` to list choke-point counts beyond the CLI's top-5 display. Instructor material (answer-key.md, exercise READMEs) not used. No system changed.

Scope check: `contoso-simulation` is listed in `.claude/kai/scope.txt`. The model describes itself as a simulation of what Defender XDR shows in the AI agent inventory and Exposure Management graph (`json:3`). All facts below are facts about the model, not about a live tenant.

## A. Inventory: agent attributes

| ID | Asset | Observation (fact only) | Source |
|---|---|---|---|
| E-01 | Environment model | 5 agents are defined; all 5 have `status: Published`. | `json:4-85`; `inventory` header "5 agents" |
| E-02 | Environment model | `disabledUsers` contains exactly one account: former.employee@contoso.com. No other account-status field (active/departed, last sign-in) exists in the model. | `json:86` |
| E-03 | agent-hr-benefits (HR Benefits Assistant) | Platform Copilot Studio; environment Contoso-Production; status Published; generativeOrchestration true. | `json:6-15` |
| E-04 | agent-hr-benefits | Owner and createdBy: alex.wilber@contoso.com (one owner). Account is not listed in `disabledUsers`. | `json:11-12,86` |
| E-05 | agent-hr-benefits | `userAuthentication: "None"`; channel "Public website". Graph edge ep-internet (Anonymous internet user) → agent `canChatWith`, note "No user authentication; published to public website". | `json:13-14,125` |
| E-06 | agent-hr-benefits | `identity: null` (no agent identity, managed identity or blueprint linked). | `json:16`; `blast-radius agent-hr-benefits` "(identity: none)" |
| E-07 | agent-hr-benefits | Tool "Get employee record (SharePoint connector, maker credentials)". Graph: agent `usesConnection` conn-maker-alex ("SharePoint connection (alex.wilber, maker credentials)"), which `canRead` kn-hr-sharepoint. | `json:18,106,131-132` |
| E-08 | agent-hr-benefits | Knowledge source kn-hr-sharepoint "SharePoint: HR-Confidential", sensitivity "Highly Confidential", `critical: true`. | `json:17,108,133` |
| E-09 | agent-hr-benefits | lastActivity 2026-09-23 (50 days before collection date). | `json:19` |
| E-10 | agent-hr-benefits | Inventory findings reported by tool: "No user authentication", "Tool runs with maker credentials", "No dedicated Entra agent identity", "Knowledge source holds critical data". | `python3 agent_exposure.py inventory` |
| E-11 | agent-invoice (Invoice Processing Agent) | Platform Azure AI Foundry; environment proj-finance-agents; status Published; generativeOrchestration true. | `json:22-31` |
| E-12 | agent-invoice | Owner and createdBy: megan.bowen@contoso.com (one owner); not listed in `disabledUsers`. | `json:27-28,86` |
| E-13 | agent-invoice | `userAuthentication: "Entra ID (autonomous, app-only)"`; channel "Shared mailbox trigger: invoices@contoso.com". Graph edge ep-email ("External sender (indirect prompt injection via invoice email)") → agent `canInjectPromptInto`, note "Agent processes untrusted email bodies and attachments". | `json:29-30,89,126` |
| E-14 | agent-invoice | Identity ai-invoice-01 (`runsAs`, type agentIdentity). | `json:32,101,135` |
| E-15 | agent-invoice | Tools: "Read mail", "Search SharePoint", "Post to ERP API". No graph node models the ERP API or its credential. | `json:34`; nodes list `json:87-123` |
| E-16 | agent-invoice | Knowledge source kn-finance-sharepoint "SharePoint: Finance", sensitivity "Confidential", no `critical` flag. | `json:33,109,136` |
| E-17 | agent-invoice | lastActivity 2026-09-24 (49 days before collection date). | `json:35` |
| E-18 | agent-invoice | Inventory findings reported by tool: "High-privilege grant: Mail.Read (application, inherited from blueprint) on All Exchange Online mailboxes (incl. CFO)" and "High-privilege grant: Sites.Read.All (application, inherited from blueprint) on All SharePoint Online sites". | `inventory` |
| E-19 | agent-devops (DevOps Copilot) | Platform Azure AI Foundry; environment proj-platform-eng; status Published; generativeOrchestration true. | `json:38-47` |
| E-20 | agent-devops | Owner and createdBy: lee.gu@contoso.com (one owner); not listed in `disabledUsers`. | `json:43-44,86` |
| E-21 | agent-devops | `userAuthentication: "Entra ID (on-behalf-of + managed identity for tools)"`; channel Microsoft Teams. Graph edge ep-dev-workstation ("Compromised developer workstation (lee.gu)") → agent `canInvoke`, note "Stolen Teams session / Foundry project access". | `json:45-46,90,127` |
| E-22 | agent-devops | Identity mi-agent-devops (`runsAs`, type managedIdentity); no blueprint `canActAs` edge targets it. | `json:48,105,145` |
| E-23 | agent-devops | Tools: "Azure Resource Manager", "Key Vault get secret", "Run command on VM". | `json:50` |
| E-24 | agent-devops | Knowledge source kn-runbooks-repo "GitHub: platform-runbooks", sensitivity "General". | `json:49,110,146` |
| E-25 | agent-devops | lastActivity 2026-09-24 (49 days before collection date). | `json:51` |
| E-26 | agent-devops | Inventory finding reported by tool: "High-privilege grant: Contributor on Resource group rg-production". The Key Vault Secrets User grant is not listed as an inventory finding (the check at `py:84` flags only permissions containing "application" or equal to Owner/Contributor). | `inventory`; `py:81-87` |
| E-27 | agent-helpdesk (IT Helpdesk Agent) | Platform Copilot Studio; environment Contoso-Production; status Published; generativeOrchestration true. | `json:54-63` |
| E-28 | agent-helpdesk | Owner and createdBy: isaiah.langer@contoso.com (one owner); not listed in `disabledUsers`. | `json:59-60,86` |
| E-29 | agent-helpdesk | `userAuthentication: "Entra ID (authenticated users)"`; channel Microsoft Teams. Graph edge ep-teams-user ("Any authenticated employee (Teams)") → agent `canChatWith`. | `json:61-62,91,128` |
| E-30 | agent-helpdesk | Identity ai-helpdesk-01 (`runsAs`, type agentIdentity); blueprint bp-itops ("IT Operations Agents Blueprint") `canActAs` ai-helpdesk-01. | `json:64,100,104,153,155` |
| E-31 | agent-helpdesk | Tools: "Reset user password (Microsoft Graph)", "Unlock account". | `json:66` |
| E-32 | agent-helpdesk | Knowledge source kn-it-kb "SharePoint: IT Knowledge Base", sensitivity "General". | `json:65,111,154` |
| E-33 | agent-helpdesk | lastActivity 2026-09-22 (51 days before collection date). | `json:67` |
| E-34 | agent-helpdesk | Inventory finding reported by tool: "Holds directory role: Entra role: Helpdesk Administrator". | `inventory` |
| E-35 | agent-marketing (Marketing Content Agent) | Platform Copilot Studio; environment Contoso-Default; status Published; generativeOrchestration false. | `json:70-79` |
| E-36 | agent-marketing | Owner and createdBy: former.employee@contoso.com (one owner); this account is listed in `disabledUsers`. | `json:75-76,86` |
| E-37 | agent-marketing | `userAuthentication: "Entra ID (authenticated users)"`; channel Microsoft Teams. Graph edge ep-teams-user → agent `canChatWith`. | `json:77-78,129` |
| E-38 | agent-marketing | `identity: null`; `tools: []`. | `json:80,82` |
| E-39 | agent-marketing | Knowledge source kn-public-website "Public website contoso.com", sensitivity "Public". | `json:81,112,160` |
| E-40 | agent-marketing | lastActivity 2026-03-02 (255 days before collection date). | `json:83` |
| E-41 | agent-marketing | Inventory findings reported by tool: "Orphaned (all owners disabled)", "No dedicated Entra agent identity", "Inactive > 90 days". | `inventory` |

## B. Identities, blueprints, permissions, secrets

| ID | Asset | Observation (fact only) | Source |
|---|---|---|---|
| E-42 | bp-finance (Finance Agents Blueprint) | `canActAs` three agent identities: ai-invoice-01, ai-invoice-02, ai-expense-01. Edge note: "Blueprint credential can request tokens for every child agent identity". | `json:99,137-139`; `blast-radius agent-invoice` |
| E-43 | ai-invoice-01 | `hasPermission` Mail.Read (application, inherited from blueprint) on all-mailboxes ("All Exchange Online mailboxes (incl. CFO)", critical) and Sites.Read.All (application, inherited from blueprint) on all-sites ("All SharePoint Online sites", critical). | `json:114-115,140-141` |
| E-44 | ai-invoice-02 | `hasPermission` Mail.Read (application, inherited from blueprint) on all-mailboxes. No agent in `agents[]` has `runsAs` to ai-invoice-02. | `json:142`; `json:4-85` |
| E-45 | ai-expense-01 | `hasPermission` Sites.Read.All (application, inherited from blueprint) on all-sites. No agent in `agents[]` has `runsAs` to ai-expense-01. | `json:143`; `json:4-85` |
| E-46 | bp-finance | Permissions labelled "inherited from blueprint" are modelled as edges on each child identity; no `hasPermission` edge originates at bp-finance itself. | `json:137-143` |
| E-47 | mi-agent-devops | `hasRoleOn` Contributor on rg-production; rg-production `contains` vm-sql-prod ("VM vm-sql-prod (payroll database)", critical). | `json:116-117,147-148` |
| E-48 | mi-agent-devops | `hasRoleOn` Key Vault Secrets User on kv-contoso-ops (critical). | `json:118,149` |
| E-49 | kv-contoso-ops | `contains` secret-bp-finance ("Secret: finance-blueprint-client-secret", type credential); secret-bp-finance `authenticatesAs` bp-finance. This is the only credential node in the model. | `json:119,150-151` |
| E-50 | ai-helpdesk-01 | `memberOf` role-helpdesk-admin ("Entra role: Helpdesk Administrator"); role `canResetPasswordOf` user-dana ("dana.finance@contoso.com (non-admin user)"); user-dana `hasRoleOn` Storage Blob Data Reader on st-payroll ("Storage account stpayrollcontoso", critical). | `json:120-122,156-158` |
| E-51 | bp-itops | Only child identity is ai-helpdesk-01. No credential node for bp-itops exists in the model. | `json:155`; `blast-radius agent-helpdesk` |
| E-52 | conn-maker-alex | Connection runs with alex.wilber maker credentials; only modelled permission is `canRead` kn-hr-sharepoint. It is the only `connection` node in the model; no other agent uses a maker-credential connection. | `json:106,131-132` |
| E-53 | Secrets reachable per agent | Per tool blast radius: agent-devops reaches secret-bp-finance at hop 3 (via kv-contoso-ops). No other agent's blast radius includes a credential node. | `blast-radius <id>` for all 5 agents |

## C. Blast radius (tool output)

| ID | Asset | Observation (fact only) | Source |
|---|---|---|---|
| E-54 | agent-hr-benefits | reachable 2, critical 1 (kn-hr-sharepoint), score 7. | `blast-radius agent-hr-benefits` |
| E-55 | agent-invoice | reachable 4, critical 2 (all-mailboxes, all-sites), score 35. Blueprint bp-finance shared by ai-invoice-01, ai-invoice-02, ai-expense-01; "blast radius if the blueprint credential leaks: score 39". | `blast-radius agent-invoice` |
| E-56 | agent-devops | reachable 12, critical 4 (kv-contoso-ops, vm-sql-prod, all-mailboxes, all-sites), score 74. Path reaches bp-finance at hop 4 and all three finance identities at hop 5. | `blast-radius agent-devops` |
| E-57 | agent-helpdesk | reachable 5, critical 1 (st-payroll at hop 4), score 20. Blueprint bp-itops shared by ai-helpdesk-01 only; blueprint blast-radius score 18. | `blast-radius agent-helpdesk` |
| E-58 | agent-marketing | reachable 1, critical 0, score 2. | `blast-radius agent-marketing` |
| E-59 | Scoring method | Score = sum of type weight per reached node, x3 if node is critical (weights at `py:29-33`). Blast radius follows privilege edges only, not entry edges. | `py:20-33,97-117` |

## D. Attack paths (tool output)

| ID | Asset | Observation (fact only) | Source |
|---|---|---|---|
| E-60 | Environment | Tool reports "11 attack paths to critical assets" (default `--max-hops 8`; longest path found is 7 hops). | `attack-paths`; `py:249` |
| E-61 | Entry points | Four entryPoint nodes: ep-internet, ep-email, ep-dev-workstation, ep-teams-user. Paths per entry point: ep-dev-workstation 6, ep-internet 2, ep-email 2, ep-teams-user 1. | `json:88-91`; read-only `Environment.attack_paths()` count |
| E-62 | Targets | Paths per critical target: all-mailboxes 3, all-sites 3, kn-hr-sharepoint 2, kv-contoso-ops 1, vm-sql-prod 1, st-payroll 1. | read-only `Environment.attack_paths()` count |
| E-63 | Shortest path | [1] 2 hops: Anonymous internet user → HR Benefits Assistant → SharePoint: HR-Confidential. | `attack-paths` |
| E-64 | Longest paths | [8]-[11] 7 hops: Compromised developer workstation (lee.gu) → DevOps Copilot → mi-agent-devops → kv-contoso-ops → finance-blueprint-client-secret → Finance Agents Blueprint → ai-invoice-01/ai-invoice-02/ai-expense-01 → all-mailboxes / all-sites. | `attack-paths` |
| E-65 | Choke points (CLI) | Top 5 displayed: DevOps Copilot 6, mi-agent-devops 6, ai-invoice-01 4, Finance Agents Blueprint 4, Key Vault kv-contoso-ops 4. | `attack-paths` |
| E-66 | Choke points (full list) | secret-bp-finance also appears on 4 paths but is not shown because the CLI truncates to 5 entries (`[:5]`, ties sorted by node id). Remaining: agent-hr-benefits 2, agent-invoice 2; agent-helpdesk, ai-expense-01, ai-helpdesk-01, ai-invoice-02, conn-maker-alex, rg-production, role-helpdesk-admin, user-dana 1 each. | `py:155-161,236`; read-only `Environment.choke_points()` |
| E-67 | agent-marketing | Appears on 0 attack paths to critical assets. | `attack-paths`; E-66 list |

## E. Analyzer behaviour relevant to interpreting output

| ID | Asset | Observation (fact only) | Source |
|---|---|---|---|
| E-68 | `inventory` inactivity check | "Inactive > 90 days" is computed as `lastActivity < "2026-06-01"` (fixed string date), not relative to the run date. Relative to 2026-11-12, 2026-06-01 is 164 days earlier. | `py:90-91` |
| E-69 | `inventory` owner check | "Orphaned" is raised only when all owners appear in `disabledUsers`. | `py:69,77-78` |
| E-70 | KQL companion | `exposure-graph-sim.kql` rebuilds the same agents, disabled users and nodes as KQL datatables "from contoso-agents.json"; no additional data source. | `exposure-graph-sim.kql:1-30` |

## Gaps
- Logging / monitoring: the model has no fields for audit logging, diagnostic settings, Defender/Sentinel alerting, conversation transcripts or prompt-injection detection for any agent. Not evidenced either way. Question for risk assessor: is monitoring coverage of agent activity assumed absent or unknown?
- Access reviews / recertification: no review dates, reviewers or recertification records for agents, identities, blueprints, connections or role assignments. Not evidenced.
- Ownership process: only `owners`, `createdBy` and a `disabledUsers` list exist. No owner/sponsor fields for agent identities, blueprints (bp-finance, bp-itops), mi-agent-devops or conn-maker-alex; no backup owners; no joiner/mover/leaver process data. Owner status for alex.wilber, megan.bowen, lee.gu and isaiah.langer is inferred only from absence from `disabledUsers`; positive "active" status is not evidenced.
- Activity detail: only a single `lastActivity` date per agent. No usage volumes, sign-in logs or per-identity activity for ai-invoice-02 / ai-expense-01 (identities with grants but no owning agent in the inventory). Question for risk assessor: are these unused identities with standing application permissions?
- Tool inactivity cutoff is hard-coded (E-68). All five agents last active 49-255 days before collection; only agent-marketing exceeds 90 days. Question: should staleness be re-evaluated against the assessment date?
- Secret details: no rotation date, expiry or access policy for secret-bp-finance; no inventory of other secrets in kv-contoso-ops (only one `contains` edge is modelled). Whether "Key Vault Secrets User" grants read of all secrets in the vault is not stated in the data. Values were not and should not be copied.
- bp-itops credential: no credential node exists, so where the blueprint secret/certificate lives is not evidenced.
- ERP API (agent-invoice "Post to ERP API") and "Run command on VM" / "Reset user password" tool scopes are named in `tools` but have no permission edges; their effective scope is not evidenced.
- Helpdesk password-reset reach: the graph models one reset target (user-dana). Whether the Helpdesk Administrator role reaches other non-admin users is not modelled. Question: is user-dana representative or the only target?
- Guardrails: no data on content filters, prompt shields, human-in-the-loop approval, DLP or sensitivity-label enforcement on knowledge sources. Not evidenced.
- Environment governance: no data on Power Platform environment DLP policies (Contoso-Production, Contoso-Default) or Foundry project RBAC. Not evidenced.
- Entry-point realism: ep-dev-workstation is a hypothetical compromise node ("Compromised developer workstation"), not an observed event. Question: should its paths be scored as assumed-breach scenarios?
- Criticality labels: kn-finance-sharepoint is "Confidential" but not flagged `critical`, so the tool does not count it as an attack-path target. Question for risk assessor: is that classification accepted?
- Questions for risk assessor (judgement deliberately not made here): is an unauthenticated public channel with a Highly Confidential knowledge source acceptable (E-05, E-08)? Are tenant-wide application Mail.Read / Sites.Read.All grants for an email-triggered agent proportionate (E-13, E-43)? Is storing the finance blueprint secret in a vault readable by the DevOps managed identity an intended trust boundary (E-48, E-49)? Is a published agent owned only by a disabled account an orphaned asset (E-36)?
