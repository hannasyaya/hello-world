# AI agent risk assessment — Contoso (simulated tenant)

**Assessed:** 2026-11-12 · **Scope:** 5 published AI agents (Copilot Studio, Microsoft Foundry) and their identities, blueprints, permissions and attack paths · **Method:** Kai multi-agent assessment: evidence → risk scoring and control mapping (in parallel) → independent auditor challenge · **Basis:** inherent risk, 5×5 likelihood × impact. No compensating control was evidenced, so no residual scores are given.

> This assessment covers the SC-500 lab's **simulated** environment (`contoso-agents.json`), not a live tenant.

## 1. Headline

Contoso's AI agents went live without the governance that would normally come before publishing. Five High risks come from agents with **too much standing access** and **untrusted entry points** (the anonymous internet, external email, any employee). No evidenced ownership, approval or monitoring process would catch them.
**Most important action:** within 2 business days, take the HR Benefits Assistant off the public website or require sign-in. Right now anyone on the internet is two hops from Highly Confidential HR data (R-02).

## 2. Risk heat map (inherent)

| Likelihood ↓ / Impact → | 1 Minimal | 2 Minor | 3 Moderate | 4 Major | 5 Severe |
|---|---|---|---|---|---|
| **5 Almost certain** | | R-06a | | **R-02** | |
| **4 Likely** | | | | **R-03** | |
| **3 Possible** | | | | R-06b · R-07 · R-08 · R-09 · R-12 | **R-01 · R-04 · R-05** |
| **2 Unlikely** | | | | | R-10 |
| **1 Rare** | | | | | |

Bold = High (15+). Five Medium risks (R-06b, R-07, R-08, R-09, R-12) cluster at L3 × I4 because they are **PROVISIONAL**: the evidence couldn't show whether the control exists, so likelihood is set to the midpoint until evidence arrives.

## 3. Top risks

| ID | Risk | Rating | Owner (suggested) | Due |
|---|---|---|---|---|
| R-02 | HR Benefits Assistant gives anonymous internet users access to HR-Confidential via maker credentials | **High 20** | TBD — HR Systems Owner | Contain by **2026-11-16**; fix by 2026-12-12 |
| R-03 | Helpdesk agent can reset other users' passwords for any employee who asks | **High 16** | TBD — IT Service Desk Manager | 2026-12-12 |
| R-01 | Tenant-wide read grants on finance agent identities, reachable by prompt injection via invoice email *(provisional)* | **High 15** | TBD — Finance Applications Owner | 2026-12-12 |
| R-04 | Finance blueprint secret is stored in an ops vault the DevOps agent can read | **High 15** | TBD — Cloud Platform Lead | Contain by **2026-11-19**; fix by 2026-12-12 |
| R-05 | DevOps Copilot holds standing Contributor and run-command power over production | **High 15** | TBD — Cloud Platform Lead | 2026-12-12 |
| R-12 | Payment fraud via crafted invoice email driving autonomous ERP posting *(provisional)* | Medium 12 | TBD — Finance Controller | 2027-02-10 |

**Quick win:** removing a single grant, the DevOps identity's Key Vault Secrets User role on `kv-contoso-ops`, closes **5 of the 11 attack paths** (R-04).

All 12 risks, with rationale and actions, are in [`risk-register.csv`](risk-register.csv).

## 4. Systemic control gaps

These are the gaps a governance function owns. Fixing them stops the same risks from coming back with the next agent.

| # | Gap | Risks |
|---|---|---|
| S1 | **AI agent inventory and accountable ownership:** one owner per agent, no backup owner, and no owner at all for identities, blueprints or connections | R-06a, R-06b |
| S2 | **Non-human identity lifecycle:** no evidenced leaver process, recertification or dormancy rule. One agent runs on a person's maker credentials. | R-02, R-06b, R-08, R-10 |
| S3 | **Privileged access for agent identities:** tenant-wide app permissions, standing production Contributor, a directory admin role, with no evidenced approval | R-01, R-03, R-05, R-10 |
| S4 | **Secrets management and trust boundaries:** finance credential sits in another domain's vault | R-04 |
| S5 | **Untrusted input handling and a pre-publication gate:** nothing evidenced stops publishing an anonymous agent with confidential knowledge | R-01, R-02, R-03, R-09, R-12 |
| S6 | **Monitoring of agent activity:** no logging or alerting evidenced for any agent | R-07 |

Control mappings to NIST CSF 2.0, ISO/IEC 27001:2022, NIST AI RMF 1.0 and ISO/IEC 42001:2023 are in [`control-gaps.md`](control-gaps.md). IDs the team wasn't certain of are marked *(verify ID)*.

## 5. Auditor opinion

**Satisfactory with exceptions.** The auditor-critic confirmed the evidence and re-ran the analysis: 11 attack paths, matching blast-radius figures, and all scores consistent with the method. It raised **8 exceptions**. All 8 are resolved:

| # | Exception | Resolution |
|---|---|---|
| X-01 | R-01 claimed all three finance identities hold both permissions | **Fixed.** Restated per identity (E-44: ai-invoice-02 has Mail.Read only; E-45: ai-expense-01 has Sites.Read.All only). Added an evidence request on where the grants are assigned. The blueprint-level action now depends on the answer. |
| X-02 | R-01 claimed disclosure that isn't evidenced | **Fixed.** Likelihood 4 → 3 (still High at 15), marked PROVISIONAL, and the assumptions are stated. |
| X-03 | "Do it now" actions had 30-day due dates | **Fixed.** Containment steps now have short dates: R-02 by 2026-11-16, R-04 by 2026-11-19. |
| X-04 | R-06 impact was inconsistent with R-08 | **Fixed.** Split into R-06a (orphaned agent: L5 × I2 = 10) and R-06b (unowned identities: L3 × I4 = 12, provisional). |
| X-05 | Control gaps claimed the analyzer missed 4 stale agents | **Fixed.** The claim was false (90-day cutoff is 2026-08-14; the agents were active in late September). Restated as a latent defect. |
| X-06 | The lab tool was treated as a Contoso control | **Fixed.** Rows reclassified to Design/Evidence. R-11 removed from the register and moved to *Assessment limitations* below. |
| X-07 | No payment-fraud risk | **Fixed.** Added R-12 (provisional) and mapped it to ISO 27001 8.26 and MEASURE 2.7. |
| X-08 | Control gaps didn't cite R-IDs | **Fixed.** Added a risk cross-reference table. The E-24 row is marked as an evidence request only. |

**Open observations (should fix, not yet done):** the auditor raised 16 observations, all still open:
- **O-01:** describe missing guardrails the same way in every risk.
- **O-02:** R-05 double-counts R-04's attack paths.
- **O-03 / O-05:** confirm the helpdesk role scope and who can reach DevOps Copilot in Teams. Either answer could raise a score.
- **O-06 / O-07:** add `score_basis` and `review_date` columns.
- **O-08:** name the owners of the High risks.
- **O-09 to O-12:** control-ID refinements (third-party mapping and supplier controls).
- **O-15:** replace people's names with role names in committee-facing files.
- **O-04, O-13, O-14, O-16:** minor fixes and notes.

Details are in [`auditor-review.md`](auditor-review.md). No disagreements with the auditor remain open.

### Assessment limitations

- **Simulated data:** everything assessed is a simulation. "Active" owner status is inferred only from absence from the disabled-users list.
- **Lab analyzer blind spots:** the analyzer (formerly R-11):
  - doesn't flag Key Vault data-plane roles;
  - truncates choke points to five, which hides `secret-bp-finance`, which is on 4 of the 11 paths;
  - checks inactivity against a fixed date. That is a latent defect that changes no current result.

  The team used the full choke-point list to compensate. If Contoso relies on Defender XDR exposure output, check whether it has similar limits.
- **Not modelled:** logging, access reviews, guardrails, secret rotation, and tool scopes aren't in the model at all. Those risks are provisional.

## 6. Next steps: decisions for you

1. **Approve the containment actions** for R-02 (by 2026-11-16) and R-04 (by 2026-11-19).
2. **Name owners** for the five High risks. Your risk appetite allows no High risk without a named owner and a review date.
3. **Send the evidence requests**, in this order:
   - logging coverage (R-07)
   - access review records (R-08)
   - guardrail, DLP and environment settings (R-09)
   - ERP API scope and approval step (R-12, R-01)
   - helpdesk role scope (R-03)
   - DevOps Copilot audience (R-04, R-05)
   - who can write to the platform-runbooks repository (E-24)

   The provisional scores are revised when the evidence comes back.
4. **Sponsor the systemic fixes:** an AI agent register with owners (S1) and a pre-publication approval gate (S5). Run `/policy standard for AI agent publication and identities` to draft them.
5. **Decide on R-06a and R-10:** unpublish the orphaned marketing agent, and remove the two finance identities that no agent uses, or accept the risk with a named owner.

## 7. Package contents

| File | Produced by | What it holds |
|---|---|---|
| [`evidence.md`](evidence.md) | evidence-collector | 70 sourced, neutral evidence items (E-01 to E-70) and gaps |
| [`risk-register.csv`](risk-register.csv) | risk-assessor, revised by Kai after audit | 12 scored risks (5 High, 7 Medium) |
| [`control-gaps.md`](control-gaps.md) | control-mapper, revised by Kai after audit | 6 systemic gaps, finding-to-control map, control improvements |
| [`auditor-review.md`](auditor-review.md) | auditor-critic | Opinion, 8 exceptions, 16 observations, possible missed risks |
| `summary.md` | Kai | This report |
