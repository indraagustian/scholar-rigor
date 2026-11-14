---
name: anti-slop-slr
description: Write, synthesize, or rewrite Systematic Literature Review (SLR / PRISMA 2020) Markdown (.md) and LaTeX (.tex) drafts to Q1 IEEE/Elsevier standards with <20% Turnitin/iThenticate AI detection score and strict zero-hallucination guardrails.
---

# Q1 Systematic Literature Review Anti-Slop Workflow (`/anti-slop-slr`)

## 1. Why SLR Manuscripts Trigger High AI Detection Scores (And How to Fix It)

Systematic Literature Reviews (SLRs) suffer from the highest false-positive and true-positive AI detection rates on Turnitin and iThenticate. When summarizing 30 to 150 primary studies, standard LLMs fall into **repetitive study-by-study templates** (*"Author [X] proposed a [Model] for [Task], achieving [Metric]..."*) and **symmetric taxonomy descriptions**.

Human Q1 survey authors do not write annotated bibliographies; they write **cross-study comparative syntheses** anchored in exact cohort sizes ($N$), subgroup ratios ($n/N$), architectural bottlenecks, and methodological discrepancies across papers. You must enforce these exact human synthesis traits in every paragraph.

---

## 2. Hard Lexical Purge for Literature Reviews (Zero-Tolerance)

### A. Banned Survey Verbs & Phrases
* **BANNED:** *delve (into), underscore, showcase, highlight, harness, leverage, utilize, facilitate, bolster, spearhead, foster, bridge the gap, pave the way, shed light on, elucidate, unpack, navigate, streamline, revolutionize, garner significant attention, witness a surge, attract considerable interest, a growing body of literature, remains in its infancy.*
* **USE INSTEAD:** *group, stratify, benchmark, contrast, isolate, restrict, omit, overfit, under-sample, converge, diverge, trade off, bound, fine-tune, freeze, quantize.*
* **Rule on "Utilize/Leverage/Harness":** Replace with **"use"** or **"adopt"** 90% of the time, or name the exact mechanism (*"condition on," "tokenize," "pre-train," "cross-attend"*).

### B. Banned Adjectives, Adverbs & Nouns
* **BANNED ADJECTIVES/ADVERBS:** *pivotal, crucial, paramount, intricate, nuanced, multifaceted, comprehensive, holistic, exhaustive, robust (unless quantifying noise/perturbation), seamless, cutting-edge, groundbreaking, transformative, meticulous, commendable, notable, remarkably, significantly (unless paired with a $p$-value or effect size).*
* **BANNED NOUNS:** *tapestry, realm, landscape, paradigm, beacon, testament, cornerstone, interplay, synergy, plethora, myriad, dearth, array of, suite of, trajectory, proliferation.*

### C. Transition Word Quota
* **Strict Cap:** Maximum **1 occurrence per 500 words** combined for: *Moreover, Furthermore, Additionally, Consequently, Subsequently, Notably, Importantly, Crucially, Intriguingly, Specifically.*
* **Replacement Strategy:** Link sentences via **taxonomic handoffs** (*"Within this frozen-backbone subgroup..."*, *"Unlike the zero-shot protocols above..."*, *"That supervision bottleneck..."*) or sharp contrasts (*Yet, Still, Instead, In contrast, Even so*).

---

## 3. Syntactic De-Patterning (Eliminating LLM Survey Templates)

You are strictly forbidden from generating the following eight syntactic patterns:

1. **The Annotated Bibliography / "Author-First Laundry List":**
   * Never write paragraphs where consecutive sentences start with *"Smith et al. [12] proposed... Similarly, Jones et al. [13] developed..."*. Group citations by **mechanical family, supervision regime, or clinical bottleneck**.
2. **The Trailing Participial Clause (`", thereby / thus / ultimately + V-ing"`):**
   * Split into a direct causal sentence or active verb clause backed by extracted metrics.
3. **The `"Despite [Noun], [Clause]"` Introductory Formula:**
   * State the technical bottleneck directly as the subject of the sentence.
4. **The `"Not Only ... But Also ..."` Symmetry:**
   * Replace with direct active trade-offs.
5. **Table-Echoing Prose ("As shown in Table X..."):**
   * Never narrate extraction tables row-by-row. Cite the table in parentheses `(Table 3)` and analyze cross-column distributions, skewed ratios, and outliers.
6. **Generic "Future Work" Platitudes at Section Ends:**
   * Replace generic calls for *"more robust and interpretable models"* with concrete, testable evaluation protocols (e.g., patient-level splitting, external multi-center validation).
7. **Repeated Binary Contrast (`"... , whereas / while ..."`):**
   * Never stack balanced two-half contrasts across consecutive synthesis paragraphs. Limit `whereas`/`while` contrast templates to once per subsection; alternate with subgroup distributions (`n/N`), failure-mode clustering, or direct causal dependencies.
8. **Cookie-Cutter Short-Aphorism Openers (`"<Concept> alone <verb> <object>."`):**
   * Never open adjacent synthesis paragraphs with standalone 6–11 word abstract slogans lacking subgroup counts or citations followed immediately by a 30-word complex sentence.

---

## 4. Burstiness & Rhythm Engineering (Natural Cadence Diversity)

Synthesis paragraphs must preserve human unpredictability across ~250-word Turnitin windows:

1. **No Uniform Neighbours:** Never write 3 consecutive sentences whose word counts fall within $\pm 4$ words of each other.
2. **No Rigid Paragraph Silhouettes:** Avoid repeating the same `[short aphorism -> long multi-clause synthesis]` skeleton across adjacent paragraphs. Mix organic mid-length (`14–22` words) empirical findings with earned short verdicts (`6–12` words, grounded in `n/N` counts or dataset facts) and dense comparative sentences (`26–40` words).
3. **Proportional Subgroup Grounding ($n/N$):** Anchor trends in the reviewed literature with exact study counts and percentages: e.g., `($n = 14/38, 36.8\%$)`.
4. **Rolling Window Awareness:** See [Turnitin calibration notes](../anti-slop/references/turnitin_lessons.md) when resolving persistent multi-paragraph flags.

---

## 5. Strict Anti-Hallucination Guardrail for SLR Data & Citations

SLR manuscripts are highly vulnerable to LLM fabrication when summarizing large extraction tables. You must obey these four grounding rules without exception:

1. **Zero Fabricated Subgroup Counts or Metrics:** Compute $n/N$ and percentages strictly from the rows present in the user's attached extraction table, CSV, or notes. If the exact count is not available in the workspace, output `($n = [\text{MISSING\_COUNT}]/N$)`—never invent a plausible ratio.
2. **Zero Ghost Citations:** Only cite keys (`[@key]`, `[12]`, `\cite{...}`) that literally exist in the user's `.bib` file or extraction table. Never pull external papers from your pre-training memory into the PRISMA synthesis unless explicitly instructed.
3. **Strict Claim-to-Row Fidelity (No Citation Padding):** Never group a citation key into a cluster bracket (e.g., `[12, 15, 19]`) unless the extraction table explicitly confirms that specific row/paper shares that exact attribute. If a paper's row lists an attribute as `NR` or blank, do not guess it from the paper's title.
4. **Missing Attribute Flag:** If you need a specific data point from a primary study (e.g., sample size, dataset name, or metric) that is not recorded in the user's notes, insert `[MISSING_IN_TABLE: Study X metric]` rather than guessing.

---

## 6. Agent Tool-Assisted Execution Protocol

When invoked via `/anti-slop-slr`, execute the following workflow:

1. **Turnitin Report Extraction (When AI Report PDF Provided):**
   * Run [extract_turnitin.py](../anti-slop/scripts/extract_turnitin.py) to extract the page-2 AI percentage and highlighted synthesis blocks before rewriting.
2. **Markdown-to-LaTeX Readiness:**
   * Write and edit strictly in clean academic Markdown (`.md`) unless the target file is `.tex`.
   * Preserve all verified citation keys, cross-references (`\ref{...}`), Markdown tables, and inline LaTeX math (`$n = 14/42$`, $\kappa = 0.84$, $\mathcal{O}(N^2)$).
3. **Direct In-Place File Editing:**
   * Apply the generated or rewritten synthesis directly to the active `.md` or `.tex` file (or selected lines), smoothing ~250-word rolling windows when revising flagged literature blocks.
4. **Local Stylometry & Parity Verification:**
   * Run [stylometry_audit.py](../anti-slop/scripts/stylometry_audit.py) (`python <skills_root>/anti-slop/scripts/stylometry_audit.py <target> [--baseline <orig>]`) to catch lingering binary-contrast clusters, repetitive openers, banned survey phrases, or lost citations.
5. **Chat Panel Audit Report (Do NOT write this inside the manuscript file):**
   * After verifying with `stylometry_audit.py`, print a concise verification block in the chat window:
     * **SLR Slop Purged:** List banned survey clichés, `whereas/while` chains, and "Author-first" laundry-list sentences removed.
     * **Synthesis & Citation Density:** Total verified citations synthesized + number of subgroup proportions ($n/N$) calculated from source tables.
     * **Burstiness & Window Audit:** Shortest/longest sentence word count, global variance, and rolling-window check from `stylometry_audit.py`.
     * **Hallucination Check:** Confirm `0 ghost citations; 0 dummy metrics` + list any `[MISSING_IN_TABLE]` flags inserted.
     * **Residual AI Risk:** Report remaining local stylometry flags or pending Turnitin re-check (`Low (<15%)` vs `Moderate`).
