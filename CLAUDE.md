# ScholarRigor Claude Code Instructions (`CLAUDE.md`)

Follow the closed-world scientific verification protocol and load the bundled skills under `skills/` (or `~/.claude/skills/`) when editing manuscripts:

- **`/anti-slop`** (`skills/anti-slop/SKILL.md`): Academic rewriting and Turnitin/iThenticate stylometric hardening for `.tex` and `.md` manuscripts.
- **`/anti-slop-slr`** (`skills/anti-slop-slr/SKILL.md`): Cross-study Systematic Literature Review (PRISMA 2020) synthesis anchored to exact `(n/N, %)` subgroup counts.
- **`/verify-data`** (`skills/verify-data/SKILL.md`): Deterministic citation and numeric audit against workspace logs and `.bib` files.

## Guardrails

1. Never fabricate experimental numbers, statistical tests, or BibTeX keys. Use `[MISSING_IN_SOURCE: ...]` or `\cite{CITATION_NEEDED: ...}` when evidence is missing.
2. When a Turnitin AI PDF report is provided, run `skills/anti-slop/scripts/extract_turnitin.py` first, inspect the ~250-word rolling window around each flagged span, and verify edits with `skills/anti-slop/scripts/stylometry_audit.py` and `skills/verify-data/scripts/verify_grounding.py`.
3. Never report compilation or audits as passing without running them after your final edit.
