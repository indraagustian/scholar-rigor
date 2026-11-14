---
description: Rewrite or draft Q1 academic LaTeX/Markdown manuscripts without AI slop, synthetic cadence, or hallucinated data.
---

Read and follow the complete instructions in `skills/anti-slop/SKILL.md` (or `~/.claude/skills/anti-slop/SKILL.md` / `~/.codex/skills/anti-slop/SKILL.md`).

If a Turnitin AI PDF report is provided, extract flagged spans first via `python <skill_dir>/scripts/extract_turnitin.py <report.pdf> --full`. After editing, verify stylometry, 250-word rolling windows, and citation/number parity with `python <skill_dir>/scripts/stylometry_audit.py` and `verify_grounding.py`.

Task details: $ARGUMENTS
