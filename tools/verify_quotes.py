#!/usr/bin/env python3
"""Check that every quote in an evidence file appears word for word at its cited location."""

import argparse
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (PAGE_RE, SECTION_RE, nfc, project_root, read_json,  # noqa: E402
                    text_path_for, write_json)

__version__ = "1.2.3"


def split_pages(text):
    """Return {page number: [lines]} from a converted text file."""
    pages, current = {}, None
    for line in text.splitlines():
        m = PAGE_RE.match(line)
        if m:
            current = int(m.group(1))
            pages.setdefault(current, [])
        elif current is not None:
            pages[current].append(line)
    return pages


PAGE_NUMBER_RE = re.compile(r"^\s*(page\s+)?\d{1,4}(\s*/\s*\d{1,4})?\s*$", re.I)


FOOTNOTE_RE = re.compile(r"^\s*\d{1,3}\s*\S")


def shape(line):
    """A line with its digits masked, so that headers carrying a page number still count as the same header."""
    line = re.sub(r"\d+", "#", line.strip())
    line = re.sub(r"_+", "_", line)
    return " ".join(line.split())


def boundary_lines(pages):
    """Shapes of lines that recur among the first eight or last three non-empty lines of three or more pages: running headers and footers."""
    from collections import Counter
    seen = Counter()
    for lines in pages.values():
        content = [l.strip() for l in lines if l.strip() and not SECTION_RE.match(l)]
        seen.update({shape(l) for l in content[:8] + content[-3:]})
    return {l for l, n in seen.items() if n >= 3}


def drop_footnotes(lines):
    """Remove a block of footnotes at the foot of a page: from the first footnote-numbered line in the lower part of the page."""
    start = int(len(lines) * 0.5)
    for k in range(start, len(lines)):
        if FOOTNOTE_RE.match(lines[k]) and not PAGE_NUMBER_RE.match(lines[k]):
            return lines[:k]
    return lines


def strip_boundaries(lines, recurring, top, bottom):
    """Remove page numbers and running headers or footers at the top and/or bottom of one page."""
    lines = [l for l in lines if not SECTION_RE.match(l)]

    def junk(l):
        return not l.strip() or PAGE_NUMBER_RE.match(l) or shape(l) in recurring
    if top:
        while lines and junk(lines[0]):
            lines = lines[1:]
    if bottom:
        while lines and junk(lines[-1]):
            lines = lines[:-1]
    return lines


def section_text(lines, heading):
    """Lines under the first section marker whose heading matches, up to the next section marker."""
    want = squash(heading).casefold()
    out, inside = [], False
    for line in lines:
        m = SECTION_RE.match(line)
        if m:
            if inside:
                break
            inside = squash(m.group(1)).casefold() == want
            continue
        if inside:
            out.append(line)
    return out if inside or out else None


def squash(s):
    return " ".join(nfc(s).split())


def variants(block):
    """Two readings of a block: line-break hyphens removed, and kept. Whitespace collapsed in both."""
    joined = nfc("\n".join(block))
    removed = re.sub(r"(?<=\w)-[ \t]*\n[ \t]*(?=\w)", "", joined)
    kept = re.sub(r"(?<=\w)-[ \t]*\n[ \t]*(?=\w)", "-", joined)
    return squash(removed), squash(kept)


def check_item(item, pages):
    loc = item.get("location") or {}
    page, page_end, section = loc.get("page"), loc.get("page_end"), loc.get("section")
    if page is not None:
        wanted = range(page, (page_end or page) + 1)
        missing = [n for n in wanted if n not in pages]
        if missing:
            return False, f"page(s) {missing} not in text file"
        if len(wanted) == 1:
            block = [l for l in pages[page] if not SECTION_RE.match(l)]
        else:
            # A quote that runs over a page break: skip page numbers and running headers or footers between the pages.
            recurring = boundary_lines(pages)
            block, alt = [], []
            for k, n in enumerate(wanted):
                part = strip_boundaries(pages[n], recurring, top=k > 0, bottom=k < len(wanted) - 1)
                block += part
                # Second reading: footnotes at the foot of every page but the last are skipped as well.
                alt += strip_boundaries(drop_footnotes(part), recurring, top=False, bottom=True) if k < len(wanted) - 1 else part
            quote = squash(item.get("stated_text", ""))
            if quote and any(quote in v for v in variants(alt)) and not any(quote in v for v in variants(block)):
                return True, f"found at page {page}-{page_end} (footnotes between the pages skipped)"
        where = f"page {page}" + (f"-{page_end}" if page_end else "")
    elif section:
        block = section_text([l for n in sorted(pages) for l in pages[n]], section)
        if block is None:
            return False, f"section '{section}' not found"
        where = f"section '{section}'"
    else:
        return False, "no page or section cited"
    quote = squash(item.get("stated_text", ""))
    if not quote:
        return False, "empty stated_text"
    if any(quote in v for v in variants(block)):
        return True, f"found at {where}"
    return False, f"not found at {where}"


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Check every stated_text in an evidence file against the converted text of its source: the cited page(s) for paged "
                    "documents, the cited section for webpages. Ignores only whitespace, line-break hyphenation, Unicode normalisation "
                    "(NFC) and, for quotes that run over a page break (page_end), the page numbers, running headers or footers and footnotes between the pages; Latin and Cyrillic look-alike letters are never treated as equal. Sets quote_verified on each item and writes a CSV report.")
    p.add_argument("evidence_files", nargs="+", help="evidence JSON files")
    p.add_argument("--root", help="project root (default: the folder above tools/)")
    p.add_argument("--report-dir", help="folder for reports (default review/<run_id>/quote_checks/)")
    p.add_argument("--dry-run", action="store_true", help="report only; do not change the evidence files")
    p.add_argument("--version", action="version", version=__version__)
    a = p.parse_args(argv)
    root = project_root(a.root)
    failures = 0
    for ef in a.evidence_files:
        data = read_json(ef)
        sid = data["source_id"]
        tpath = text_path_for(root, sid)
        if not tpath.exists():
            print(f"error: {sid}: text file missing at {tpath}", file=sys.stderr)
            failures += len(data.get("items", []))
            continue
        pages = split_pages(tpath.read_text(encoding="utf-8"))
        rows = []
        for item in data.get("items", []):
            ok, detail = check_item(item, pages)
            item["quote_verified"] = ok
            rows.append([item.get("item_id", ""), "pass" if ok else "fail", detail])
            failures += 0 if ok else 1
        if not a.dry_run:
            write_json(ef, data)
        run_id = data.get("extraction", {}).get("run_id", "UNKNOWN")
        rdir = Path(a.report_dir) if a.report_dir else root / "review" / run_id / "quote_checks"
        rdir.mkdir(parents=True, exist_ok=True)
        with (rdir / f"{sid}.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["item_id", "result", "detail"])
            w.writerows(rows)
        passed = sum(r[1] == "pass" for r in rows)
        print(f"{sid}: {passed}/{len(rows)} quotes verified; report {rdir / (sid + '.csv')}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
