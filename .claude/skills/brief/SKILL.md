---
name: brief
description: Turn a Kai report into a short spoken MP3 briefing, with a different voice for each agent, and send it to the operator to play on their phone. Uses Piper offline text-to-speech, so report text never leaves the machine. Use when the operator says "/brief", "audio briefing", "read it to me" or "voice summary", and offer it at the end of /assess.
argument-hint: [report folder, default: newest in kai-reports/]
---

# /brief — spoken executive briefing

Report: **$ARGUMENTS** (if empty, use the newest folder in `kai-reports/`)

## 1. Write the script for the ear

Read the report's `summary.md` (and `auditor-review.md` for the opinion). Write
`<report folder>/briefing.txt`. The operator's audience is executives (see `operator.md`), so
the briefing is what a board member would want to hear in the car.

Format: paragraphs separated by a blank line. Each new speaker starts with a tag from
`.claude/kai/voice/voices.json`, such as `[kai]` or `[auditor-critic]`.

Structure (150–220 words in total, under 90 seconds):
1. `[kai]` One-sentence headline, then what it means for the organization: patient care,
   services, personal data, public trust.
2. `[kai]` The top three risks. Say each one plainly, as cause and consequence, in one sentence.
3. `[risk-assessor]` One sentence on the overall numbers, e.g. "Twelve risks: five high, seven medium."
4. `[auditor-critic]` The audit opinion, and anything still open, in one or two sentences.
5. `[kai]` The decisions needed, with dates. Close with "Full report is in the app."

Rules for spoken text:
- No tables, bullets, markdown, file names or URLs.
- Say risk IDs only when someone will need them, written as "R 2", not "R-02".
- Write dates the way you'd say them, e.g. "by Monday the sixteenth of November".
  Round numbers ("about a third").
- Use short sentences. One idea per sentence.
- Don't include personal names or identifiers (steering rule 7). Use roles instead.

## 2. Render

```bash
python3 .claude/kai/voice/kai_brief.py <report folder>/briefing.txt --title "<report title>"
```

The first run installs Piper and downloads the voices (about 60 MB each, cached in
`~/.cache/kai-voices`). Later runs take seconds.

## 3. Deliver

Send `<report folder>/briefing.mp3` to the operator with SendUserFile, with a one-line
caption giving the length and the headline. Commit `briefing.txt`. The MP3 is git-ignored,
because it can be rebuilt from the script.
