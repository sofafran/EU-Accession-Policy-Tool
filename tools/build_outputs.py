#!/usr/bin/env python3
"""Build the stage 12 outputs (procedure P5, Codebook 7) for a run from the project files.

Writes to outputs/<run_id>/: scope_overview.md, one issue_brief_<issue_id>.md per approved reform issue,
coverage_and_limits_report.md and, for run 1b, one comparator_brief_<issue_id>.md per selected issue.
Facts and judgements come only from the registers, evidence files, entities, links and judgements.
Narrative sections are read from review/<run_id>/stage12/narrative/<name>.md, written by the agent and
labelled as such; any evidence item ID they cite is moved to the annex and replaced by a number.
With --factpacks, writes one plain fact pack per issue to review/<run_id>/stage12/factpacks/ instead,
as the input for writing the narrative sections."""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import evidence_files, project_root, read_csv, read_json, split_list  # noqa: E402

VERSION = "1.0.1"
ITEM = re.compile(r"\b[A-Z]{3}-(?:EU|GOV|CSO|IO|RES|MED|INT)-\d{4}-\d{3}-\d{4}\b")
INTV = re.compile(r"\bINT-[A-Z]{3}-\d{4}\b")
ORDER = {"eu_requirement": 0, "country_response": 1, "implementation": 2, "outcome": 3, "unresolved_gap": 4, "lesson": 5}
CHAIN = {"eu_requirement": "EU requirement", "country_response": "Country response", "implementation": "Implementation",
         "outcome": "Outcome", "unresolved_gap": "Unresolved gap", "lesson": "Lesson"}
COUNTRIES = {"ALB": "Albania", "HRV": "Croatia", "MDA": "Moldova", "MNE": "Montenegro", "SRB": "Serbia", "MKD": "North Macedonia"}
DRAFT = ("**Status: {status}.** It uses only judgements validated at G6 (GATE-0007) "
         "and, for comparator material, G6b (GATE-0011). Sections marked *Agent synthesis* are written by the tool from that "
         "material and add no new judgement. Numbers in square brackets refer to the evidence annex at the end.")


class Refs:
    """Numbers evidence items in order of first citation, for one output file."""

    def __init__(self, items):
        self.items, self.order = items, []

    def n(self, k):
        if k not in self.order:
            self.order.append(k)
        return self.order.index(k) + 1

    def sub(self, text, names=None):
        text = ITEM.sub(lambda m: f"[{self.n(m.group(0))}]" if m.group(0) in self.items else m.group(0), text or "")
        if names:
            text = INTV.sub(lambda m: names.get(m.group(0), m.group(0)), text)
        text = re.sub(r"\((\[\d+\](?:[;,] ?\[\d+\])*)\)", lambda m: re.sub(r"[;,] ?", "", m.group(1)), text)
        text = re.sub(r"\](?:[;,] ?|\s(?:and|or)\s)\[", "][", text)
        return text.replace(" ([", " [").replace("]))", "])")

    def annex(self, reg):
        out = ["## Annex: evidence items", "",
               "Each item is quoted word for word from its source. Machine-translated items show the source-language quote and the English "
               "translation, and their evidence confidence is capped at Medium.", ""]
        for k in self.order:
            i = self.items[k]
            s = reg.get(i["_source"], {})
            loc = i["location"]
            where = f"p. {loc['page']}" if loc.get("page") else (loc.get("section") or "")
            title = s.get("title", "")
            q = i["stated_text"].replace("\n", " ").strip()
            line = f"[{self.n(k)}] **{k}**. {s.get('institution', '')}, *{title}* ({i['dates'].get('publication_date') or ''}), {where}. \"{q}\""
            if i.get("machine_translated") and i.get("translation_en"):
                line += f" Machine translation: \"{i['translation_en'].strip()}\""
            out += [line, ""]
        return out


def load(root, run):
    items = {}
    for f in evidence_files(root):
        d = read_json(f)
        for it in d["items"]:
            items[it["item_id"]] = {**it, "_source": d["source_id"]}
    js = read_csv(root / "judgements" / "judgements.csv")[1]
    links = read_csv(root / "links" / "links.csv")[1]
    reg = {r["source_id"]: r for r in read_csv(root / "registers" / "source_register.csv")[1]}
    sq = {}
    for r in read_csv(root / "judgements" / "source_quality.csv")[1]:
        if r["review_status"] in ("validated", "overridden"):
            sq.setdefault(r["source_id"], {})[r["topic"]] = r["overall"]
    issues = [r for r in read_csv(root / "taxonomy" / "reform_issues.csv")[1] if r["status"] == "approved"]
    mech = {r["mechanism_id"]: r["label"] for r in read_csv(root / "taxonomy" / "mechanisms.csv")[1]}
    ints = {r["intervention_id"]: r for r in read_csv(root / "entities" / "interventions.csv")[1]}
    ok = [j for j in js if j["review_status"] in ("validated", "overridden")]
    dups = {l["from_id"] for l in links if l["link_type"] == "same_as_earlier" and reg.get(l["from_id"].rsplit("-", 1)[0], {}).get("version_of")}
    by = {}
    for k, i in items.items():
        if i["country"] != "MKD" or i["pass2"]["classification_status"] == "out_of_scope" or k in dups:
            continue
        for x in i["pass2"]["reform_issue_ids"]:
            by.setdefault(x, []).append(k)
    return dict(items=items, js=ok, links=links, reg=reg, sq=sq, issues=issues, mech=mech, ints=ints, by=by)


def quality(D, k, issue):
    i = D["items"][k]
    q = D["sq"].get(i["_source"], {})
    for t in [*split_list(issue["chapters"]), *split_list(issue["themes"]), "TECH", "02"]:
        if t in q:
            return q[t]
    return next(iter(q.values()), "not rated")


def issue_view(D, issue):
    x, oid = issue["issue_id"], issue["issue_id"] + "@MKD"
    J = {j["judgement_type"]: j for j in D["js"] if j["object_id"] == oid}
    mine = set(D["by"].get(x, []))
    conf = {j["object_id"]: j["value"] for j in D["js"] if j["judgement_type"] == "evidence_confidence"}
    rel = {j["object_id"]: j["value"] for j in D["js"] if j["judgement_type"] == "relevance" and j["context_id"] == x}
    iids = sorted({n for k in mine for n in D["items"][k]["pass2"]["intervention_ids"] if n.startswith("INT-MKD")})
    status = {}
    for j in D["js"]:
        if j["judgement_type"] == "implementation_status" and j["object_id"] in iids:
            if j["object_id"] not in status or j["context_id"] >= status[j["object_id"]]["context_id"]:
                status[j["object_id"]] = j
    outc = []
    for l in D["links"]:
        if l["link_type"] == "leads_to" and l["to_id"] in mine:
            s = next((j for j in D["js"] if j["object_id"] == l["link_id"] and j["judgement_type"] == "success"), None)
            a = next((j for j in D["js"] if j["object_id"] == l["link_id"] and j["judgement_type"] == "attribution"), None)
            outc.append((l, s, a))
    conflicts = [l for l in D["links"] if l["link_type"] == "contradicts" and l["review_status"] == "validated" and (l["from_id"] in mine or l["to_id"] in mine)]
    key = []
    for t in ("unresolved_gap", "direction_of_travel", "priority", "tractability"):
        for k in split_list(J.get(t, {}).get("evidence_item_ids", "")):
            if k in D["items"] and k not in key:
                key.append(k)
    reqs = sorted((k for k in mine if D["items"][k]["pass2"]["chain_link"] == "eu_requirement" and D["items"][k]["_source"].startswith("MKD-EU")),
                  key=lambda k: (D["items"][k]["dates"].get("publication_date") or "", k))
    mt = sum(1 for k in mine if D["items"][k].get("machine_translated"))
    srcs = {D["items"][k]["_source"] for k in mine}
    return dict(J=J, mine=mine, conf=conf, rel=rel, iids=iids, status=status, outc=outc, conflicts=conflicts, key=key, reqs=reqs, mt=mt, srcs=srcs)


def narrative(root, run, name):
    p = root / "review" / run / "stage12" / "narrative" / f"{name}.md"
    if not p.exists():
        return {}
    parts, cur = {}, None
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
            parts[cur] = []
        elif cur:
            parts[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in parts.items()}


def table(head, rows):
    esc = lambda c: str(c).replace("|", "/").replace("\n", " ")
    return ["| " + " | ".join(head) + " |", "|" + "---|" * len(head), *["| " + " | ".join(esc(c) for c in r) + " |" for r in rows], ""]


def names_of(D):
    return {k: v["name"] for k, v in D["ints"].items()}


def issue_brief(root, run, D, issue):
    V, R, names = issue_view(D, issue), Refs(D["items"]), names_of(D)
    x, J = issue["issue_id"], V["J"]
    N = narrative(root, run, x)
    syn = lambda s: N.get(s) or "*Not yet written.*"
    mechs = "; ".join(f"{D['mech'].get(m, m)} ({m})" for m in split_list(issue["mechanism_ids"]))
    out = [f"# Issue brief: {issue['label']}", "", f"{x} · North Macedonia · {DRAFT}", "",
           f"**Issue definition.** {issue['definition']} **Problem mechanisms:** {mechs}.", "",
           "## In brief (agent synthesis)", "", R.sub(syn("In brief"), names), "",
           "## Assessment (validated at G6)", ""]
    out += table(["Judgement", "Value"], [[t.replace("_", " ").capitalize(), J.get(t, {}).get("value", "not judged")]
                                         for t in ("unresolved_gap", "direction_of_travel", "priority", "tractability")])
    for t, h in (("unresolved_gap", "What remains"), ("direction_of_travel", "Direction of travel"), ("priority", "Priority"), ("tractability", "Tractability")):
        j = J.get(t)
        if j:
            ov = f" The analyst set this value at G6: {j['override_reason']}" if j["review_status"] == "overridden" else ""
            out += [f"**{h}.** {R.sub(j['reason'], names)}{ov}", ""]
    out += ["*These reasons are shown as validated at G6. Where a reason says that implementation statuses were still proposals, it was written at stage 10; those statuses were validated at the same gate.*", ""]
    out += ["## The EU requirement and how it has changed", "", "*Agent synthesis:* " + R.sub(syn("How the EU requirement has changed"), names), ""]
    out += ["## Country response and implementation", ""]
    if V["iids"]:
        rows = []
        for n in V["iids"]:
            j = V["status"].get(n, {})
            rows.append([names.get(n, n), D["ints"].get(n, {}).get("intervention_type", ""), j.get("value", "not judged"), R.sub(j.get("reason", ""), names)])
        out += ["Implementation status is a validated judgement (G6); adoption is never treated as success.", ""]
        out += table(["Intervention", "Type", "Implementation status", "Reason"], rows)
    else:
        out += ["No country intervention is linked to this issue in the evidence.", ""]
    out += ["## Outcomes", ""]
    if V["outc"]:
        rows = [[names.get(l["from_id"], l["from_id"]), R.sub(D["items"][l["to_id"]]["summary"]) + f" [{R.n(l['to_id'])}]",
                 s["value"] if s else "not judged", a["value"] if a else "not judged", R.sub(s["reason"], names) if s else ""] for l, s, a in V["outc"]]
        out += table(["Intervention", "Stated outcome", "Success", "Attribution", "Reason"], rows)
    else:
        out += ["No stated outcome is linked to an intervention under this issue, so no success or attribution judgement was made.", ""]
    out += ["## Conflicting evidence", ""]
    if V["conflicts"]:
        out += [f"- {R.sub(l['basis'], names)} [{R.n(l['from_id'])}][{R.n(l['to_id'])}]" for l in V["conflicts"]] + [""]
    else:
        out += ["No confirmed conflict between sources under this issue.", ""]
    out += ["## Key evidence", "",
            "The items relied on for the assessment above. Source quality, evidence confidence and relevance are separate judgements and are never combined.", ""]
    rows = []
    for k in V["key"]:
        i = D["items"][k]
        note = "; ".join(filter(None, ["machine translated" if i.get("machine_translated") else "", *[f for f in i["flags"] if f in ("hedged", "ocr")]]))
        rows.append([f"[{R.n(k)}]", (i["dates"].get("publication_date") or "")[:4], i["_source"], CHAIN.get(i["pass2"]["chain_link"], i["pass2"]["chain_link"]),
                     i["summary"], quality(D, k, issue), V["conf"].get(k, ""), V["rel"].get(k, ""), note])
    out += table(["Ref", "Year", "Source", "Chain link", "What the source says (summary)", "Source quality", "Evidence confidence", "Relevance", "Notes"], rows)
    out += ["## Open questions (agent synthesis)", "", R.sub(syn("Open questions"), names), "",
            "## Coverage and limits", "",
            f"This brief rests on {len(V['mine'])} in-scope evidence items from {len(V['srcs'])} sources dated from 2020 to the evidence freeze "
            f"of 29 October 2026, of which {V['mt']} are machine translated. It covers North Macedonia only and the scope of RUN-2026-01; "
            "about one in eight in-scope claims in EU sources may have been missed (LIM-0025). Full limits are in the coverage and limits report.", ""]
    return out + R.annex(D["reg"])


def scope_overview(root, run, D):
    R, N = Refs(D["items"]), narrative(root, run, "scope_overview")
    out = ["# Scope overview: North Macedonia, RUN-2026-01", "", DRAFT, "",
           "## Summary (agent synthesis)", "", R.sub(N.get("Summary", "*Not yet written.*")), ""]
    groups = {}
    for r in D["issues"]:
        g = "Chapter 2: Freedom of movement for workers" if r["issue_id"].startswith("RI-FMW") else "Technology and AI (cross-cutting theme)"
        groups.setdefault(g, []).append(r)
    for g, rs in groups.items():
        out += [f"## {g}", ""]
        rows = []
        for r in sorted(rs, key=lambda r: ({"High": 0, "Medium": 1, "Low": 2}.get(issue_view(D, r)["J"].get("priority", {}).get("value"), 3), r["issue_id"])):
            V = issue_view(D, r)
            g_ = lambda t: V["J"].get(t, {}).get("value", "")
            rows.append([r["issue_id"], r["label"], r["chapters"].replace(";", ", ") or "spans clusters", r["themes"].replace(";", ", "), g_("priority"),
                         g_("direction_of_travel"), g_("unresolved_gap"), g_("tractability"), f"{len(V['mine'])} items, {len(V['srcs'])} sources, {V['mt']} MT"])
        out += table(["Issue", "Label", "Chapters", "Themes", "Priority", "Direction of travel", "Unresolved gap", "Tractability", "Evidence coverage"], rows)
    out += ["## Notes on evidence coverage (agent synthesis)", "", R.sub(N.get("Notes on evidence coverage", "*Not yet written.*")), ""]
    return out + (R.annex(D["reg"]) if R.order else [])


def coverage(root, run, D):
    import collections
    R, N = Refs(D["items"]), narrative(root, run, "coverage_and_limits")
    req = read_csv(root / "registers" / "source_requirements.csv")[1]
    lim = read_csv(root / "registers" / "limits_log.csv")[1]
    reg = [r for r in D["reg"].values() if r["role"] == "target"]
    out = ["# Source coverage and limits report: RUN-2026-01", "", DRAFT, "",
           "## Summary (agent synthesis)", "", R.sub(N.get("Summary", "*Not yet written.*")), "",
           "## Source requirements", ""]
    c = collections.Counter(r["status"] for r in req if r["role"] != "comparator")
    out += [f"North Macedonia requirements by status: " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())) + ".", ""]
    out += table(["Requirement", "Description", "Core or supporting", "Status", "Notes"],
                 [[r["requirement_id"], r["description"], r["core_or_supporting"], r["status"], r["notes"]] for r in req if r["role"] != "comparator" and r["status"] != "found"])
    c = collections.Counter(r["status"] for r in reg)
    out += ["## Sources for North Macedonia", "", "By status: " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())) + ".", ""]
    out += ["### Excluded and inaccessible", ""]
    out += table(["Source", "Title", "Status", "Reason"], [[r["source_id"], r["title"], r["status"], r["status_reason"]] for r in reg if r["status"] not in ("available", "processed", "extracted")])
    mt = [k for k, i in D["items"].items() if i["country"] == "MKD" and i.get("machine_translated") and i["pass2"]["classification_status"] != "out_of_scope"]
    allk = [k for k, i in D["items"].items() if i["country"] == "MKD" and i["pass2"]["classification_status"] != "out_of_scope"]
    msrc = sorted({D["items"][k]["_source"] for k in mt})
    out += ["## Reliance on machine translation", "",
            f"{len(mt)} of {len(allk)} in-scope North Macedonia items ({100 * len(mt) / max(len(allk), 1):.0f}%) are machine translated, "
            f"from {len(msrc)} sources: {', '.join(msrc)}. Their evidence confidence is capped at Medium.", ""]
    cmp_ = [k for k, i in D["items"].items() if i["country"] != "MKD" and i.get("machine_translated")]
    out += [f"In the comparator pilot, {len(cmp_)} items are machine translated, under LIM-0029 and LIM-0030, also capped at Medium.", ""]
    out += ["## Active limits", ""]
    out += table(["Limit", "Type", "Description", "Applies to", "Revisit"], [[r["limit_id"], r["limit_type"], r["description"], r["applies_to"], r["revisit_in"]] for r in lim if r["run_id"] == run and r["status"] == "active"])
    out += ["## Methodological limitations found during testing (agent synthesis)", "", R.sub(N.get("Methodological limitations", "*Not yet written.*")), ""]
    return out + (R.annex(D["reg"]) if R.order else [])


def comparator_brief(root, run, D, issue):
    R, names, x = Refs(D["items"]), names_of(D), issue["issue_id"]
    N = narrative(root, run, f"comparator_{x}")
    cases = {r["case_id"]: r for r in read_csv(root / "review" / run / "run1b" / "cases" / f"cases_{x}.csv")[1]}
    J = {(j["object_id"], j["judgement_type"]): j for j in D["js"]}
    V = issue_view(D, issue)
    out = [f"# Comparator brief: {issue['label']}", "", f"{x} · North Macedonia · {DRAFT} "
           "**Draft policy options at the end are internal drafts** and stay so after sign-off at G7 until a separate decision adapts them for an external audience.", "",
           "## The issue in North Macedonia (validated at G6)", "",
           f"**Unresolved gap ({V['J']['unresolved_gap']['value']}).** {R.sub(V['J']['unresolved_gap']['reason'], names)}", "",
           f"**Priority {V['J']['priority']['value']}, tractability {V['J']['tractability']['value']}, direction of travel {V['J']['direction_of_travel']['value']}.**", "",
           "## Reading this brief (agent synthesis)", "", R.sub(N.get("Reading this brief", "*Not yet written.*"), names), "",
           "## The comparator cases", ""]
    rows = [[c["case_id"], COUNTRIES.get(c["country"], c["country"]), J.get((cid, "comparator_relevance"), {}).get("value", ""), J.get((cid, "transferability"), {}).get("value", ""),
             R.sub(next(r for r in read_csv(root / "entities" / "comparator_cases.csv")[1] if r["case_id"] == cid)["description"], names)] for cid, c in cases.items()]
    out += table(["Case", "Country", "Comparator relevance", "Transferability (agent synthesis)", "Summary"], rows)
    parts = [("problem_addressed", "Problem addressed"), ("reform_or_mechanism", "Reform or mechanism used"), ("how_implemented", "How it was implemented"),
             ("evidence_of_results", "Evidence of results"), ("limitations_of_evidence", "Limitations of the evidence"),
             ("practical_lesson_for_north_macedonia", "Practical lesson for North Macedonia (agent synthesis)"),
             ("transferable", "What is transferable (agent synthesis)"), ("not_transferable", "What is not transferable (agent synthesis)")]
    for cid, c in cases.items():
        rj, tj = J.get((cid, "comparator_relevance"), {}), J.get((cid, "transferability"), {})
        out += [f"### {cid}: {COUNTRIES.get(c['country'], c['country'])}", "", f"**Comparator relevance: {rj.get('value', '')}.** {R.sub(rj.get('reason', ''), names)}", ""]
        for f, h in parts:
            out += [f"**{h}.** {R.sub(c[f], names)}", ""]
        out += [f"**Transferability judgement: {tj.get('value', '')}.** {R.sub(tj.get('reason', ''), names)}", ""]
    for s in ("Lessons across the cases", "Draft policy options"):
        out += [f"## {s} (agent synthesis, internal draft)" if s == "Draft policy options" else f"## {s} (agent synthesis)", "", R.sub(N.get(s, "*Not yet written.*"), names), ""]
    return out + R.annex(D["reg"])


def factpack(D, issue):
    V, names = issue_view(D, issue), names_of(D)
    out = [f"# Fact pack {issue['issue_id']}: {issue['label']}", "", issue["definition"], "", "## Validated issue judgements", ""]
    for t, j in V["J"].items():
        out += [f"- {t}: {j['value']} ({j['review_status']}). {j['reason']} Items: {j['evidence_item_ids']}"]
    out += ["", "## Interventions and validated implementation status", ""]
    out += [f"- {n} {names.get(n, '')}: {V['status'].get(n, {}).get('value', 'not judged')}. {V['status'].get(n, {}).get('reason', '')}" for n in V["iids"]]
    out += ["", "## Outcomes", ""] + [f"- {l['from_id']} leads to {l['to_id']}: success {s['value'] if s else '-'}, attribution {a['value'] if a else '-'}. {s['reason'] if s else ''}" for l, s, a in V["outc"]]
    out += ["", "## Confirmed conflicts", ""] + [f"- {l['from_id']} vs {l['to_id']}: {l['basis']}" for l in V["conflicts"]]
    key = set(V["key"]) | {k for j in V["status"].values() for k in split_list(j["evidence_item_ids"])}
    out += ["", "## EU requirement items from Commission documents (summary only)", ""]
    out += [f"- {k} | {(D['items'][k]['dates'].get('publication_date') or '')[:7]} | {D['items'][k]['information_type']} | {D['items'][k]['summary']}" for k in V["reqs"]]
    out += ["", f"## Items relied on by the validated judgements (summary, then quote); {len(V['mine'])} in-scope items in all", ""]
    for k in sorted(key & V["mine"], key=lambda k: (ORDER.get(D["items"][k]["pass2"]["chain_link"], 9), D["items"][k]["dates"].get("publication_date") or "", k)):
        i = D["items"][k]
        q = (i.get("translation_en") or i["stated_text"]).replace("\n", " ")
        out += [f"- {k} | {i['pass2']['chain_link']} | {(i['dates'].get('publication_date') or '')[:7]} | conf {V['conf'].get(k, '')} | rel {V['rel'].get(k, '')}"
                f"{' | MT' if i.get('machine_translated') else ''} | {i['summary']} | \"{q[:400]}\""]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root")
    ap.add_argument("--run", default="RUN-2026-01")
    ap.add_argument("--factpacks", action="store_true", help="write fact packs for the narrative sections instead of the outputs")
    ap.add_argument("--version", action="version", version=VERSION)
    a = ap.parse_args(argv)
    root = project_root(a.root)
    D = load(root, a.run)
    global DRAFT
    g7 = [r for r in read_csv(root / "registers" / "gate_log.csv")[1] if r["run_id"] == a.run and r["gate"] == "G7" and r["decision"] in ("pass", "pass_with_conditions")]
    DRAFT = DRAFT.format(status=f"Validated at G7 ({g7[-1]['gate_decision_id']}), internal output" if g7 else "Draft, prepared at stage 12 for sign-off at G7")
    write = lambda p, lines: (p.parent.mkdir(parents=True, exist_ok=True), p.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8"))
    if a.factpacks:
        for r in D["issues"]:
            write(root / "review" / a.run / "stage12" / "factpacks" / f"{r['issue_id']}.md", factpack(D, r))
        print(f"wrote {len(D['issues'])} fact packs")
        return 0
    od = root / "outputs" / a.run
    write(od / "scope_overview.md", scope_overview(root, a.run, D))
    for r in D["issues"]:
        write(od / f"issue_brief_{r['issue_id']}.md", issue_brief(root, a.run, D, r))
    write(od / "coverage_and_limits_report.md", coverage(root, a.run, D))
    for f in sorted((root / "review" / a.run / "run1b" / "cases").glob("cases_*.csv")):
        x = f.stem[len("cases_"):]
        r = next(r for r in D["issues"] if r["issue_id"] == x)
        write(od / f"comparator_brief_{x}.md", comparator_brief(root, a.run, D, r))
    print(f"wrote outputs to {od}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
