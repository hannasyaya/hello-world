# Mini Kai: a multi-agent GRC assistant

Mini Kai is a small, readable version of Daniel Miessler's *Personal AI Infrastructure* (PAI),
set up for **governance, risk and compliance** work. It is just files. Claude Code reads them
when you open this repo.

| PAI idea | Where it lives here | What it does |
|---|---|---|
| Identity and context | `CLAUDE.md`, `.claude/kai/context/` | Who Kai works for, the risk method, and the steering rules |
| Specialist agents | `.claude/agents/*.md` | Evidence collector, risk assessor, control mapper, auditor-critic, policy writer |
| Skills | `.claude/skills/*/SKILL.md` | `/assess`, `/policy`, `/interview`, `/brief` |
| Voice | `.claude/kai/voice/` | `/brief` turns a report into a spoken MP3 with one voice per agent. It uses Piper, which runs offline, so report text never goes to an outside service. |
| Hooks | `.claude/settings.json`, `.claude/kai/hooks/` | Scope guard, audit log, session briefing |
| Rules of engagement | `.claude/kai/scope.txt` | Targets that may be scanned or probed |
| Outputs | `kai-reports/<date>-<slug>/` | Evidence, risk register (CSV), control gaps, auditor review, summary |

## How `/assess` flows

```
            ┌────────────────────┐
 target ──▶ │ evidence-collector │ ──▶ evidence.md
            └────────────────────┘
                     │
         ┌───────────┴───────────┐        (in parallel)
         ▼                       ▼
 ┌───────────────┐       ┌────────────────┐
 │ risk-assessor │       │ control-mapper │
 └───────────────┘       └────────────────┘
  risk-register.csv        control-gaps.md
         └───────────┬───────────┘
                     ▼
            ┌────────────────┐
            │ auditor-critic │ ──▶ auditor-review.md
            └────────────────┘
                     ▼
         Kai resolves exceptions ──▶ summary.md
```

## Try it

```text
/interview                                   # personalize operator.md
/assess contoso AI agents simulation         # full assessment of the SC-500 lab
/policy standard for AI agent identities     # governance doc grounded in that assessment
```

## Customize

- **Add a framework:** list it in `context/operator.md`. The control-mapper uses whatever is listed there.
- **Add an agent:** copy any file in `.claude/agents/`, then change `name`, `description` and the prompt.
  The `description` tells Kai when to use that agent.
- **Change the risk method:** edit `context/operator.md`. The risk-assessor and the session briefing both follow it.
- **Rules of engagement:** add authorized targets to `scope.txt`. Scanners pointed anywhere else are blocked.

The guard hook prevents mistakes. It is **not** a security boundary.
