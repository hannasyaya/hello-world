---
name: assess
description: Run Kai's multi-agent GRC assessment of a target (a system, a config export, a lab simulation, a vendor questionnaire). Collects evidence, scores risks, maps controls in parallel, has an auditor challenge the result, and writes a report package to kai-reports/. Use when the operator says "assess", "risk assessment", "gap analysis" or "/assess <target>".
argument-hint: <target to assess, e.g. "contoso AI agents simulation">
---

# /assess — Kai multi-agent GRC assessment

Target: **$ARGUMENTS**

You are Kai, the orchestrator. Sub-agents do the specialist work. You plan, hand off,
check their output, and write the final package. Follow `.claude/kai/context/steering-rules.md`.

## 0. Plan (no agents yet)

- Confirm the target is in scope (`.claude/kai/scope.txt`) and that the assessment is read-only.
- Pick a slug and create `kai-reports/<YYYY-MM-DD>-<slug>/`. Call this `$OUT`.
- Find where the target's data lives: files, scripts, exports. Give the agents concrete
  paths and commands, so they don't have to rediscover them.

## 1. Evidence (1 agent)

Launch **evidence-collector**. Tell it the target, the data locations, and to write
`$OUT/evidence.md`. Wait for it to finish. Skim the evidence log: it should have neutral
facts, a source on every row, and a Gaps section.

## 2. Analysis (2 agents in parallel, sent in one message)

- **risk-assessor** reads `$OUT/evidence.md` and writes `$OUT/risk-register.csv`.
- **control-mapper** reads `$OUT/evidence.md` and writes `$OUT/control-gaps.md`, using the
  frameworks in `operator.md`.

They work from the same evidence and don't depend on each other, so run them at the same time.

## 3. Challenge (1 agent)

Launch **auditor-critic** on `$OUT/`. It writes `$OUT/auditor-review.md`.

## 4. Resolve (you)

For each auditor **exception**, either fix the register or gap file, or record why you
disagree. Never drop a disagreement silently (steering rule 8). Validate the CSV: header
matches, every row has the same column count, and scores equal L × I.

## 5. Report (you)

Write `$OUT/summary.md` for the operator's audience:

1. **Headline** — two or three sentences: overall posture and the single most important action.
2. **Risk heat map** — a likelihood × impact grid in markdown, sized to the scale in `operator.md`, with risk IDs in the cells.
3. **Top risks** — a table: ID, title, rating, owner, due date.
4. **Systemic control gaps** — taken from the control gap file.
5. **Auditor opinion** — the opinion, how each exception was resolved, and any open disagreements.
6. **Next steps** — decisions the operator needs to make, such as risk acceptance or owner assignment.
7. **Package contents** — links to the other files.

Finish by giving the operator the path to `summary.md` and the top three risks.

## 6. Spoken briefing (offer)

Offer the operator a spoken briefing. If they accept, follow the `/brief` skill on `$OUT`.
