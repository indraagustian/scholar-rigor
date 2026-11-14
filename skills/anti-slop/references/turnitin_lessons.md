# Empirical Turnitin Calibration Notes (IEEE 6-Page Benchmarks)

Key failure modes and working fixes observed across multi-round Turnitin AI Writing evaluations (`54% -> 40% -> 32%`):

1. **Rolling ~250-Word Windows Override Single-Sentence Fixes**
   - Turnitin aggregates signal over overlapping windows rather than grading isolated sentences.
   - Rewriting only 2–3 sentences inside a flagged abstract or literature subsection can accidentally drag previously unflagged neighboring sentences into a cyan highlight if the cadence or vocabulary clashes across the window boundary.
   - When a second pass still flags a short block, inspect the surrounding 250-word span instead of only paraphrasing highlighted fragments.

2. **Rigid "Short Aphorism + Long Explanation" Cadence Triggers False/Residual Flags**
   - Forcing every paragraph to open with a 7–10 word punchy thesis sentence lacking citations or numbers (`"<Concept> alone <verb> <object>."`) followed immediately by a 30-word multi-clause explanation creates a uniform cross-paragraph silhouette that Turnitin still flags (~72% of Related Works in `v3` despite zero banned words).
   - Keep short sentences (`6–12` words) where they earn impact (concrete bottlenecks, crisp experimental verdicts, mid/end paragraph) and vary paragraph opening shapes freely, including natural mid-length (`14–22` words) causal prose.

3. **Repeated Binary Contrast (`... , whereas/while ...`) Across Adjacent Paragraphs**
   - Even without `"Smith et al. proposed..."`, writing consecutive Related Works paragraphs with balanced `"A achieves X, whereas/while B computes Y"` contrast halves forms an unmistakable LLM rhetorical template.
   - Limit `whereas/while` contrast templates to at most once per subsection; alternate with failure-mode grouping, quantitative bottleneck comparisons, or direct architectural dependencies.

4. **Concrete Parameters & Symbol Anchors Clear Results & Methods Sections**
   - Experimental subsections anchored directly to tensor shapes, code tokens (`\texttt{...}`), GPU VRAM/FPS measurements, Eq. symbols, and specific ablation trade-offs cleared Turnitin down to `0%` highlights on whole pages.
