#!/usr/bin/env python3
"""Regenerate index.html, the single review page, from the project files."""

import argparse
import datetime as dt
import re
import sys
from collections import Counter
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (evidence_files, gate_decisions, gate_passed, project_root,  # noqa: E402
                    read_csv, read_json, run_record)

__version__ = "1.0.0"

LABELS = {
    "Validated": ("validated", "Passed its gate and recorded in the gate log."),
    "Pending review": ("pending", "In a gate package, awaiting the reviewers' decision."),
    "Proposed": ("proposed", "Put forward by the agent, not yet in a gate package."),
    "Draft": ("draft", "Work in progress, not yet ready for review."),
    "Not started": ("notstarted", "No work yet."),
}
GATES = [
    ("G0", "Scope, freeze date, reviewers and versions"),
    ("G1", "Source requirements list"),
    ("G2", "Source set and quality ratings"),
    ("G3", "Extraction rules after the sample"),
    ("G4", "Reform-issue taxonomy and mechanisms"),
    ("G5", "Classification queues and entities"),
    ("G6", "Analytical judgements; issues for run 1b"),
    ("G1b", "Comparator countries and source requirements"),
    ("G2b", "Comparator sources"),
    ("G5b", "Comparator extraction and classification"),
    ("G6b", "Comparator judgements and lessons"),
    ("G7", "Outputs sign-off"),
    ("G8", "Run review and changes before the next run"),
]
# Run record version fields and the gate that approves each.
VERSION_ITEMS = [
    ("Codebooks", "Codebooks version", "G0"),
    ("Theme list", "Theme list version", "G0"),
    ("Data dictionary", "Data dictionary version", "G0"),
    ("Evidence schema", "Evidence schema version", "G0"),
    ("Helper tools", "Tools versions", "G0"),
    ("Evidence freeze date", "Evidence freeze date", "G0"),
    ("Extraction rules", "Extraction rules version", "G3"),
    ("Problem mechanism list", "Mechanism list version", "G4"),
    ("Reform-issue taxonomy", "Taxonomy version", "G4"),
    ("Classification rules", "Classification rules version", "G5"),
    ("Judgement rules", "Judgement rules version", "G6"),
]
EMPTY_VALUES = re.compile(r"^(|TBC.*|none yet.*|to be recorded.*)$", re.I)

CSS = """
:root {
  --bg: #f7f7f5; --surface: #ffffff; --text: #1d1f23; --muted: #5b616b; --border: #dcdde0; --accent: #2f5d8a;
  --validated-bg: #e3f2e6; --validated-fg: #1f5e2c;
  --pending-bg: #fff1d6;   --pending-fg: #7a4b00;
  --proposed-bg: #e6eefa;  --proposed-fg: #1f4a80;
  --draft-bg: #efe8f7;     --draft-fg: #563d7c;
  --notstarted-bg: #ececec; --notstarted-fg: #4a4a4a;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #15171a; --surface: #1e2125; --text: #e7e8ea; --muted: #a2a8b1; --border: #343840; --accent: #8db7e3;
    --validated-bg: #1d3a24; --validated-fg: #a8dcb3; --pending-bg: #3d2f12; --pending-fg: #f3cf8a;
    --proposed-bg: #1c2d45; --proposed-fg: #a9c8f0; --draft-bg: #2f2540; --draft-fg: #cdb8ec;
    --notstarted-bg: #2b2d31; --notstarted-fg: #c4c6ca;
  }
}
:root[data-theme="dark"] {
  --bg: #15171a; --surface: #1e2125; --text: #e7e8ea; --muted: #a2a8b1; --border: #343840; --accent: #8db7e3;
  --validated-bg: #1d3a24; --validated-fg: #a8dcb3; --pending-bg: #3d2f12; --pending-fg: #f3cf8a;
  --proposed-bg: #1c2d45; --proposed-fg: #a9c8f0; --draft-bg: #2f2540; --draft-fg: #cdb8ec;
  --notstarted-bg: #2b2d31; --notstarted-fg: #c4c6ca;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); font: 16px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
.wrap { max-width: 1000px; margin: 0 auto; padding: 24px 16px 64px; }
header { border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 8px; }
h1 { font-size: 1.6rem; margin: 0 0 4px; }
h2 { font-size: 1.2rem; margin: 0 0 12px; }
h3 { font-size: 1rem; margin: 16px 0 6px; }
p { margin: 0 0 10px; }
.sub { color: var(--muted); margin: 0; }
nav { display: flex; flex-wrap: wrap; gap: 6px 14px; margin: 16px 0 8px; font-size: .9rem; }
nav a, a { color: var(--accent); }
nav a { text-decoration: none; }
nav a:hover { text-decoration: underline; }
section { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 18px 18px 12px; margin-top: 16px; }
.notice { border-left: 4px solid var(--accent); }
.label { display: inline-block; font-size: .75rem; font-weight: 600; letter-spacing: .02em; padding: 2px 8px; border-radius: 999px; white-space: nowrap; vertical-align: middle; }
.validated { background: var(--validated-bg); color: var(--validated-fg); }
.pending { background: var(--pending-bg); color: var(--pending-fg); }
.proposed { background: var(--proposed-bg); color: var(--proposed-fg); }
.draft { background: var(--draft-bg); color: var(--draft-fg); }
.notstarted { background: var(--notstarted-bg); color: var(--notstarted-fg); }
.legend { display: grid; grid-template-columns: max-content 1fr; gap: 8px 12px; align-items: center; }
.table-wrap { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: .92rem; }
th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--border); vertical-align: top; }
th { color: var(--muted); font-weight: 600; }
dl.facts { display: grid; grid-template-columns: max-content 1fr; gap: 6px 16px; margin: 0; }
dl.facts dt { color: var(--muted); }
dl.facts dd { margin: 0; }
ul { margin: 0 0 10px; padding-left: 20px; }
.placeholder { color: var(--muted); }
code { font-size: .88em; background: var(--bg); padding: 1px 4px; border-radius: 4px; }
footer { color: var(--muted); font-size: .85rem; margin-top: 24px; }
@media (max-width: 600px) { dl.facts, .legend { grid-template-columns: 1fr; } dl.facts dt { margin-top: 6px; } }
"""


def md(text):
    """Escape text and render `code` spans."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", escape(text))


def label(status):
    cls = LABELS.get(status, ("notstarted", ""))[0]
    return f'<span class="label {cls}">{escape(status)}</span>'


def table(header, rows):
    head = "".join(f"<th>{escape(h)}</th>" for h in header)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def facts(pairs):
    return '<dl class="facts">' + "".join(f"<dt>{escape(k)}</dt><dd>{v}</dd>" for k, v in pairs) + "</dl>"


def placeholder(text):
    return f'<p class="placeholder">{escape(text)}</p>'


class Page:
    def __init__(self, root, run, today):
        self.root, self.run, self.today = root, run, today
        self.rec, self.rec_text = run_record(root, run)
        self.decisions = gate_decisions(root, run)
        self.review_dir = root / "review" / run

    def pending(self, gate):
        if gate in self.decisions:
            return False
        return any(self.review_dir.glob(f"{gate}_*.xlsx")) if self.review_dir.exists() else False

    def status(self, gate, has_data):
        if gate_passed(self.decisions, gate):
            return "Validated"
        if self.pending(gate):
            return "Pending review"
        return "Draft" if has_data else "Not started"

    def current_package(self):
        for gate, _ in GATES:
            if self.pending(gate):
                return gate
        return None

    # Sections -----------------------------------------------------------------

    def run_status(self):
        m = re.search(r"^Status: \*\*(.+?)\*\*", self.rec_text, re.M)
        last = max(self.decisions.values(), key=lambda r: r["gate_decision_id"], default=None)
        nxt = next((g for g, _ in GATES if not gate_passed(self.decisions, g)), None)
        pkg = self.current_package()
        return "Run status", facts([
            ("Run", escape(self.run)),
            ("Status", escape(m.group(1) if m else "unknown")),
            ("Current stage", md(re.sub(r";? *update at the start of every stage.*\)$", ")", self.rec.get("Current stage", "")))),
            ("Last gate decision", escape(f"{last['gate']} {last['decision']} on {last['date']} ({last['gate_decision_id']})") if last else "None recorded"),
            ("Gate package awaiting decision", escape(pkg) if pkg else "None"),
            ("Next gate", escape(nxt) if nxt else "All gates passed"),
            ("Evidence freeze date", md(self.rec.get("Evidence freeze date", ""))),
            ("Reviewers", md(self.rec.get("Reviewers", ""))),
            ("Alpha reviewers", md(self.rec.get("Alpha reviewers", ""))),
        ])

    def purpose(self):
        return "Purpose of the alpha", f"<p>{md(self.rec.get('Purpose', ''))}</p>"

    def scope(self):
        _, themes = read_csv(self.root / "taxonomy" / "themes.csv")
        live = [t for t in themes if t.get("status") != "retired"]
        body = facts([(k, md(self.rec.get(k, ""))) for k in
                      ("Target country", "Thematic scope", "Time window", "Language", "Comparator scope")])
        if live:
            body += "<h3>Cross-cutting theme areas</h3>" + table(
                ["Code", "Area", "Definition"], [[escape(t["theme_code"]), escape(t["label"]), escape(t["definition"])] for t in live])
        return "Scope " + label(self.status("G0", True)), body

    def work_in_progress(self):
        rows = []
        _, limits = read_csv(self.root / "registers" / "limits_log.csv")
        active = [r["limit_id"] for r in limits if r["run_id"] == self.run and r["status"] == "active"]
        rows.append(["Scope and active limits", escape(", ".join(active)), label(self.status("G0", True)), "Approved at G0"])
        for name, field, gate in VERSION_ITEMS:
            value = self.rec.get(field, "")
            has = not EMPTY_VALUES.match(value.strip())
            rows.append([escape(name), md(value), label(self.status(gate, has)), escape(f"Approved at {gate}")])
        for m in re.finditer(r"^- \*\*([^*]+?) \((unresolved|unverified)[^)]*\):\*\* (.+)$", self.rec_text, re.M):
            st = "Proposed" if m.group(2) == "unresolved" else "Not started"
            rows.append([escape(m.group(1)), "", label(st), md(m.group(3))])
        return "Work in progress", table(["Item", "Current value", "Status", "Note"], rows)

    def gates(self):
        approvers = self.approvers()
        rows = []
        for gate, what in GATES:
            r = self.decisions.get(gate)
            if r and gate_passed(self.decisions, gate):
                st = label("Validated") + escape(f" {r['decision']}, {r['date']}")
            elif r:
                st = label("Draft") + escape(f" {r['decision']}, {r['date']}: to be presented again")
            elif self.pending(gate):
                st = label("Pending review")
            else:
                st = label("Not started")
            rows.append([escape(gate), escape(what), escape(approvers.get(gate, approvers.get("*", ""))), st])
        return "Gates", table(["Gate", "What it decides", "Approvers", "Status"], rows)

    def approvers(self):
        out = {}
        for part in self.rec.get("Reviewers", "").split(";"):
            m = re.match(r"\s*(?:Formal gate approvers:\s*)?(.+?)\s*\((.+)\)\s*$", part)
            if not m:
                continue
            names = re.sub(r"\s+together$", "", m.group(1))
            if "all gates" in m.group(2):
                out["*"] = names
            else:
                for g in re.findall(r"G\d+b?", m.group(2)):
                    out[g] = names
        return out

    def sources(self):
        _, reg = read_csv(self.root / "registers" / "source_register.csv")
        _, req = read_csv(self.root / "registers" / "source_requirements.csv")
        if not reg and not req:
            return "Sources " + label("Not started"), placeholder(
                "Will show the source requirements and gaps, the source register by family, year, chapter and theme, exclusions and "
                "inaccessible documents, and source quality ratings. Populated from stage 1; validated at G1 and G2.")
        body = ""
        if req:
            body += "<h3>Source requirements " + label(self.status("G1", True)) + "</h3>" + table(
                ["Status", "Requirements"], [[escape(k), str(v)] for k, v in sorted(Counter(r["status"] for r in req).items())])
        if reg:
            fams = sorted({r["source_family"] for r in reg})
            stats = sorted({r["status"] for r in reg})
            cnt = Counter((r["source_family"], r["status"]) for r in reg)
            body += "<h3>Source register</h3>" + table(["Family"] + stats, [[escape(f)] + [str(cnt[(f, s)]) for s in stats] for f in fams])
        return "Sources " + label(self.status("G2", bool(reg))), body

    def extraction(self):
        files = [read_json(p) for p in evidence_files(self.root)]
        if not files:
            return "Extraction " + label("Not started"), placeholder(
                "Will show the extraction sample, the comparison with hand-coded passages, accuracy and error patterns, and the rules "
                "version approved. Populated from stage 5; validated at G3.")
        items = [i for f in files for i in f.get("items", [])]
        by_status = Counter(f["extraction"]["status"] for f in files)
        body = facts([
            ("Evidence files", escape(", ".join(f"{v} {k}" for k, v in sorted(by_status.items())))),
            ("Evidence items", str(len(items))),
            ("Quotes verified", f"{sum(bool(i.get('quote_verified')) for i in items)} of {len(items)}"),
            ("Items by type", escape(", ".join(f"{k} {v}" for k, v in sorted(Counter(i['information_type'] for i in items).items())))),
            ("Items by scope basis", escape(", ".join(f"{k} {v}" for k, v in sorted(Counter(b for i in items for b in i.get('scope_basis', [])).items())))),
            ("Rules version", escape(self.rec.get("Extraction rules version", ""))),
        ])
        return "Extraction " + label(self.status("G3", True)), body

    def taxonomy(self):
        _, issues = read_csv(self.root / "taxonomy" / "reform_issues.csv")
        if not issues:
            return "Taxonomy " + label("Not started"), placeholder(
                "Will show the reform issues for the in-scope chapters and themes, the problem mechanisms, and items that fit no issue. "
                "Populated from stage 7; validated at G4.")
        pend = self.pending("G4") or self.pending("G5")

        def st(r):
            if r["status"] == "approved":
                return label("Validated")
            if r["status"] in ("merged", "retired"):
                return escape(r["status"])
            return label("Pending review" if pend else "Draft")
        rows = [[escape(r["issue_id"]), escape(r["label"]), escape(r["definition"]), escape(r["chapters"]), escape(r["themes"]), st(r)] for r in issues]
        return "Taxonomy " + label(self.status("G4", True)), table(["ID", "Issue", "Definition", "Chapters", "Themes", "Status"], rows)

    def classification(self):
        items = [i for p in evidence_files(self.root) for i in read_json(p).get("items", [])]
        done = [i for i in items if i.get("pass2", {}).get("classification_status") != "not_classified"]
        if not done:
            return "Classification " + label("Not started"), placeholder(
                "Will show classification coverage, resolved queues, interventions and actors, conflicting evidence and items found to "
                "be out of scope. Populated from stage 9; validated at G5.")
        cnt = Counter(i["pass2"]["classification_status"] for i in items)
        _, links = read_csv(self.root / "links" / "links.csv")
        body = table(["Classification status", "Items"], [[escape(k), str(v)] for k, v in sorted(cnt.items())])
        body += facts([("Contradicts links", str(sum(l["link_type"] == "contradicts" for l in links)))])
        return "Classification " + label(self.status("G5", True)), body

    def assessment(self):
        _, js = read_csv(self.root / "judgements" / "judgements.csv")
        if not js:
            return "Assessment " + label("Not started"), placeholder(
                "Will show one dossier per reform issue: the chain from EU requirement to unresolved gap, direction of travel, priority "
                "and tractability, with source quality, evidence confidence and relevance shown side by side. Populated from stage 10; "
                "validated at G6.")
        pend = self.pending("G6")

        def st(r):
            if r["review_status"] in ("validated", "overridden"):
                return label("Validated") + ("" if r["review_status"] == "validated" else " overridden")
            return label("Pending review" if pend else "Proposed")
        issue_level = [r for r in js if r["object_type"] == "issue_country"]
        body = table(["Judgement type", "Proposed", "Validated or overridden"], [
            [escape(t), str(sum(r["judgement_type"] == t and r["review_status"] == "proposed" for r in js)),
             str(sum(r["judgement_type"] == t and r["review_status"] != "proposed" for r in js))]
            for t in sorted({r["judgement_type"] for r in js})])
        if issue_level:
            body += "<h3>Issue-level judgements</h3>" + table(["Issue", "Judgement", "Value", "Reason", "Status"], [
                [escape(r["object_id"]), escape(r["judgement_type"]), escape(r["value"]), escape(r["reason"]), st(r)] for r in issue_level])
        return "Assessment " + label(self.status("G6", True)), body

    def comparators(self):
        _, cases = read_csv(self.root / "entities" / "comparator_cases.csv")
        if not cases:
            return "Comparator pilot (run 1b) " + label("Not started"), placeholder(
                "Will show the issues chosen for the pilot, comparator countries and cases, lessons and transferability. Populated after "
                "G6; validated at G1b to G6b.")
        rows = [[escape(c["case_id"]), escape(c["country"]), escape(c["reform_issue_id"]), escape(c["description"]),
                 label("Validated" if c.get("selected_at") else "Proposed")] for c in cases]
        return "Comparator pilot (run 1b) " + label(self.status("G6b", True)), table(["Case", "Country", "Issue", "Description", "Status"], rows)

    def outputs(self):
        out_dir = self.root / "outputs" / self.run
        files = sorted(out_dir.glob("*.md")) if out_dir.exists() else []
        if not files:
            return "Outputs " + label("Not started"), placeholder(
                "Will show the scope overview, issue briefs, the source coverage and limits report, comparator briefs and draft policy "
                "options. Draft policy options stay labelled as internal drafts after sign-off. Populated from stage 12; validated at G7.")
        st = self.status("G7", True)
        rows = []
        for f in files:
            rel = f.relative_to(self.root).as_posix()
            note = "Internal draft policy options" if f.name.startswith("comparator_brief_") else ""
            rows.append([f'<a href="{escape(rel)}">{escape(f.name)}</a>', label(st), escape(note)])
        return "Outputs " + label(st), table(["File", "Status", "Note"], rows)

    def lessons(self):
        _, rows = read_csv(self.root / "runs" / self.run / "alpha_learning_log.csv")
        pend = self.current_package() is not None

        def st(r):
            s = r.get("status", "")
            if s in ("accepted", "implemented"):
                return label("Validated") + escape(f" {s}")
            if s == "open":
                return label("Pending review" if pend else "Proposed")
            return escape(s)
        body = f'<p class="sub">Curated lessons from <code>runs/{escape(self.run)}/alpha_learning_log.csv</code>. Each is confirmed by the analyst at a gate.</p>'
        body += table(["ID", "Area", "Lesson", "Scaling", "Status"], [
            [escape(r["lesson_id"]), escape(r["area"].replace("_", " ")), escape(r["description"]),
             escape(r["scaling_dimension"].replace(";", "; ")), st(r)] for r in rows]) if rows else placeholder("No lessons recorded yet.")
        review = self.root / "runs" / self.run / "run_review.md"
        if review.exists():
            body += "<h3>Run review " + label(self.status("G8", True)) + f'</h3><p><a href="{escape(review.relative_to(self.root).as_posix())}">run_review.md</a></p>'
        else:
            body += "<h3>Run review " + label("Not started") + "</h3>" + placeholder("The run review, with a section on readiness for scaling, appears here at G8.")
        return "Alpha lessons", body

    def known_gaps(self):
        gaps = []
        for doc in ("ARCHITECTURE.md", "README.md"):
            path = self.root / doc
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            refs = re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", text) + re.findall(r"`([\w./-]+\.dot)`", text)
            for ref in dict.fromkeys(refs):
                if not (self.root / ref).exists():
                    gaps.append(f"{ref}, referred to in {doc}, is missing from the repository.")
        if not gaps:
            return None
        return "Known documentation gaps", "<ul>" + "".join(f"<li>{escape(g)}</li>" for g in gaps) + "</ul>"

    def render(self):
        sections = [("status", self.run_status()), ("purpose", self.purpose()), ("scope", self.scope()),
                    ("wip", self.work_in_progress()), ("gates", self.gates()), ("sources", self.sources()),
                    ("extraction", self.extraction()), ("taxonomy", self.taxonomy()), ("classification", self.classification()),
                    ("assessment", self.assessment()), ("comparators", self.comparators()), ("outputs", self.outputs()),
                    ("lessons", self.lessons())]
        gaps = self.known_gaps()
        if gaps:
            sections.append(("gaps", gaps))
        nav = "".join(f'<a href="#{sid}">{escape(re.sub(r"<span.*?</span>|<[^>]+>", "", title).strip())}</a>' for sid, (title, _) in sections)
        body = "".join(f'<section id="{sid}"><h2>{title}</h2>{content}</section>' for sid, (title, content) in sections)
        legend = "".join(f'{label(k)}<span>{escape(v[1])}</span>' for k, v in LABELS.items())
        country = self.rec.get("Target country", "")
        return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Accession Alpha Review</title>
<!-- Generated by tools/build_review_page.py {__version__} on {self.today}. Do not edit by hand: rebuild instead.
     This page is a review interface only. Gate decisions are recorded in registers/gate_log.csv. -->
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header>
<h1>EU Accession Reform Intelligence Tool: alpha review</h1>
<p class="sub">{escape(self.run)} · {escape(country)} · Page updated {escape(self.today)}</p>
<nav aria-label="Sections">{nav}</nav>
</header>
<section class="notice" aria-label="About this page">
<p>This page lets reviewers follow how the alpha is developing. It is a review interface, not the place where decisions are made: gate decisions are taken on the review spreadsheets and recorded in the gate log. Nothing on this page is analysis unless it is labelled {label("Validated")}.</p>
<div class="legend">{legend}</div>
</section>
{body}
<footer><p>Generated from the project files of {escape(self.run)} by <code>tools/build_review_page.py</code> {__version__}. Rebuilt when each gate package is prepared and after each gate decision.</p></footer>
</div>
</body>
</html>
"""


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Regenerate index.html from the run record, gate log, limits log, registers, taxonomy, evidence, judgements, outputs "
                    "and alpha learning log. Writes one self-contained file (inline styles, no external scripts or fonts). Status labels "
                    "come from the gate log, review packages and review statuses, never from the tool's own judgement.")
    p.add_argument("--run", default="RUN-2026-01", help="run ID (default RUN-2026-01)")
    p.add_argument("--root", help="project root (default: the folder above tools/)")
    p.add_argument("--output", help="file to write (default index.html in the project root)")
    p.add_argument("--date", help="date shown on the page (default today, YYYY-MM-DD)")
    p.add_argument("--version", action="version", version=__version__)
    a = p.parse_args(argv)
    root = project_root(a.root)
    page = Page(root, a.run, a.date or dt.date.today().isoformat())
    out = Path(a.output) if a.output else root / "index.html"
    out.write_text(page.render(), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
