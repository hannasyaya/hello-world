---
name: interview
description: Personalize Kai by interviewing the operator about their role, frameworks, risk method, risk appetite and audience, then updating .claude/kai/context/operator.md. Use on first run or when the operator says "/interview" or "update my profile".
---

# /interview — personalize Kai

1. Read `.claude/kai/context/operator.md`. Note every field marked `_(to confirm)_` or left blank.
2. Ask the operator about those fields, **at most 4 questions at a time**. Use the
   AskUserQuestion tool where the answer is a choice. Cover:
   - Role and sector, and any regulators that apply (for example DORA, HIPAA, PCI DSS, the EU AI Act)
   - Frameworks used day to day, and which one is primary
   - Risk method (scale, thresholds) and risk appetite
   - Report audience and preferred format
   - Recurring work Kai could take over (for example, quarterly access reviews or vendor assessments)
3. Rewrite `operator.md` with the answers. Keep it short: bullets only, nothing over a line or two.
4. Don't record personal identifiers such as full name, email or employer, unless the operator
   explicitly asks you to.
5. Suggest one new skill or agent that would help with the recurring work they described.
