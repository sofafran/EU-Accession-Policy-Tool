#!/usr/bin/env python3
"""Stage 10 tier 2 ratings for RUN-2026-02 by the written rules (judgement rules 0.5 section 3, Codebook 6), as in RUN-2026-01:
evidence confidence for every in-scope item and relevance for every item-issue pair. Writes proposed rows to judgements/judgements.csv
(CRLF, appended). Reason wording follows the alpha's validated templates. Usage: tier2_ratings.py [--dry-run]"""
import csv, json, glob, sys
from pathlib import Path
from collections import Counter
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from common import run_items
RUN = "RUN-2026-02"
LV = {"High": 3, "Medium": 2, "Low": 1}; NM = {3: "High", 2: "Medium", 1: "Low"}
sq = {}
for r in csv.DictReader(open(ROOT / "judgements/source_quality.csv")):
    if r["review_status"] in ("validated", "overridden", "proposed") and r["overall"] in LV:
        sq[(r["source_id"], r["topic"])] = r["overall"]
links = [l for l in csv.DictReader(open(ROOT / "links/links.csv", newline="")) if l["review_status"] != "rejected"]
corr, contested = {}, {}
for l in links:
    if l["link_type"] == "corroborates":
        corr.setdefault(l["from_id"], set()).add(l["to_id"]); corr.setdefault(l["to_id"], set()).add(l["from_id"])
    if l["link_type"] == "contradicts" and l["review_status"] == "validated":
        contested.setdefault(l["from_id"], set()).add(l["to_id"]); contested.setdefault(l["to_id"], set()).add(l["from_id"])

def topic_rating(src, it):
    th = it.get("themes") or []
    if it.get("chapter") == "02" and not th:
        order = ["02", "TECH"]
    else:
        order = sorted({t for t in th if (src, t) in sq}) + ["TECH", "02"]
    for t in order:
        if (src, t) in sq:
            return sq[(src, t)]
    return None

rows, stats = [], Counter()
for f in sorted(glob.glob(str(ROOT / "evidence/*/*.json"))):
    d = json.load(open(f, encoding="utf-8"))
    src = d["source_id"]
    for it in run_items(d, RUN):
        p = it["pass2"]
        if p["classification_status"] == "out_of_scope":
            continue
        iid = it["item_id"]; flags = set(it.get("flags") or [])
        s = topic_rating(src, it)
        if s is None:
            stats["no_rating"] += 1
            s = "Medium"; head = "Rated {v} because the source has no quality rating for this topic, so it is treated as Medium"
        elif s == "High":
            head = "Rated {v} because the source is rated High for this topic and the claim is stated directly"
        else:
            head = f"Rated {{v}} because the source is rated {s} for this topic"
        lvl = LV[s]; buts, semis = [], []
        is_corr = bool(corr.get(iid))
        if "reported_view" in flags:
            lvl = min(lvl, 2); buts.append("it reports another party's view")
        if "regional" in flags:
            lvl = min(lvl, 2); buts.append("it is a regional claim that does not name the country")
        if iid in contested:
            lvl = min(lvl, 2); buts.append("it is contested by " + ", ".join(sorted(contested[iid])))
        if it.get("machine_translated"):
            lvl = min(lvl, 2); semis.append("it relies on machine translation, so it is capped at Medium")
        if flags & {"hedged", "ocr"}:
            if is_corr:
                semis.append("the text is uncertain but the claim is corroborated")
            else:
                lvl = max(1, lvl - 1); semis.append("the text is hedged, or comes from text recognition or a garbled passage, and the claim is uncorroborated")
        if s == "Medium" and is_corr and lvl == 2 and not buts and not semis:
            lvl = 3; semis.append("it is corroborated by independent evidence")
        v = NM[lvl]
        reason = head.format(v=v)
        if buts:
            reason += (", but " if s == "High" else "; ") + "; ".join(buts)
        if semis:
            reason += "; " + "; ".join(semis)
        reason += "."
        cites = [iid] + sorted(contested.get(iid, set()))
        rows.append(("evidence_confidence", iid, "", v, reason, ";".join(cites)))
        stats["conf_" + v] += 1
        ri = p["reform_issue_ids"]; note = (p.get("classification_note") or "").lower()
        loose = any(k in note for k in ("awkward fit", "partial fit", "moderate fit", "loose fit"))
        for k, issue in enumerate(ri):
            if k == 0 and not loose:
                rv, rr = "High", "It concerns the same country and is classified first to this issue."
            elif k == 0:
                rv, rr = "Medium", "It concerns the same country, but the classification notes a loose fit to this issue."
            else:
                rv, rr = "Medium", "It concerns the same country and bears on this issue as a secondary, adjacent fit."
            if "regional" in flags and rv == "High":
                rv, rr = "Medium", "It is a regional claim that does not name the country, so it concerns the same issue in a group of comparable countries."
            rows.append(("relevance", iid, issue, rv, rr, iid)); stats["rel_" + rv] += 1
print(dict(stats), len(rows))
if "--dry-run" in sys.argv:
    sys.exit()
jp = ROOT / "judgements/judgements.csv"
raw = open(jp, newline="").read()
h = raw.split("\r\n", 1)[0].split(",")
n = max(int(l.split(",", 1)[0][4:]) for l in raw.split("\r\n")[1:] if l.startswith("JDG-"))
first = n + 1
with open(jp, "a", newline="") as fh:
    w = csv.DictWriter(fh, h, lineterminator="\r\n")
    for t, oid, ctx, v, reason, ev in rows:
        n += 1
        w.writerow({"judgement_id": f"JDG-{n:06d}", "judgement_type": t, "object_type": "item", "object_id": oid, "context_id": ctx, "value": v,
                    "reason": reason, "evidence_item_ids": ev, "made_by": "agent", "review_status": "proposed", "rereview_flag": "", "reviewer": "",
                    "review_date": "", "override_reason": "", "supersedes": "", "codebook_version": "1.3", "rules_version": "0.5",
                    "taxonomy_version": "1.3", "run_id": RUN})
print(f"JDG-{first:06d} to JDG-{n:06d}")
