# ScholarRigor Gemini CLI Instructions (`GEMINI.md`)

When editing scientific papers, literature reviews, or verification scripts in this project, enforce closed-world anti-hallucination rules (`rules/AGENTS.md`) and use the ScholarRigor workflows/tools:

- **`skills/anti-slop/SKILL.md`** (`/anti-slop`): Q1 IEEE/Elsevier academic writing and Turnitin AI reduction without synthetic burstiness or `whereas/while` chains.
- **`skills/anti-slop-slr/SKILL.md`** (`/anti-slop-slr`): PRISMA 2020 comparative literature synthesis grounded to exact extraction rows and `(n/N, %)` ratios.
- **`skills/verify-data/SKILL.md`** (`/verify-data`): Citation and metric provenance auditing.

Run local verification helpers before finishing any manuscript edit:
- `python skills/anti-slop/scripts/extract_turnitin.py <report.pdf> --full`
- `python skills/anti-slop/scripts/stylometry_audit.py <target.tex|md> [--baseline <orig>]`
- `python skills/verify-data/scripts/verify_grounding.py <target.tex|md> --bib <refs.bib> [--baseline <orig>]`
