# ScholarRigor Agent Instructions (`AGENTS.md`)

This repository provides scientific writing, Turnitin stylometry auditing, Systematic Literature Review (SLR) synthesis, and zero-hallucination verification skills compatible with **Google Antigravity**, **OpenAI Codex**, **Claude Code**, **Cursor**, **Gemini CLI**, and any `SKILL.md`-compliant agent.

## Core Grounding Rules

- Operate under a strict closed-world assumption: never invent metrics, hyperparameters, dataset sizes, URLs, or BibTeX citation keys.
- When data or references are absent from workspace files, insert `[MISSING_IN_SOURCE: ...]` or `\cite{CITATION_NEEDED: ...}` instead of fabricating plausible values.
- Follow the full zero-hallucination rules in `rules/AGENTS.md`.

## Available Skills

- `skills/anti-slop/SKILL.md`: Rewrite or draft Q1 IEEE/Elsevier research manuscripts (`.tex` / `.md`) while eliminating LLM cliches, repeated binary contrasts (`whereas/while`), and uniform 250-word windows.
- `skills/anti-slop-slr/SKILL.md`: Synthesize Systematic Literature Reviews (`PRISMA 2020`) from extraction sheets using `(n/N, %)` subgroup counts rather than chronological lists.
- `skills/verify-data/SKILL.md`: Audit drafts against experimental logs, CSVs, and `.bib` files.

## Verification Scripts

- `python skills/anti-slop/scripts/extract_turnitin.py <report.pdf> --full`
- `python skills/anti-slop/scripts/stylometry_audit.py <draft.tex|md> [--baseline <orig>]`
- `python skills/verify-data/scripts/verify_grounding.py <draft.tex|md> --bib <refs.bib> [--baseline <orig>]`
