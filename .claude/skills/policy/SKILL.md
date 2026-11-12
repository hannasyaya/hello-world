---
name: policy
description: Draft a governance document (policy, standard, procedure, remediation plan or risk-acceptance memo) from a completed Kai assessment in kai-reports/. Use when the operator says "/policy", "draft a policy", "write a standard" or "remediation plan".
argument-hint: <document type and topic, e.g. "standard for AI agent identities">
---

# /policy — governance document from an assessment

Request: **$ARGUMENTS**

1. Find the assessment to ground the document in. Use the folder the operator named, or else
   the newest folder in `kai-reports/`. If there is none, say so and suggest running
   `/assess` first. Don't write a policy that isn't grounded in an assessment.
2. Launch the **policy-writer** agent. Give it:
   - the document type and topic
   - the paths to `risk-register.csv`, `control-gaps.md` and `auditor-review.md`
   - the output path: `<that folder>/policy-<slug>.md`
3. Check the draft. Every requirement should be testable and traced to a risk or a gap.
   Fix anything that isn't.
4. Give the operator the file path and the open decisions.
