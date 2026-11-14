"""Extract Turnitin AI Writing Report scores and highlighted passages.

Usage:
    python extract_turnitin.py <report.pdf> [<report2.pdf> ...] [--full] [--page N]
"""

import argparse
import re
import sys

try:
    import pymupdf as fitz
except ImportError:
    print("Error: pymupdf is required (pip install pymupdf).", file=sys.stderr)
    sys.exit(2)

DEFAULT_CYAN_RGB = (0.32, 0.777, 0.855)
HEADER_Y_MIN = 40.0
FOOTER_Y_MAX = 740.0


def _color_distance(c1, c2):
    return sum(abs(a - b) for a, b in zip(c1, c2))


def _is_highlight_fill(fill, target_rgb=DEFAULT_CYAN_RGB, tol=0.06):
    if not fill or len(fill) < 3:
        return False
    rgb = tuple(round(float(x), 3) for x in fill[:3])
    return _color_distance(rgb, target_rgb) <= tol


def analyze_report(pdf_path, include_lines=False, page_filter=None):
    """Parse cover metadata, page-2 AI score, and per-page highlighted words."""
    doc = fitz.open(pdf_path)
    cover_text = doc[0].get_text() if len(doc) > 0 else ""
    score_text = doc[1].get_text() if len(doc) > 1 else ""

    score_match = re.search(r"(\d+%|\*+%)\s+detected as AI", score_text)
    ai_score = score_match.group(1) if score_match else "UNKNOWN"
    sub_match = re.search(r"Submission ID\s+([^\s]+)", cover_text)
    word_match = re.search(r"([\d,]+)\s+Words", cover_text)

    total_body = 0
    total_hl = 0
    page_stats = []
    highlighted_pages = {}

    for pno in range(2, len(doc)):
        page_num = pno + 1
        if page_filter and page_num != page_filter:
            continue
        page = doc[pno]
        hl_rects = [
            d["rect"]
            for d in page.get_drawings()
            if _is_highlight_fill(d.get("fill"))
        ]
        p_total = 0
        p_hl = 0
        lines = {}
        for w in page.get_text("words"):
            if w[1] < HEADER_Y_MIN or w[3] > FOOTER_Y_MAX:
                continue
            p_total += 1
            wr = fitz.Rect(w[:4])
            hit = any(
                (not (wr & hr).is_empty and (wr & hr).get_area() > 0.25 * wr.get_area())
                for hr in hl_rects
            )
            if hit:
                p_hl += 1
            lines.setdefault((w[5], w[6]), []).append((w[4], hit))

        total_body += p_total
        total_hl += p_hl
        page_stats.append((page_num, p_hl, p_total))

        if include_lines and p_hl > 0:
            entries = []
            for key in sorted(lines):
                items = lines[key]
                hits = sum(1 for _, h in items if h)
                if hits == 0:
                    continue
                if hits == len(items):
                    entries.append(("ALL", " ".join(t for t, _ in items)))
                else:
                    text = " ".join(f"[{t}]" if h else t for t, h in items)
                    entries.append((f"PART({hits}/{len(items)})", text))
            highlighted_pages[page_num] = entries

    return {
        "path": pdf_path,
        "submission_id": sub_match.group(1) if sub_match else "N/A",
        "declared_words": word_match.group(1) if word_match else "N/A",
        "ai_score": ai_score,
        "body_hl": total_hl,
        "body_total": total_body,
        "page_stats": page_stats,
        "highlighted_pages": highlighted_pages,
    }


def main():
    parser = argparse.ArgumentParser(description="Extract Turnitin AI PDF report highlights.")
    parser.add_argument("pdfs", nargs="+", help="One or more Turnitin AI report PDF paths.")
    parser.add_argument("--full", action="store_true", help="Print highlighted text lines per page.")
    parser.add_argument("--page", type=int, default=None, help="Inspect a single 1-based page number.")
    args = parser.parse_args()

    for idx, pdf in enumerate(args.pdfs):
        res = analyze_report(pdf, include_lines=args.full, page_filter=args.page)
        ratio = (res["body_hl"] / res["body_total"] * 100.0) if res["body_total"] else 0.0
        pages_str = ", ".join(f"p{p}:{h}/{t}" for p, h, t in res["page_stats"])
        if idx > 0:
            print("-" * 72)
        print(
            f"Report: {res['path']}\n"
            f"  Score: {res['ai_score']} detected as AI | ID: {res['submission_id']} | "
            f"Cover words: {res['declared_words']}\n"
            f"  Body highlights: {res['body_hl']}/{res['body_total']} ({ratio:.1f}%) | {pages_str}"
        )
        if args.full:
            for pno, entries in res["highlighted_pages"].items():
                print(f"\n  [Page {pno}]")
                for tag, line_txt in entries:
                    print(f"    {tag:12s}: {line_txt}")


if __name__ == "__main__":
    main()
