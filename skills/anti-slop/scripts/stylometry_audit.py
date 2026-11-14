"""Audit academic .tex or .md manuscripts for AI slop, templates, and window rhythm.

Usage:
    python stylometry_audit.py <manuscript.tex|md> [--baseline <orig.tex|md>] [--window 250]
"""

import argparse
import difflib
import os
import re
import statistics

BANNED_VERBS = [
    r"\bdelve(?:s|d|ing)?\b", r"\bunderscore(?:s|d|ing)?\b", r"\bshowcase(?:s|d|ing)?\b",
    r"\bhighlight(?:s|ed|ing)?\b", r"\bharness(?:es|ed|ing)?\b", r"\bleverage(?:s|d|ing)?\b",
    r"\butilize(?:s|d|ing)?\b", r"\bfacilitate(?:s|d|ing)?\b", r"\bbolster(?:s|ed|ing)?\b",
    r"\bspearhead(?:s|ed|ing)?\b", r"\bfoster(?:s|ed|ing)?\b", r"\bbridge the gap\b",
    r"\bpave the way\b", r"\bshed light on\b", r"\belucidate(?:s|d|ing)?\b",
    r"\bunpack(?:s|ed|ing)?\b", r"\bnavigate(?:s|d|ing)?\b", r"\bstreamline(?:s|d|ing)?\b",
    r"\brevolutionize(?:s|d|ing)?\b", r"\bunleash(?:es|ed|ing)?\b", r"\bgrapple(?:s|d|ing)? with\b",
    r"\bgarner significant attention\b", r"\bwitness(?:es|ed)? a surge\b",
    r"\battract(?:s|ed)? considerable interest\b", r"\bremains in its infancy\b",
]

BANNED_ADJ_ADV = [
    r"\bpivotal\b", r"\bcrucial\b", r"\bparamount\b", r"\bintricate\b", r"\bnuanced\b",
    r"\bmultifaceted\b", r"\bcomprehensive\b", r"\bholistic\b", r"\bexhaustive\b",
    r"\brobust\b", r"\bseamless\b", r"\bcutting-edge\b", r"\bgroundbreaking\b",
    r"\btransformative\b", r"\bmeticulous\b", r"\bcommendable\b", r"\bnotable\b",
    r"\bremarkably\b", r"\bsignificantly\b",
]

BANNED_NOUNS = [
    r"\btapestry\b", r"\brealm\b", r"\blandscape\b", r"\bparadigm\b", r"\bbeacon\b",
    r"\btestament\b", r"\bcornerstone\b", r"\bbottleneck\b", r"\binterplay\b",
    r"\bsynergy\b", r"\bplethora\b", r"\bmyriad\b", r"\bdearth\b", r"\barray of\b",
    r"\bsuite of\b", r"\btrajectory\b", r"\bproliferation\b",
]

QUOTA_TRANSITIONS = [
    r"\bmoreover\b", r"\bfurthermore\b", r"\badditionally\b", r"\bconsequently\b",
    r"\bsubsequently\b", r"\bnotably\b", r"\bimportantly\b", r"\bcrucially\b",
    r"\bintriguingly\b", r"\bspecifically\b",
]

FORMULAIC_STARTS = (
    "in addition,", "on the other hand,", "to address", "however,", "moreover,",
    "furthermore,", "additionally,", "consequently,", "subsequently,", "notably,",
    "importantly,", "specifically,", "instead,", "instead of ", "despite ",
    "under ", "even with ", "across all ", "answering ", "because ", "as a result,",
)

NON_PARTICIPIAL_ING = {
    "during", "including", "using", "regarding", "concerning", "according",
    "everything", "something", "nothing", "anything", "thing", "string",
    "ring", "wing", "king", "spring", "bring", "meaning", "setting",
    "encoding", "decoding", "embedding", "grounding", "hedging", "pooling",
    "gating", "weighting", "padding", "learning", "training", "testing",
    "imaging", "vignetting", "flattening", "conditioning", "tracking",
    "indexing", "reasoning", "segmenting", "clustering", "scaling", "lighting",
    "bridging", "sampling", "tokenizing", "prompting",
}

ABBRS = ("Fig.", "et al.", "vs.", "e.g.", "i.e.", "No.", "Dr.", "Sec.", "Tab.", "Eq.")


def extract_prose_paragraphs(text, is_tex):
    """Extract clean prose blocks (line_no, raw_text) skipping tables/math/code."""
    lines = text.splitlines()
    if is_tex:
        has_start = any(
            (r"\begin{abstract}" in ln or r"\maketitle" in ln or r"\begin{document}" in ln)
            for ln in lines
        )
        started = not has_start
        skip_env = None
        blocks = []
        for idx, raw in enumerate(lines, 1):
            s = raw.strip()
            if not started:
                if r"\begin{abstract}" in s or r"\maketitle" in s or (
                    r"\begin{document}" in s
                    and not any((r"\begin{abstract}" in ln or r"\maketitle" in ln) for ln in lines)
                ):
                    started = True
                    if r"\begin{abstract}" not in s:
                        continue
                else:
                    continue
            if r"\end{document}" in s or r"\bibliography{" in s:
                break
            if skip_env:
                if f"\\end{{{skip_env}}}" in s:
                    skip_env = None
                continue
            for env in ("table", "table*", "figure", "figure*", "equation", "equation*", "align", "align*", "thebibliography", "IEEEkeywords"):
                if f"\\begin{{{env}}}" in s and f"\\end{{{env}}}" not in s:
                    skip_env = env
                    break
            if skip_env or not s or s.startswith("%"):
                continue
            if re.match(r"^\\(?:begin|end|section|subsection|subsubsection|title|author|maketitle|IEEE|thanks|centering|includegraphics|vspace|label)\b", s):
                continue
            if not s.startswith("\\") or s.startswith("\\item") or s.startswith("\\textbf"):
                blocks.append((idx, s))
        return blocks

    blocks = []
    in_code = False
    buf, start_ln = [], None
    for idx, raw in enumerate(lines, 1):
        s = raw.strip()
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code or s.startswith("#") or s.startswith("|") or re.match(r"^[-*]{3,}$", s):
            if buf:
                blocks.append((start_ln, " ".join(buf)))
                buf, start_ln = [], None
            continue
        if not s:
            if buf:
                blocks.append((start_ln, " ".join(buf)))
                buf, start_ln = [], None
            continue
        if start_ln is None:
            start_ln = idx
        buf.append(s)
    if buf:
        blocks.append((start_ln, " ".join(buf)))
    return blocks


def clean_for_words(s):
    """Normalize LaTeX/Markdown markup for accurate word and sentence inspection."""
    s = re.sub(r"\\caption\{", "", s)
    s = re.sub(r"\\cite\{[^}]*\}", "", s)
    s = re.sub(r"\\(?:eq)?ref\{[^}]*\}", "1", s)
    s = re.sub(r"\\item\s*", "", s)
    s = re.sub(r"\\(?:textbf|textit|texttt|emph)\{([^}]*)\}", r"\1", s)
    s = s.replace("~", " ").replace("``", '"').replace("''", '"').replace("\\%", "%")
    s = re.sub(r"\$[^$]*\$", " MATH ", s)
    s = re.sub(r"`[^`]+`", " CODE ", s)
    s = s.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip()


def split_sentences(text):
    t = text.strip()
    if t.startswith("\\caption{") and t.endswith("}"):
        t = t[len("\\caption{"):-1]
    for abbr in ABBRS:
        t = t.replace(abbr, abbr.replace(".", "<DOT>"))
    t = re.sub(r"(\d)\.(\d)", r"\1<DOT>\2", t)
    t = t.replace("?''", "<QMARK>").replace('?"', "<QDQUOTE>")
    parts = re.split(r'(?<=[.!?])(?:\'\'|\")?\}?\s+(?=[A-Z0-9\\`(\[])', t)
    return [
        p.replace("<DOT>", ".").replace("<QMARK>", "?''").replace("<QDQUOTE>", '?"').strip()
        for p in parts
        if p.strip()
    ]


def word_count(sent):
    cleaned = clean_for_words(sent)
    return len([w for w in cleaned.split() if re.search(r"[A-Za-z0-9]", w)])


def audit_manuscript(path, baseline_path=None, window_words=250):
    with open(path, encoding="utf-8") as f:
        text = f.read()

    is_tex = path.lower().endswith(".tex")
    blocks = extract_prose_paragraphs(text, is_tex)
    prose_joined = "\n".join(clean_for_words(b) for _, b in blocks)
    total_words = len(prose_joined.split())

    print(f"=== STYLOMETRY & ANTI-SLOP AUDIT: {os.path.basename(path)} ===")
    print(f"Prose blocks analyzed: {len(blocks)} | Approx body words: {total_words}")

    # 1. Lexical Slop & Transition Quota
    for label, pats in [
        ("Banned verbs/phrases", BANNED_VERBS),
        ("Banned adj/adv", BANNED_ADJ_ADV),
        ("Banned nouns", BANNED_NOUNS),
    ]:
        hits = [(p, len(re.findall(p, prose_joined, re.I))) for p in pats if re.search(p, prose_joined, re.I)]
        print(f"  {label:22s}: {hits if hits else '0 hits'}")

    trans_hits = []
    trans_total = 0
    for p in QUOTA_TRANSITIONS:
        cnt = len(re.findall(p, prose_joined, re.I))
        if cnt:
            trans_hits.append((p.strip(r"\b"), cnt))
            trans_total += cnt
    allowed = max(1, total_words // 500)
    print(f"  Quota transitions     : {trans_total} (limit <=1 per 500w = {allowed}) {trans_hits}")
    em_dashes = len(re.findall(r"---|\u2014", text))
    print(f"  Em-dashes             : {em_dashes}")

    # 2. Paragraph-level & Template Audit
    all_wcs = []
    sent_records = []  # (line_no, wc, clean_text, has_binary_contrast)
    short_openers = []
    silhouette_streak = 0

    print("\n=== TEMPLATE & RHYTHM WARNINGS BY BLOCK ===")
    warnings_found = 0
    for ln, raw in blocks:
        sents = split_sentences(raw)
        wcs = [word_count(s) for s in sents]
        all_wcs.extend(wcs)
        block_flags = []

        # Uniform 3-consecutive +-4w
        for idx in range(len(wcs) - 2):
            win3 = wcs[idx:idx+3]
            if max(win3) - min(win3) <= 4 and win3[0] >= 10:
                block_flags.append(f"3-uniform-sents={win3}")

        # Aphorism opener + Punch-Long silhouette streak
        first_clean = clean_for_words(sents[0]) if sents else ""
        is_aphorism_open = (
            len(wcs) >= 2
            and 5 <= wcs[0] <= 11
            and not re.search(r"\d", first_clean)
            and wcs[1] >= 24
        )
        if is_aphorism_open:
            short_openers.append((ln, wcs[:2], first_clean))
            silhouette_streak += 1
            if silhouette_streak >= 2:
                block_flags.append(f"consecutive-punch-long-opener(streak={silhouette_streak})")
        else:
            silhouette_streak = 0

        binary_contrast_cnt = 0
        for s_idx, (s, s_wc) in enumerate(zip(sents, wcs), 1):
            c = clean_for_words(s)
            cl = c.lower()
            has_bin = bool(re.search(r",\s+(?:whereas|while)\s+", cl))
            if has_bin:
                binary_contrast_cnt += 1
            sent_records.append((ln, s_wc, c, has_bin))

            if cl.startswith("despite "):
                block_flags.append(f"S{s_idx}:despite-formula")
            if re.search(r"\bnot only\b.+\bbut also\b", cl):
                block_flags.append(f"S{s_idx}:not-only-but-also")
            for fs in FORMULAIC_STARTS:
                if cl.startswith(fs):
                    block_flags.append(f"S{s_idx}:formula-start('{fs.strip()}')")
                    break
            for m in re.finditer(r",\s+(?:thereby\s+|thus\s+|ultimately\s+)?([a-z]+ing)\b", c):
                tok = m.group(1).lower()
                if tok not in NON_PARTICIPIAL_ING or any(adv in m.group(0).lower() for adv in ("thereby", "thus", "ultimately")):
                    block_flags.append(f"S{s_idx}:trailing-participial('{m.group(0).strip()}')")

        if binary_contrast_cnt >= 2:
            block_flags.append(f"repeated-binary-contrast(x{binary_contrast_cnt})")

        if block_flags:
            warnings_found += 1
            print(f"  L{ln:3d} wcs={wcs}: {', '.join(block_flags)}")

    if not warnings_found:
        print("  Clean: no paragraph-level template or uniformity warnings.")

    # 3. Rolling Window Analysis (~250 words, stride 125)
    print(f"\n=== ROLLING {window_words}-WORD WINDOW AUDIT ===")
    hot_windows = 0
    idx = 0
    while idx < len(sent_records):
        w_sum, end = 0, idx
        while end < len(sent_records) and w_sum < window_words:
            w_sum += sent_records[end][1]
            end += 1
        win = sent_records[idx:end]
        if len(win) >= 5:
            win_wcs = [r[1] for r in win]
            win_var = statistics.variance(win_wcs)
            bin_cnt = sum(1 for r in win if r[3])
            short_cnt = sum(1 for w in win_wcs if w <= 11)
            flags = []
            if win_var < 55.0:
                flags.append(f"low-var={win_var:.1f}")
            if bin_cnt >= 3:
                flags.append(f"binary-contrast-cluster={bin_cnt}")
            if short_cnt >= 5 and (short_cnt / len(win_wcs)) >= 0.42 and max(win_wcs) >= 28:
                flags.append(f"punch-heavy={short_cnt}/{len(win_wcs)}")
            if flags:
                hot_windows += 1
                print(f"  Lines L{win[0][0]}–L{win[-1][0]} ({w_sum}w, {len(win)} sents, var={win_var:.1f}): {', '.join(flags)}")
        if end >= len(sent_records):
            break
        # advance ~half window
        adv, step_w = idx, 0
        while adv < end and step_w < window_words // 2:
            step_w += sent_records[adv][1]
            adv += 1
        idx = max(adv, idx + 1)

    if not hot_windows:
        print("  No hot rolling windows detected.")

    if len(all_wcs) > 1:
        short_p = sum(1 for w in all_wcs if w <= 12) / len(all_wcs) * 100
        mid_p = sum(1 for w in all_wcs if 13 <= w <= 25) / len(all_wcs) * 100
        long_p = sum(1 for w in all_wcs if w >= 26) / len(all_wcs) * 100
        print(
            f"\nGlobal cadence ({len(all_wcs)} sents): mean={statistics.mean(all_wcs):.1f}w, "
            f"var={statistics.variance(all_wcs):.1f}, sd={statistics.stdev(all_wcs):.1f} | "
            f"<=12w:{short_p:.0f}% 13-25w:{mid_p:.0f}% >=26w:{long_p:.0f}%"
        )

    # 4. Optional baseline diff check
    if baseline_path:
        with open(baseline_path, encoding="utf-8") as bf:
            b_lines = bf.read().splitlines()
        t_lines = text.splitlines()
        if len(b_lines) == len(t_lines):
            chg = [i for i, (a, b) in enumerate(zip(b_lines, t_lines), 1) if a != b]
            print(f"\nBaseline parity ({os.path.basename(baseline_path)}): {len(chg)}/{len(t_lines)} lines changed -> {chg}")
        else:
            sm = difflib.SequenceMatcher(None, b_lines, t_lines)
            ops = sum(1 for tag, *_ in sm.get_opcodes() if tag != "equal")
            print(f"\nBaseline diff: {len(b_lines)} -> {len(t_lines)} lines ({ops} diff hunks)")


def main():
    parser = argparse.ArgumentParser(description="Audit academic draft for AI slop and stylometric windows.")
    parser.add_argument("manuscript", help="Path to .tex or .md file.")
    parser.add_argument("--baseline", default=None, help="Optional original draft to list modified lines.")
    parser.add_argument("--window", type=int, default=250, help="Rolling window size in words (default: 250).")
    args = parser.parse_args()
    audit_manuscript(args.manuscript, baseline_path=args.baseline, window_words=args.window)


if __name__ == "__main__":
    main()
