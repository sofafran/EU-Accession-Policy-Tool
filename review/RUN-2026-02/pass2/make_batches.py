#!/usr/bin/env python3
"""Write pass 2 input batches for RUN-2026-02 items not yet in any batch (stage 9 helper, tier 1)."""
import csv, glob, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from common import run_items, read_csv
RUN = "RUN-2026-02"
D = ROOT / "review" / RUN / "pass2"
prefix, size = sys.argv[1], int(sys.argv[2])
only = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None
done = set()
for f in (D / "input").glob("*.csv"):
    done |= {r["item_id"] for r in read_csv(f)[1]}
seed = {r["item_id"]: r["issue_ids"] for r in read_csv(ROOT / "review" / RUN / "G4_issue_mapping.csv")[1]}
rows = []
for f in sorted(glob.glob(str(ROOT / "evidence" / "*" / "*.json"))):
    d = json.load(open(f, encoding="utf-8"))
    if only and d["source_id"] not in only:
        continue
    for it in run_items(d, RUN):
        if it["item_id"] in done:
            continue
        rows.append({"item_id": it["item_id"], "family": d["source_id"].split("-")[1], "type": it["information_type"],
                     "text_en": it.get("translation_en") or it["stated_text"], "summary": it.get("summary") or "",
                     "scope_basis": ";".join(it.get("scope_basis") or []), "themes": ";".join(it.get("themes") or []),
                     "chapter": it.get("chapter") or "", "flags": ";".join(it.get("flags") or []), "extraction_note": it.get("extraction_note") or "",
                     "intervention_as_stated": it.get("intervention_as_stated") or "", "stated_status": it.get("stated_status") or "",
                     "g4_seed_issues": seed.get(it["item_id"], "")})
h = list(rows[0].keys()) if rows else []
n = 0
for i in range(0, len(rows), size):
    n += 1
    with open(D / "input" / f"{prefix}{n:02d}.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, h, lineterminator="\n"); w.writeheader(); w.writerows(rows[i:i + size])
print(len(rows), "items in", n, "batches")
