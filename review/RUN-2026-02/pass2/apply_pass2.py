#!/usr/bin/env python3
"""Apply pass 2 classifier outputs to RUN-2026-02 items (stage 9 helper, tier 1).
Writes the pass2 block of this run's items only, the file's classification record, and new rows in the
unmatched and ambiguous queues. Usage: apply_pass2.py BATCH [BATCH ...] (names in review/RUN-2026-02/pass2/output)."""
import csv, glob, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from common import run_items, read_csv, write_csv
RUN, D = "RUN-2026-02", ROOT / "review" / "RUN-2026-02" / "pass2"
LINKS = {"eu_requirement", "country_response", "implementation", "outcome", "unresolved_gap", "lesson"}
STAT = {"auto", "queued_ambiguous", "queued_unmatched", "out_of_scope"}
approved = {r["issue_id"] for r in read_csv(ROOT / "taxonomy" / "reform_issues.csv")[1] if r["status"] == "approved"}
mechs = {r["mechanism_id"] for r in read_csv(ROOT / "taxonomy" / "mechanisms.csv")[1] if r["status"] == "approved"}
out = {}
for b in sys.argv[1:]:
    inp = [r["item_id"] for r in read_csv(D / "input" / f"{b}.csv")[1]]
    rows = read_csv(D / "output" / f"{b}.csv")[1]
    got = [r["item_id"] for r in rows]
    if sorted(got) != sorted(inp):
        sys.exit(f"{b}: output items differ from input (missing {sorted(set(inp) - set(got))[:5]}, extra {sorted(set(got) - set(inp))[:5]})")
    for r in rows:
        ri = [x.strip() for x in r["reform_issue_ids"].split(";") if x.strip()]
        me = [x.strip() for x in r["mechanism_ids"].split(";") if x.strip()]
        bad = [x for x in ri if x not in approved] + [x for x in me if x not in mechs]
        if bad or r["chain_link"] not in LINKS or r["classification_status"] not in STAT or len(ri) > 3 or len(me) > 3:
            sys.exit(f"{b} {r['item_id']}: invalid row {bad or (r['chain_link'], r['classification_status'])}")
        out[r["item_id"]] = {**r, "_ri": ri, "_me": me}
uq_h, uq = read_csv(ROOT / "taxonomy" / "unmatched_queue.csv")
aq_h, aq = read_csv(ROOT / "taxonomy" / "ambiguous_queue.csv")
open_uq = {q["item_id"] for q in uq if q["status"] == "open"}
open_aq = {q["item_id"] for q in aq if q["status"] == "open"}
nu, na = max(int(q["queue_id"]) for q in uq) + 1, max(int(q["queue_id"]) for q in aq) + 1
applied = 0
for f in sorted(glob.glob(str(ROOT / "evidence" / "*" / "*.json"))):
    d = json.load(open(f, encoding="utf-8"))
    mine = [it for it in run_items(d, RUN) if it["item_id"] in out]
    if not mine:
        continue
    assert d["extraction"]["run_id"] == RUN and d["classification"].get("run_id") == RUN, f
    for it in mine:
        r = out[it["item_id"]]
        keep_ints = (it.get("pass2") or {}).get("intervention_ids") or []
        it["pass2"] = {"chain_link": r["chain_link"], "reform_issue_ids": r["_ri"], "mechanism_ids": r["_me"], "intervention_ids": keep_ints,
                       "classification_status": r["classification_status"], "classification_note": r["classification_note"] or None}
        applied += 1
        if r["classification_status"] == "queued_unmatched" and it["item_id"] not in open_uq:
            uq.append({"queue_id": str(nu), "item_id": it["item_id"], "proposed_label": r["proposed_label"] or "None proposed",
                       "proposed_definition": r["proposed_definition"] or "Item fits no issue; see note.", "similar_issue_ids": r.get("candidate_issue_ids", ""),
                       "status": "open", "resolution": f"RUN-2026-02 stage 9 proposal for G5: {r['classification_note']}", "gate_id": ""})
            nu += 1; open_uq.add(it["item_id"])
        if r["classification_status"] == "queued_ambiguous" and it["item_id"] not in open_aq:
            aq.append({"queue_id": str(na), "item_id": it["item_id"], "candidate_issue_ids": r["candidate_issue_ids"] or ";".join(r["_ri"]),
                       "agent_reasoning": r["classification_note"], "status": "open", "resolution": "", "gate_id": ""})
            na += 1; open_aq.add(it["item_id"])
    allmine = run_items(d, RUN)
    done = all((it.get("pass2") or {}).get("classification_status", "not_classified") != "not_classified" for it in allmine)
    d["classification"] = {"status": "complete" if done else "partial", "run_id": RUN, "rules_version": "0.4", "taxonomy_version": "1.2",
                           "classified_at": "2026-11-05", "mechanisms_version": "1.0"}
    with open(f, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2); fh.write("\n")
write_csv(ROOT / "taxonomy" / "unmatched_queue.csv", uq_h, uq)
write_csv(ROOT / "taxonomy" / "ambiguous_queue.csv", aq_h, aq)
print(f"applied {applied} of {len(out)}; unmatched rows to {nu - 1}, ambiguous rows to {na - 1}")
