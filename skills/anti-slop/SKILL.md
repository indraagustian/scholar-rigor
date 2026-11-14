---
name: anti-slop
description: Write or rewrite academic Markdown (.md) and LaTeX (.tex) drafts to Q1 IEEE/Elsevier standards with <20% Turnitin/iThenticate AI detection score and strict zero-hallucination guardrails.
---

# Q1 Scientific Paper Anti-Slop & Humanization Workflow (`/anti-slop`)

## 1. Objective & Core Philosophy

Academic AI detectors (Turnitin AI, iThenticate, GPTZero) evaluate statistical predictability through **Perplexity** (token choice predictability within a given context) and **Burstiness** (variance in sentence length, clause depth, and syntactic rhythm).

Standard LLMs default to smooth, symmetrical, hedged, and transition-heavy prose. Human Q1 researchers write with **dense technical specificity, asymmetric sentence lengths, direct causal claims, and candid methodological trade-offs**. You must enforce these exact human traits in every output.

---

## 2. Hard Lexical Purge (Zero-Tolerance Vocabulary)

### A. Banned Verbs (Never Use)
* **BANNED:** *delve (into), underscore, showcase, highlight, harness, leverage, utilize, facilitate, bolster, spearhead, foster, bridge the gap, pave the way, shed light on, elucidate, unpack, navigate, streamline, revolutionize, unleash, grapple with.*
* **USE INSTEAD:** *measure, quantify, isolate, constrain, regularize, decouple, approximate, prune, sample, project, compute, observe, degrade, converge, diverge, bottleneck, trade off, omit, bound.*
* **Rule on "Utilize/Leverage/Harness":** Replace with **"use"** 90% of the time, or specify the exact operation (*"apply," "adopt," "convolve," "concatenate," "condition on"*).

### B. Banned Adjectives & Adverbs (Never Use)
* **BANNED:** *pivotal, crucial, paramount, intricate, nuanced, multifaceted, comprehensive, robust (unless mathematically defined via perturbation bounds), seamless, cutting-edge, state-of-the-art (limit to max 1 per section; use SOTA or name the exact baseline), groundbreaking, transformative, meticulous, commendable, notable, remarkably, significantly (unless backed by a $p$-value or confidence interval).*
* **USE INSTEAD:** *sensitive, invariant, ill-posed, under-constrained, sparse, dense, intractable, marginal, negligible, empirical, heuristic, deterministic, stochastic.*

### C. Banned Nouns & Metaphors (Never Use)
* **BANNED:** *tapestry, realm, landscape, paradigm, beacon, testament, cornerstone, bottleneck (allowed only when referring to tensor dimensions or hardware I/O), interplay, synergy, plethora, myriad, dearth, array of, suite of.*

### D. Transition Word Quota
* **Strict Cap:** Maximum **1 occurrence per 500 words** combined for: *Moreover, Furthermore, Additionally, Consequently, Subsequently, Notably, Importantly, Crucially, Intriguingly, Specifically.*
* **Replacement Strategy:** Connect sentences through **semantic handoffs** (repeating or pronominalizing the core noun/variable from the end of Sentence A at the beginning of Sentence B) or use simple, sharp connectors: *Yet, Still, Instead, In contrast, Even so, Because of this.*

---

## 3. Syntactic De-Patterning (Eliminating LLM Sentence Templates)

You are strictly forbidden from generating the following seven syntactic structures:

1. **The Trailing Participial Clause (`", thereby / thus / ultimately + V-ing"`):**
   * *Bad:* "The proposed module aggregates multi-scale features, thereby enhancing boundary localization."
   * *Good:* "The module aggregates features across three spatial scales. This sharpens boundary localization and cuts false positives by $14.2\%$."
2. **The `"Not Only ... But Also ..."` Symmetry:**
   * *Bad:* "This approach not only reduces computational overhead but also maintains high accuracy."
   * *Good:* "This approach cuts FLOPs by half without hurting Dice scores."
3. **The `"Despite [Noun], [Clause]"` Introductory Formula:**
   * *Bad:* "Despite significant advancements in vision transformers, deployment on edge devices remains challenging."
   * *Good:* "Vision transformers scale poorly to edge hardware because self-attention grows quadratically with token count $\mathcal{O}(N^2)$."
4. **The "Rule of Three" (Triadic Lists):**
   * Never group generic adjectives, nouns, or verbs in rhetorical threes (*"accurate, scalable, and interpretable"*). Use pairs (2 items), single precise terms, or exhaustive technical lists (4+ specific parameters).
5. **Summarizing Hook Sentences at Paragraph Ends:**
   * Never wrap up paragraphs with philosophical summaries (*"Ultimately, these findings underscore..."*). End paragraphs on **hard data, a mathematical constraint, a citation, or a concrete observation**.
6. **Repeated Binary Contrast (`"... , whereas / while ..."`):**
   * Never stack balanced two-half contrasts across adjacent paragraphs (*"Method A does X, whereas Method B does Y"* in P1, then P2, then P3). Use `whereas`/`while` at most once per subsection; alternate with causal bottlenecks, parenthetical specs, or clustered failure-mode comparisons.
7. **Formulaic Short-Aphorism Openers (`"<Concept> alone <verb> <object>."`):**
   * Never open consecutive paragraphs with standalone 6–11 word abstract slogans lacking numbers, symbols, or citations (e.g., *"Pixel grids alone hide metric spatial coordinates."*) followed immediately by a 30-word complex sentence. Short sentences work best mid-paragraph or closing a point on an empirical fact, not as a uniform opener.

---

## 4. Burstiness & Rhythm Engineering (Natural Cadence Diversity)

Academic detectors score **250-word rolling windows**, so forcing every paragraph into the same *Punch-Long-Punch-Long* mold creates a secondary AI signature. Obey these quantitative rules instead:

1. **No Uniform Neighbours:** Never write 3 consecutive sentences whose word counts fall within $\pm 4$ words of each other.
2. **No Rigid Paragraph Silhouettes:** Never repeat the exact same opening rhythm (e.g., `[7–11w opener -> 28–40w multi-clause sentence]`) across consecutive paragraphs. Mix organic mid-length (`14–22` words) causal or numeric sentences with short empirical verdicts (`6–12` words) and dense mechanistic explanations (`26–40` words).
3. **Earned Short Verdicts (`6–12` words):** Place short sentences where a concrete constraint, experimental drop, or dataset boundary justifies the abrupt stop—preferably grounded in numbers, symbols, or proper model names rather than abstract slogans.
4. **Punctuation Diversity:** Use parentheses `(...)` for quick inline parameter specs or quantitative values, and semicolons `;` to join closely coupled independent technical clauses. Cap em-dashes at 1 per page.

---

## 5. Section-Specific Q1 IEEE & Elsevier Guidelines

* **Abstract (150–250 words):** Start directly with the technical problem or physical failure mode. Follow: 1 sentence problem $\rightarrow$ 1 sentence why current methods fail mechanically $\rightarrow$ 2–3 sentences naming your exact method and mathematical components $\rightarrow$ 2 sentences of hard numbers (datasets, sample sizes, exact metric gains, FLOPs/params).
* **Introduction & Related Work:** Group citations by **technical failure mode or mathematical family**, never as a chronological laundry list (*"Smith et al. [1] proposed... Later, Jones et al. [2]..."*) and never by repeating `[Short Claim -> X whereas Y]` across consecutive subsections. Vary how each paragraph enters (quantitative hardware limit, architectural mismatch, loss-function constraint, dataset discrepancy). Keep contribution bullets dry, verifiable, and grounded in architecture or proofs.
* **Methodology:** Bind prose directly to mathematical notation (e.g., $\mathbf{F}_{low} \in \mathbb{R}^{C \times H \times W}$). Explicitly state *why* a hyperparameter or layer was chosen, including what failed during preliminary runs.
* **Experiments & Discussion:** Let numbers lead without self-praise (*"by a large margin"*). Include a candid analysis of failure modes or trade-offs where your model underperforms.
* **250-Word Rolling Window Calibration:** See [Turnitin calibration notes](./references/turnitin_lessons.md). When a second Turnitin pass still flags a short span inside a larger block, audit the entire ~250-word surrounding window so neighboring sentences do not retain conflicting stylistic cadence.

---

## 6. Strict Anti-Hallucination Guardrail (Zero Dummy Data & Zero Ghost Citations)

To achieve high technical specificity without fabricating facts, you must obey these grounding rules:
1. **Never Invent Dummy Numbers:** When writing or rewriting sentences that require quantitative metrics, sample sizes ($N$), hyperparameters, or hardware specs, use **ONLY** numbers explicitly present in the user's draft or attached workspace files. If a number is missing, insert `[MISSING_IN_SOURCE: specify metric]`—never invent a realistic-looking dummy number (e.g., do not make up `-14.2%` or $\tau = 0.07$ unless it is in the user's notes).
2. **Never Fabricate or Misattribute Citations:** Only use citation keys (`[@key]`, `[1]`, `\cite{...}`) that already exist in the user's draft or attached `.bib` file. Never invent author-year keys from pre-training memory. If a claim needs a reference not present in the workspace, insert `\cite{CITATION_NEEDED: topic}`.

---

## 7. Agent Tool-Assisted Execution Protocol

When invoked via `/anti-slop`, execute the following workflow:

1. **Turnitin Report Extraction (When AI Report PDF Provided):**
   * Run [extract_turnitin.py](./scripts/extract_turnitin.py) (`python <skill_dir>/scripts/extract_turnitin.py <report.pdf> --full`) to extract the exact page-2 AI score and page-by-page cyan-highlighted passages before editing.
2. **Markdown-to-LaTeX Readiness:**
   * Write and edit strictly in clean academic Markdown (`.md`) unless the target file is explicitly `.tex`.
   * Preserve all verified citation placeholders, cross-references (`\ref{...}`, `\eqref{...}`), and LaTeX math blocks (`$...$`, `$$...$$`).
3. **Direct In-Place File Editing:**
   * Apply the generated or rewritten text directly to the active file or highlighted selection, inspecting the surrounding ~250-word rolling window when fixing stubbornly flagged blocks.
4. **Local Stylometry & Parity Verification:**
   * Run [stylometry_audit.py](./scripts/stylometry_audit.py) (`python <skill_dir>/scripts/stylometry_audit.py <target> [--baseline <orig>]`) to verify `0` banned lexical items, transition quota compliance, zero Template `1–7` hotspots, no `consecutive-punch-long-opener` or `binary-contrast-cluster` rolling windows, and exact line/citation parity.
5. **Chat Panel Audit Report (Do NOT write this inside the manuscript file):**
   * After verifying with `stylometry_audit.py`, print a concise 5-line verification block in the chat window:
     * **Slop Purged:** List key banned words or LLM syntactic templates removed.
     * **Burstiness & Window Audit:** Report shortest/longest sentence spread, global variance, and rolling-window findings from `stylometry_audit.py`.
     * **Data & Citation Integrity:** Confirm `0 dummy numbers invented; 0 external citations fabricated` + count of `[MISSING_IN_SOURCE]` flags placed for the author to fill.
     * **Compilation & Residual AI Risk:** Report build status (if `.tex`) and remaining local stylometry flags or pending Turnitin re-check (`Low (<15%)` vs `Moderate`).
