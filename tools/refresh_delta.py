#!/usr/bin/env python3
"""Refresh helper (decision E18): list what a newly extracted source adds to the issues already judged, so the agent can
propose links and re-judge only the affected issues. Reads only; writes one review spreadsheet (CSV). Adds no analysis:
the columns `proposed_link_type`, `proposed_effect` and `note` are left blank for the agent to fill and the analyst to review.

Usage: python3 tools/refresh_delta.py --sources MKD-EU-2026-0NN [MKD-EU-2026-0NN ...] [--run RUN-2026-01]
Output: review/<run>/refresh/refresh_delta.csv (one row per in-scope item of the new sources), and a summary on screen.
"""

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_outputs import load  # noqa: E402
from common import project_root, split_list  # noqa: E402

__version__ = "1.0.0"
COLS = ["item_id", "source_id", "chain_link", "reform_issue_ids", "summary", "earlier_items_same_issue_and_link",
        "current_direction", "current_priority", "current_gap", "proposed_link_type", "proposed_effect", "note"]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sources", nargs="+", required=True)
    p.add_argument("--run", default="RUN-2026-01")
    p.add_argument("--root", default=None)
    p.add_argument("--version", action="version", version=__version__)
    a = p.parse_args(argv)
    root = Path(a.root) if a.root else project_root()
    D = load(root, a.run)
    J = {}
    for j in D["js"]:
        J[(j["object_id"], j["judgement_type"])] = j
    new = [k for k, i in D["items"].items() if i["_source"] in a.sources]
    if not new:
        sys.exit("no evidence items found for " + ", ".join(a.sources) + ": extract the source first")
    rows, issues, unmatched, oos = [], Counter(), [], 0
    for k in sorted(new):
        i = D["items"][k]
        if i["pass2"]["classification_status"] == "out_of_scope":
            oos += 1
            continue
        xs = i["pass2"]["reform_issue_ids"]
        if not xs:
            unmatched.append(k)
        earlier = []
        for x in xs:
            issues[x] += 1
            earlier += [e for e in D["by"].get(x, []) if e not in new and D["items"][e]["pass2"]["chain_link"] == i["pass2"]["chain_link"]
                        and (D["items"][e]["dates"].get("publication_date") or "") >= "2024"]
        g = lambda t: "; ".join(f"{x}: {J.get((x + '@MKD', t), {}).get('value', '')}" for x in xs)
        rows.append({"item_id": k, "source_id": i["_source"], "chain_link": i["pass2"]["chain_link"], "reform_issue_ids": ";".join(xs),
                     "summary": i["summary"], "earlier_items_same_issue_and_link": ";".join(sorted(set(earlier))),
                     "current_direction": g("direction_of_travel"), "current_priority": g("priority"), "current_gap": g("unresolved_gap"),
                     "proposed_link_type": "", "proposed_effect": "", "note": "" if xs else "no matching issue: check the unmatched queue"})
    out = root / "review" / a.run / "refresh" / "refresh_delta.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, COLS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(new)} items in {', '.join(a.sources)}: {len(rows)} in scope, {oos} out of scope, {len(unmatched)} with no matching issue")
    print(f"issues touched ({len(issues)}): " + ", ".join(f"{x} ({n})" for x, n in sorted(issues.items())))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
