---
name: verify-data
description: Strict anti-hallucination protocol for scientific data extraction, experimental logs, and bibliography verification. Prevents dummy numbers and fabricated citations in Q1 IEEE/Elsevier manuscripts.
---

# Zero-Hallucination & Grounded Verification Protocol (`/verify-data`)

## 1. Core Mandate: Epistemic Honesty Over Completion

You are operating under a **Strict Closed-World Assumption** for all experimental numbers, primary study attributes, mathematical bounds, and bibliographic references.

**Golden Rule:** An incomplete sentence or table cell marked with an explicit missing-data flag is infinitely better than a plausible-sounding fabricated number or citation. You are strictly forbidden from guessing, interpolating, extrapolating, or generating "dummy/example" values when reading papers, CSVs, logs, or `.bib` files.

---

## 2. Hard Rules Against Numerical & Experimental Hallucination

### A. Zero-Fabrication of Metrics & Hyperparameters
1. **Never Invent Missing Metrics:** If the user asks you to report Accuracy, Dice, HD95, F1, $p$-values, FLOPs, Parameters, VRAM, or inference latency, you must locate the exact string in the attached workspace files (`.md`, `.csv`, `.json`, `.tex`, `.pdf`, or terminal logs).
2. **Mandatory Fallback Tag (`[MISSING_IN_SOURCE]`):** If a requested metric, sample size ($N$), or hyperparameter (learning rate, batch size, optimizer, epoch count, LoRA rank $r$) is not explicitly present in the provided files, you **MUST** output:
   * In prose: `[MISSING_IN_SOURCE: specify metric/value needed]`
   * In Markdown/LaTeX tables: `NR` (Not Reported) or `[MISSING: metric]`
3. **No Silent Unit Conversion or Rounding Assumptions:**
   * Do not convert MACs to FLOPs, or milliseconds to FPS, unless you state the exact formula used inline.
   * Preserve the exact decimal precision reported in the raw log or source table (e.g., if the log says `0.894`, do not write `89.42%`).

### B. Source Provenance Binding (Where Did This Number Come From?)
Whenever you extract or synthesize numbers from experimental logs or primary SLR papers, you must internally bind every number to its exact source location (Filename + Line/Table/Row).
* If two files in the workspace contain conflicting numbers for the same experiment (e.g., `results_v1.csv` says `88.1%` and `draft_notes.md` says `89.0%`), **DO NOT pick one silently**. Flag the conflict immediately in the text: `[CONFLICT: 88.1% in results_v1.csv vs 89.0% in draft_notes.md]`.

---

## 3. Hard Rules Against Reference & Citation Hallucination

Reference hallucination occurs in two ways: **(1) Ghost Citations** (inventing a non-existent paper or BibTeX key) and **(2) Misattributed Claims** (attaching a real citation key from the user's `.bib` file to a technical claim that paper never made). Both are strictly banned.

### A. Whitelist-Only Citation Keys
1. **Strictly Bound to Workspace Bibliography:** You may only cite keys that literally exist inside the user's attached `.bib` file, Markdown reference list, or SLR extraction table.
2. **Never Guess Author-Year Keys:** Never invent keys like `\cite{smith2023vision}` or `[@wang2024medical]` based on your pre-training memory.
3. **Mandatory Placeholder for Unverified Claims:** If a sentence requires a citation (e.g., a baseline comparison, dataset origin, or prior clinical finding) and no matching entry exists in the workspace files, output:
   * `\cite{CITATION_NEEDED: brief description of required paper}` or `[CITATION_NEEDED: topic]`.

### B. Claim-to-Citation Fidelity (Preventing Misattribution)
1. **Verify Before Grouping:** In SLR or Related Work sections, never pad a citation bracket (e.g., `[12, 15, 19, 24]`) just to make the synthesis look dense. Only include a citation key in a bracket if the provided extraction table or paper summary explicitly confirms that specific study uses that exact mechanism or dataset.
2. **Never Extrapolate Paper Details from Titles Alone:** If the `.bib` file or Markdown note only contains a paper's **title** (without abstract or extracted data columns), do not guess its dataset, sample size, or quantitative performance. Mark those attributes as `NR (Title/BibTeX only)`.

---

## 4. Subgroup Math & PRISMA Arithmetic Verification

LLMs frequently hallucinate arithmetic when summing SLR subgroups or ablation tables.
1. **Explicit Sum Checks:** Whenever reporting PRISMA counts or SLR subgroup proportions ($n/N$), verify that the subgroup counts sum to the stated total $N$, and calculate the exact percentage:
   $$\text{Percentage} = \left(\frac{n}{N}\right) \times 100\%$$
2. **Never Force-Fit Percentages:** If the user's table has 35 rows, do not write *"70% of the 35 studies ($n=25$)"* because $25 / 35 = 71.4\%$. Always compute the exact ratio.

---

## 5. Agent Execution Protocol for `/verify-data`

When invoked via `/verify-data` (either before or after `/anti-slop` / `/anti-slop-slr`), execute these exact steps:

1. **Automated Pre-Check (Citations, Labels, Placeholders, Numeric Parity):**
   * Run [verify_grounding.py](./scripts/verify_grounding.py) (`python <skill_dir>/scripts/verify_grounding.py <draft> [--bib <refs.bib>] [--baseline <orig>]`) to automatically detect ghost keys, dangling `\ref`/`\label` pointers, open quarantine placeholders, and numeric deltas on edited lines.
2. **Cross-Check Active Manuscript Against Source Files:**
   * Scan every numerical value, metric, sample size ($N$), hyperparameter, and citation key in the target `.md` or `.tex` draft against the raw data files (`.csv`, `.json`, `.bib`, extraction tables) provided in the context.
3. **Quarantine Unverified Numbers & Citations In-Place:**
   * Replace any ungrounded/guessed number in the editor with `[MISSING_IN_SOURCE: ...]` and any unverified citation key with `[CITATION_NEEDED: ...]`.
4. **Print Provenance & Hallucination Audit Table in Chat Panel:**
   * Output a structured verification table in the assistant chat window (NOT inside the manuscript file):

| Claim / Metric / Citation in Draft | Status (`VERIFIED` / `UNVERIFIED` / `CONFLICT`) | Exact Source Location (File + Line/Row) | Action Taken |
| :--- | :--- | :--- | :--- |
| e.g., Dice $89.4\%$ on BraTS | `VERIFIED` | `logs/eval_summary.csv` (Row 4, Col 3) | Kept intact |
| e.g., Inference time $14\text{ ms}$ | `UNVERIFIED` | Not found in workspace files | Replaced with `[MISSING_IN_SOURCE: latency]` |
| e.g., `\cite{chen2024swin}` | `GHOST_KEY` | Absent from `references.bib` | Replaced with `\cite{CITATION_NEEDED: Swin baseline}` |
