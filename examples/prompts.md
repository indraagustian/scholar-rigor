# ScholarRigor Usage Prompts & Workflow Examples

Ready-to-use prompts across supported coding agents and standalone CLI runs.

---

## 1. De-AI Revision Using a Turnitin Report

### Google Antigravity
```text
/anti-slop @turnitin_report.pdf @main.tex @references.bib

Identify every highlighted AI-flagged block from @turnitin_report.pdf, rewrite ONLY those flagged passages in @main.tex using structural burstiness and domain-specific active voice, and preserve all LaTeX commands, equations, labels, and citations untouched.
```

### Claude Code / OpenAI Codex
```text
/anti-slop turnitin_report.pdf main.tex references.bib
```
*(Or via natural-language skill trigger:)*
```text
Run the anti-slop workflow on turnitin_report.pdf and main.tex against references.bib. Do not modify unflagged sections, and print a before/after stylometry summary plus a grounding audit table.
```

### Gemini CLI
```text
/scholar-rigor:anti-slop turnitin_report.pdf main.tex references.bib
```

### Cursor (Chat / Composer)
```text
@manuscript-writing.mdc @turnitin_report.pdf @main.tex @references.bib
Follow the anti-slop skill instructions: extract flagged passages from turnitin_report.pdf, perform a structural rewrite only on flagged blocks in main.tex, and verify citation and metric integrity.
```

---

## 2. Iterative Turnitin Loop (`<20%` Calibration Target)

When an initial Turnitin pass drops from e.g. `58%` to `35%` (remaining uniform clusters):

```text
/anti-slop @turnitin_v2.pdf @main.tex @references.bib

Compare @turnitin_v2.pdf against @main.tex and focus strictly on the remaining flagged blocks. Perform a deep structural rewrite:
1. Merge or split uniform 18-25 word sentences so consecutive sentences contrast sharply (e.g., 7-11 word empirical statements next to 28-40 word mechanistic explanations).
2. Remove formulaic sentence-initial discourse markers ("In addition,", "On the other hand,", "To address this issue,") and link sentences through shared technical nouns or exact quantitative contrasts.
3. Anchor every claim to observed tensor shapes, equations, or measured trade-offs in @main.tex.
4. Confirm with stylometry_audit.py and verify_grounding.py that all citations, labels, and numbers match the original draft.
```

---

## 3. Systematic Literature Review (PRISMA 2020)

```text
/anti-slop-slr @prisma_screening_log.csv @extraction_matrix.csv @references.bib @slr_draft.tex

Draft the Methods (Search Strategy, Inclusion/Exclusion Criteria, PRISMA Flow) and Synthesis sections in @slr_draft.tex strictly from @prisma_screening_log.csv and @extraction_matrix.csv. Flag any missing study counts with [MISSING_IN_SOURCE: ...], cite only BibTeX keys present in @references.bib, and avoid repetitive per-paper summary templates.
```

---

## 4. Pre-Submission Zero-Hallucination Audit

```text
/verify-data @draft_revised.tex @draft_original.tex @references.bib @experiment_results.csv

Audit @draft_revised.tex against @draft_original.tex, @references.bib, and @experiment_results.csv. Verify that no metrics drifted, no LaTeX labels/references broke, and no citation keys were dropped or fabricated.
```

---

## 5. Standalone CLI Scripts (Agent-Free or CI Check)

Run directly from any terminal inside your manuscript repository:

```bash
# 1. Extract Turnitin flagged blocks & score breakdown (optional PyMuPDF dependency)
python path/to/skills/anti-slop/scripts/extract_turnitin.py turnitin_report.pdf --full

# 2. Measure sentence-length std, CV, 16-24w AI plateau, discourse openers, and diff parity
python path/to/skills/anti-slop/scripts/stylometry_audit.py main_revised.tex --baseline main_original.tex --window 250

# 3. Verify LaTeX citations, \label/\ref balance, numbers, and fallback placeholders (stdlib only)
python path/to/skills/verify-data/scripts/verify_grounding.py main_revised.tex --bib references.bib --baseline main_original.tex
```
