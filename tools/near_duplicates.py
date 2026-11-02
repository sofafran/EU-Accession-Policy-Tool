#!/usr/bin/env python3
"""Find registered sources whose texts are near-duplicates of each other (PC-03, PC-17; ALN-0023).

Exact file duplicates are caught by the fingerprint at stage 2. This check catches what the fingerprint
cannot: two versions of one document (for example the Commission and Council versions of a screening
report) registered as separate sources. It compares the converted texts of sources of the same country
by overlapping eight-word sequences and writes every pair above the thresholds to a CSV for the G2
package. It reads only; deciding that two sources are versions of one document stays with the agent
(tier 1 for exact duplicates) or the analyst."""

import argparse
import re
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import SOURCE_ID_RE, nfc, project_root, read_csv, text_path_for, write_csv  # noqa: E402

__version__ = "1.0.0"
SHINGLE = 8
JACCARD = 0.4       # share of word sequences the two texts have in common (calibrated on RUN-2026-01: the known version pair scored 0.51)
CONTAINMENT = 0.6   # or share of the shorter text found in the longer one (known pair 0.68; template-based payment decisions about 0.64, so expect some pairs to dismiss)
MIN_SHINGLES = 50   # texts shorter than this are too short to compare reliably
MARKER = re.compile(r"^=== (PAGE \d+|SECTION: .*) ===$")
WORD = re.compile(r"\w+", re.UNICODE)


def shingles(text):
    words = []
    for line in text.splitlines():
        if not MARKER.match(line.strip()):
            words += WORD.findall(nfc(line).lower())
    return {zlib.crc32(" ".join(words[i:i + SHINGLE]).encode("utf-8")) for i in range(max(len(words) - SHINGLE + 1, 0))}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0] + " Writes review/<run>/near_duplicates.csv.")
    p.add_argument("--run", required=True, help="run ID, for the report folder")
    p.add_argument("--country", help="compare only sources of this country code")
    p.add_argument("--sources", default="", help="comma-separated source IDs to check against all others of their country (default: all pairs)")
    p.add_argument("--jaccard", type=float, default=JACCARD, help=f"report pairs at or above this Jaccard similarity (default {JACCARD})")
    p.add_argument("--containment", type=float, default=CONTAINMENT, help=f"or at or above this containment of the shorter text (default {CONTAINMENT})")
    p.add_argument("--output", help="CSV to write (default review/<run>/near_duplicates.csv)")
    p.add_argument("--root", help="project root (default: the folder above tools/)")
    p.add_argument("--version", action="version", version=__version__)
    a = p.parse_args(argv)
    root = project_root(a.root)
    _, reg = read_csv(root / "registers" / "source_register.csv")
    focus = {s.strip() for s in a.sources.split(",") if s.strip()}
    texts, missing = {}, []
    for r in reg:
        sid = r.get("source_id", "")
        m = SOURCE_ID_RE.match(sid)
        if not m or (a.country and m.group(1) != a.country):
            continue
        path = text_path_for(root, sid)
        if not path.exists():
            missing.append(sid)
            continue
        sh = shingles(path.read_text(encoding="utf-8"))
        if len(sh) >= MIN_SHINGLES:
            texts[sid] = (m.group(1), sh, r)
    rows = []
    ids = sorted(texts)
    for i, x in enumerate(ids):
        for y in ids[i + 1:]:
            if texts[x][0] != texts[y][0] or (focus and not ({x, y} & focus)):
                continue
            sx, sy = texts[x][1], texts[y][1]
            inter = len(sx & sy)
            if not inter:
                continue
            jac = inter / len(sx | sy)
            con = inter / min(len(sx), len(sy))
            if jac >= a.jaccard or con >= a.containment:
                rx, ry = texts[x][2], texts[y][2]
                recorded = rx.get("version_of") == y or ry.get("version_of") == x
                rows.append({"source_a": x, "source_b": y, "title_a": rx.get("title", ""), "title_b": ry.get("title", ""),
                             "jaccard": f"{jac:.2f}", "containment": f"{con:.2f}",
                             "already_recorded": "yes" if recorded else "no",
                             "note": "recorded as a version in the register" if recorded else "check: possible version of the same document"})
    rows.sort(key=lambda r: (r["already_recorded"], -float(r["containment"])))
    out = Path(a.output) if a.output else root / "review" / a.run / "near_duplicates.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    write_csv(out, ["source_a", "source_b", "title_a", "title_b", "jaccard", "containment", "already_recorded", "note"], rows)
    new = sum(r["already_recorded"] == "no" for r in rows)
    print(f"near_duplicates {__version__}: {len(texts)} source text(s) compared; {len(rows)} pair(s) above the thresholds, {new} not yet recorded; wrote {out}")
    if missing:
        print(f"no text file for {len(missing)} registered source(s), not compared: {', '.join(missing[:10])}{' ...' if len(missing) > 10 else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
