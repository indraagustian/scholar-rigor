---
description: Verify all manuscript metrics, subgroup arithmetic, and citations against workspace logs, CSV tables, and .bib files.
---

Read and follow the complete instructions in `skills/verify-data/SKILL.md` (or `~/.claude/skills/verify-data/SKILL.md` / `~/.codex/skills/verify-data/SKILL.md`).

Run `python <skill_dir>/scripts/verify_grounding.py` first when available, quarantine unverified numbers with `[MISSING_IN_SOURCE: ...]` and unverified citations with `[CITATION_NEEDED: ...]`, and print the provenance audit table.

Task details: $ARGUMENTS
