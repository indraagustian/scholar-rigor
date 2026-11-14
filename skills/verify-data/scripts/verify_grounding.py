"""Verify citations, cross-references, quarantine tags, and numeric fidelity.

Usage:
    python verify_grounding.py <draft.tex|md> [--bib refs.bib] [--baseline orig.tex|md]
"""

import argparse
from collections import Counter
import os
import re
import sys

QUARANTINE_PATTERNS = [
    r"\[MISSING_IN_SOURCE[^\]]*\]",
    r"\[MISSING_IN_TABLE[^\]]*\]",
    r"\[MISSING:[^\]]*\]",
    r"\[CONFLICT:[^\]]*\]",
    r"\[CITATION_NEEDED[^\]]*\]",
    r"\\cite\{CITATION_NEEDED[^}]*\}",
    r"\[UNVERIFIED_[^\]]*\]",
]


def load_bib_keys(bib_paths):
    keys = set()
    for bp in bib_paths:
        with open(bp, encoding="utf-8") as f:
            keys.update(re.findall(r"@\w+\{\s*([^,\s]+)\s*,", f.read()))
    return keys


def extract_cites(text):
    used = []
    for grp in re.findall(r"\\cite[a-zA-Z]*\{([^}]*)\}", text):
        for k in grp.split(","):
            k = k.strip()
            if k and not k.startswith("CITATION_NEEDED"):
                used.append(k)
    for grp in re.findall(r"\[((?:@[A-Za-z0-9_:-]+(?:\s*;\s*)?)+)\]", text):
        for k in re.findall(r"@([A-Za-z0-9_:-]+)", grp):
            used.append(k)
    return used


def extract_numbers(line):
    return sorted(re.findall(r"(?<![A-Za-z_])([+-]?\d+(?:\.\d+)?%?)", line))


def main():
    parser = argparse.ArgumentParser(description="Verify citations, labels, tags, and numeric fidelity.")
    parser.add_argument("draft", help="Target .tex or .md manuscript.")
    parser.add_argument("--bib", nargs="*", default=[], help="One or more .bib files.")
    parser.add_argument("--baseline", default=None, help="Optional original draft for numeric/ref parity.")
    args = parser.parse_args()

    with open(args.draft, encoding="utf-8") as f:
        text = f.read()

    used_cites = extract_cites(text)
    used_set = set(used_cites)
    print(f"=== GROUNDING AUDIT: {os.path.basename(args.draft)} ===")
    print(f"Citations used: {len(used_cites)} calls ({len(used_set)} unique keys)")

    exit_code = 0
    if args.bib:
        bib_keys = load_bib_keys(args.bib)
        missing = sorted(used_set - bib_keys)
        unused = sorted(bib_keys - used_set)
        print(f"BibTeX keys loaded: {len(bib_keys)} | Missing (ghost) keys: {missing if missing else 'NONE'}")
        if unused:
            print(f"Unused BibTeX keys ({len(unused)}): {unused}")
        if missing:
            exit_code = 1

    if args.draft.lower().endswith(".tex"):
        labels = set(re.findall(r"\\label\{([^}]*)\}", text))
        refs = set(re.findall(r"\\(?:eq)?ref\{([^}]*)\}", text))
        dangling = sorted(refs - labels)
        print(f"LaTeX labels: {len(labels)} | refs: {len(refs)} | Dangling refs: {dangling if dangling else 'NONE'}")
        if dangling:
            exit_code = 1

    # Quarantine tags check
    q_hits = []
    for ln, raw in enumerate(text.splitlines(), 1):
        for pat in QUARANTINE_PATTERNS:
            for m in re.finditer(pat, raw):
                q_hits.append((ln, m.group(0)))
    print(f"Open quarantine placeholders: {len(q_hits)}")
    for ln, tag in q_hits:
        print(f"  L{ln}: {tag}")

    # Baseline numeric & citation parity check
    if args.baseline:
        with open(args.baseline, encoding="utf-8") as bf:
            orig_text = bf.read()
        for kind, fn in [
            ("cites", extract_cites),
            ("refs", lambda t: re.findall(r"\\(?:eq)?ref\{([^}]*)\}", t)),
            ("labels", lambda t: re.findall(r"\\label\{([^}]*)\}", t)),
        ]:
            c_orig = Counter(fn(orig_text))
            c_new = Counter(fn(text))
            if c_orig == c_new:
                print(f"Parity [{kind}]: EXACT MATCH ({sum(c_new.values())})")
            else:
                print(f"Parity [{kind}]: CHANGED | removed={dict(c_orig - c_new)} | added={dict(c_new - c_orig)}")

        o_lines = orig_text.splitlines()
        n_lines = text.splitlines()
        if len(o_lines) == len(n_lines):
            print("\nNumeric delta on modified lines vs baseline:")
            diff_nums = 0
            for idx, (a, b) in enumerate(zip(o_lines, n_lines), 1):
                if a != b:
                    na, nb = extract_numbers(a), extract_numbers(b)
                    if na != nb:
                        diff_nums += 1
                        added = list((Counter(nb) - Counter(na)).elements())
                        removed = list((Counter(na) - Counter(nb)).elements())
                        print(f"  L{idx:3d}: +added={added} | -removed={removed}")
            if diff_nums == 0:
                print("  All modified lines preserve identical numeric tokens.")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
