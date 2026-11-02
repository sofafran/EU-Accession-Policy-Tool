"""The analysis page once a run's outputs have passed G7: an easy-to-navigate product page built only from validated
records (issue judgements, signed-off outputs and their narrative inputs, comparator cases and draft options).
Called by build_review_page.py; adds no analysis of its own. One self-contained file with inline CSS and JavaScript."""

import re
from collections import Counter
from html import escape

from build_outputs import COUNTRIES, issue_view, lesson_field, load, narrative, names_of
from common import gate_passed, read_csv, split_list

ITEM = re.compile(r"\b[A-Z]{3}-(?:EU|GOV|CSO|IO|RES|MED|INT)-\d{4}-\d{3}-\d{4}\b")
PRI = {"High": 0, "Medium": 1, "Low": 2}
STRAND = {"fmw": "Chapter 2", "tec": "Technology & AI"}

CSS_EXTRA = """
html { scroll-behavior: smooth; }
section, .issue, .group, .pcard, .case, .option { scroll-margin-top: 64px; }
nav.top { position: sticky; top: 0; z-index: 5; background: var(--bg); border-bottom: 1px solid var(--border); padding: 8px 0; display: flex; flex-wrap: wrap; gap: 6px; }
nav.top a { text-decoration: none; font-size: .88rem; border: 1px solid var(--border); border-radius: 999px; padding: 4px 12px; background: var(--surface); }
nav.top a:hover, nav.top a:focus { border-color: var(--accent); }
.lbl { display: inline-block; font-size: .72rem; font-weight: 600; padding: 2px 8px; border-radius: 999px; white-space: nowrap; vertical-align: middle; }
.lbl.validated { background: var(--validated-bg); color: var(--validated-fg); }
.lbl.internal { background: var(--pending-bg); color: var(--pending-fg); }
.lbl.synth { background: var(--proposed-bg); color: var(--proposed-fg); }
.lbl.limit { background: var(--notstarted-bg); color: var(--notstarted-fg); }
.chip { display: inline-block; font-size: .78rem; border: 1px solid var(--border); border-radius: 6px; padding: 1px 7px; margin: 2px 4px 2px 0; white-space: nowrap; }
.chip b { font-weight: 600; }
.chip.High { border-color: #c0392b; } .chip.Medium { border-color: #b7791f; } .chip.Low { border-color: var(--border); }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin: 12px 0; }
.stat { border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; background: var(--bg); }
.stat .n { font-size: 1.5rem; font-weight: 700; color: var(--accent); line-height: 1.1; font-variant-numeric: tabular-nums; }
.stat .l { font-size: .82rem; color: var(--muted); }
.filters { display: flex; flex-wrap: wrap; gap: 8px 12px; align-items: end; background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; margin: 8px 0 12px; }
.filters label { display: flex; flex-direction: column; font-size: .8rem; color: var(--muted); gap: 2px; }
.filters input, .filters select, .filters button { font: inherit; font-size: .9rem; padding: 5px 8px; border: 1px solid var(--border); border-radius: 6px; background: var(--surface); color: var(--text); }
.filters input[type=search] { min-width: 240px; }
.count { font-weight: 600; margin: 4px 0 8px; }
.group h3 { margin-top: 18px; }
.issue, .pcard, .case, .option { border: 1px solid var(--border); border-radius: 8px; padding: 12px 14px; margin: 10px 0; background: var(--surface); }
.issue .top, .pcard .top, .case .top, .option .top { display: flex; flex-wrap: wrap; gap: 6px 10px; align-items: baseline; justify-content: space-between; }
.issue h4, .pcard h4, .case h4, .option h4 { margin: 2px 0 6px; font-size: 1.02rem; }
.idlink { font-family: ui-monospace, monospace; font-size: .82rem; color: var(--muted); text-decoration: none; }
.idlink:hover { text-decoration: underline; }
.gap { margin: 6px 0; }
details > summary { cursor: pointer; color: var(--accent); font-weight: 600; font-size: .9rem; margin: 6px 0; }
details.more[open] > summary { margin-bottom: 10px; }
details.refs > summary { font-weight: 500; }
.detail h5 { font-size: .9rem; margin: 14px 0 4px; color: var(--muted); text-transform: uppercase; letter-spacing: .03em; }
.detail p { margin: 0 0 8px; }
.ints { list-style: none; padding: 0; margin: 0; font-size: .9rem; }
.ints li { padding: 3px 0; border-bottom: 1px dotted var(--border); }
.ints .st { color: var(--muted); font-size: .82rem; }
dl.kv { display: grid; grid-template-columns: 190px 1fr; gap: 6px 14px; margin: 6px 0; }
dl.kv dt { color: var(--muted); font-size: .9rem; }
dl.kv dd { margin: 0; }
.hidden { display: none !important; }
.totop { display: inline-block; margin-top: 12px; font-size: .85rem; }
.case { border-left: 4px solid var(--accent); }
.option { border-left: 4px solid var(--pending-fg); }
.compbox { background: var(--bg); border: 1px solid var(--border); border-radius: 10px; padding: 4px 14px 10px; margin: 14px 0; }
.note { color: var(--muted); font-size: .9rem; }
.quote { font-size: .9rem; }
.assess { margin: 6px 0; font-size: .95rem; }
.prog { display: flex; flex-wrap: wrap; gap: 4px 16px; font-size: .86rem; margin: 4px 0 0; color: var(--muted); }
.prog b { color: var(--text); font-weight: 600; }
details.prog26 > summary { font-weight: 500; }
.banner26 { border: 1px dashed var(--border); border-radius: 8px; padding: 8px 12px; margin: 10px 0; background: var(--bg); }
nav.top a.active { border-color: var(--accent); background: var(--accent); color: var(--bg); }
.says { margin: 6px 0 10px; padding-left: 20px; } .says li { margin: 4px 0; }
.stat a { text-decoration: none; color: inherit; display: block; }
.stat:has(a):hover { border-color: var(--accent); }
.pindex { columns: 2 320px; column-gap: 24px; padding-left: 20px; font-size: .92rem; } .pindex li { break-inside: avoid; margin: 2px 0; }
@media (max-width: 700px) { dl.kv { grid-template-columns: 1fr; } .filters input[type=search] { min-width: 0; width: 100%; } }
"""

JS = r"""
(function () {
  var cards = Array.prototype.slice.call(document.querySelectorAll('.issue'));
  var f = { q: document.getElementById('f-q'), strand: document.getElementById('f-strand'), pri: document.getElementById('f-pri'),
            dir: document.getElementById('f-dir'), gap: document.getElementById('f-gap'), st: document.getElementById('f-st'), u26: document.getElementById('f-u26') };
  var count = document.getElementById('f-count');
  function apply() {
    var q = f.q.value.trim().toLowerCase(), n = 0;
    cards.forEach(function (c) {
      var ok = (!f.strand.value || c.dataset.strand === f.strand.value) && (!f.pri.value || c.dataset.priority === f.pri.value) &&
               (!f.dir.value || c.dataset.direction === f.dir.value) && (!f.gap.value || c.dataset.gap === f.gap.value) &&
               (!f.st.value || (' ' + c.dataset.status + ' ').indexOf(' ' + f.st.value + ' ') !== -1) &&
               (!f.u26.value || (' ' + c.dataset.u26 + ' ').indexOf(' ' + f.u26.value + ' ') !== -1) &&
               (!q || c.dataset.search.indexOf(q) !== -1);
      c.classList.toggle('hidden', !ok);
      if (ok) n++;
    });
    document.querySelectorAll('.group').forEach(function (g) {
      g.classList.toggle('hidden', !g.querySelector('.issue:not(.hidden)'));
    });
    count.textContent = 'Showing ' + n + ' of ' + cards.length + ' reform issues';
  }
  function reset() { f.q.value = ''; f.strand.value = ''; f.pri.value = ''; f.dir.value = ''; f.gap.value = ''; f.st.value = ''; f.u26.value = ''; apply(); }
  ['input', 'change'].forEach(function (ev) { Object.keys(f).forEach(function (k) { f[k].addEventListener(ev, apply); }); });
  document.getElementById('f-reset').addEventListener('click', reset);
  document.querySelectorAll('a[data-strand]').forEach(function (a) {
    a.addEventListener('click', function () { reset(); f.strand.value = a.dataset.strand; apply(); });
  });
  function openHash() {
    var id = decodeURIComponent(location.hash.slice(1));
    var el = id && document.getElementById(id);
    if (el && el.classList.contains('issue')) {
      if (el.classList.contains('hidden')) reset();
      var d = el.querySelector('details.more:not(.prog26)'); if (d) d.open = true;
      el.scrollIntoView();
    }
  }
  var links = Array.prototype.slice.call(document.querySelectorAll('nav.top a'));
  function spy() {
    var cur = null;
    links.forEach(function (a) {
      var t = document.getElementById(a.getAttribute('href').slice(1));
      if (t && !t.classList.contains('hidden') && t.getBoundingClientRect().top <= 90) cur = a;
    });
    links.forEach(function (a) { a.classList.toggle('active', a === cur); });
  }
  window.addEventListener('scroll', spy, { passive: true });
  window.addEventListener('hashchange', openHash);
  apply();
  openHash();
  spy();
})();
"""


def lbl(text, cls):
    return f'<span class="lbl {cls}">{escape(text)}</span>'


VAL = lbl("Validated", "validated")
DRAFT = lbl("Internal draft", "internal")
AWAIT = lbl("Awaiting 2026 Enlargement Package", "limit")
SYN = lbl("Agent synthesis", "synth")


def pretty(v):
    return (v or "not judged").replace("_", " ")


def text(t):
    """Escape and set item IDs in code type so they read as references."""
    return ITEM.sub(lambda m: f"<code>{m.group(0)}</code>", escape(t or ""))


def sentences(t):
    return [s for s in re.split(r"(?<=[.])\s+(?=[A-Z])", (t or "").strip()) if s]


def no_refs(t):
    """Drop bracketed lists of item IDs, for the one-line summaries on collapsed cards (the IDs stay in the detail)."""
    t = re.sub(r"\s*\((?:[^()]*?\b[A-Z]{3}-(?:EU|GOV|CSO|IO|RES|MED|INT)-\d{4}-\d{3}-\d{4}\b[^()]*?)\)", "", t or "")
    return re.sub(r"\s+([.,;])", r"\1", t).strip()


# Wording specific to one run, kept so that its page does not change when the tool is generalised (E19).
RUN_TEXT = {
    "RUN-2026-01": {
        "other26": "(the 2026 Rule of Law country chapter, the 2026 economic reform programme assessment and conclusions, the third Reform Agenda payment "
                   "assessment and the 2026 subcommittee), which is part of the validated alpha",
        "status": "Completed alpha",
        "title": "Accession Alpha Analysis",
        "lang": "translations from Macedonian and other languages are machine translations",
        "summary": "alpha_summary.html",
        "summary_label": "Alpha summary",
    },
}
NUM = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}

STATUS = {"validated": "Validated at G6", "analyst": "Set by the analyst at G6", "rereview": "Flagged for re-review at G7"}


def what_remains(reason):
    ss = sentences(reason)
    hit = next((s for s in ss if s.startswith("What remains")), None)
    return hit or (ss[-1] if ss else "")


class ProductPage:
    def __init__(self, page):
        self.p = page
        self.root, self.run = page.root, page.run
        self.up = "../"  # the country page sits in analysis/, one folder below the project root
        self.D = load(self.root, self.run)
        self.cc, self.cname = self.D["cc"], self.D["cname"]
        self.T = RUN_TEXT.get(self.run, {})
        self.names = names_of(self.D)
        self.views = {r["issue_id"]: issue_view(self.D, r) for r in self.D["issues"]}
        self.narr = {r["issue_id"]: narrative(self.root, self.run, r["issue_id"]) for r in self.D["issues"]}
        self.cases = {}
        for f in sorted((self.root / "review" / self.run / "run1b" / "cases").glob("cases_*.csv")):
            self.cases[f.stem[len("cases_"):]] = read_csv(f)[1]
        self.ent = {r["case_id"]: r for r in read_csv(self.root / "entities" / "comparator_cases.csv")[1]}
        self.J = {(j["object_id"], j["judgement_type"]): j for j in self.D["js"]}
        self.opts = {x: self.parse_options(x) for x in self.cases}
        self.themes = {r["theme_code"]: r["label"] for r in read_csv(self.root / "taxonomy" / "themes.csv")[1]}
        self.mechs = {r["mechanism_id"]: r["label"] for r in read_csv(self.root / "taxonomy" / "mechanisms.csv")[1]}
        # 2025 -> 2026 comparison (decision E18). The annual country report of each year is the anchor; everything else stays as judged.
        self.alljs = read_csv(self.root / "judgements" / "judgements.csv")[1]
        rep_year = lambda y: {sid for sid, r in self.D["reg"].items() if sid.startswith(f"{self.cc}-EU-") and r["document_type"] == "annual report"
                              and r["publication_date"].startswith(y) and r["status"] == "available"}
        self.rep25, self.rep26 = rep_year("2025"), rep_year("2026")
        self.other26 = {sid for sid, r in self.D["reg"].items() if sid.startswith(f"{self.cc}-EU-") and r["publication_date"].startswith("2026")} - self.rep26
        self.g7 = [r for r in page.decisions.values() if r["gate"] == "G7"][-1]

    # Helpers ------------------------------------------------------------------

    def strand(self, issue_id):
        return "fmw" if issue_id.startswith("RI-FMW") else "tec"

    def quote(self, k):
        i = self.D["items"].get(k)
        if not i:
            return ""
        s = self.D["reg"].get(i["_source"], {})
        loc = i["location"]
        where = f"p. {loc['page']}" if loc.get("page") else (loc.get("section") or "")
        conf = next((j["value"] for j in self.D["js"] if j["object_id"] == k and j["judgement_type"] == "evidence_confidence"), "")
        mt = lbl("Evidence limit: machine translated", "limit") if i.get("machine_translated") else ""
        tr = f'<p class="tr">Machine translation: {escape(i["translation_en"])}</p>' if i.get("machine_translated") and i.get("translation_en") else ""
        return (f'<div class="quote"><p>&ldquo;{escape(i["stated_text"])}&rdquo;</p>{tr}<p class="ref"><code>{escape(k)}</code> · '
                f'{escape(s.get("institution", ""))}, {escape(s.get("title", i["_source"]))[:140]}, {escape((i["dates"].get("publication_date") or "")[:4])}, '
                f'{escape(where)}{" · evidence confidence " + escape(conf) if conf else ""} {mt}</p></div>')

    def refs(self, ids, title="Evidence references"):
        seen = []
        for k in ids:
            if k in self.D["items"] and k not in seen:
                seen.append(k)
        if not seen:
            return ""
        return (f'<details class="refs"><summary>{escape(title)} ({len(seen)})</summary>'
                + "".join(self.quote(k) for k in seen) + "</details>")

    def ids_in(self, *texts):
        out = []
        for t in texts:
            for m in ITEM.findall(t or ""):
                if m not in out:
                    out.append(m)
        return out

    def jv(self, x, t):
        return self.views[x]["J"].get(t, {})

    def chips(self, x):
        g = lambda t: self.jv(x, t).get("value", "")
        return (f'<span class="chip {escape(g("priority"))}">Priority <b>{escape(g("priority"))}</b></span>'
                f'<span class="chip">Direction <b>{escape(pretty(g("direction_of_travel")))}</b></span>'
                f'<span class="chip">Gap <b>{escape(pretty(g("unresolved_gap")))}</b></span>'
                f'<span class="chip">Tractability <b>{escape(g("tractability"))}</b></span>')

    def status(self, x):
        J = self.views[x]["J"]
        st = ["validated"]
        if any(j.get("review_status") == "overridden" for j in J.values()):
            st.append("analyst")
        if any(j.get("rereview_flag") == "yes" for j in J.values()):
            st.append("rereview")
        return st

    def status_labels(self, x):
        st = self.status(x)
        out = VAL
        if "analyst" in st:
            out += " " + lbl("Set by the analyst at G6", "internal")
        if "rereview" in st:
            out += " " + lbl("Flagged for re-review", "limit")
        return out

    def banner(self):
        n = Counter(self.u26(r["issue_id"])[0] for r in self.D["issues"])
        held = sum(1 for r in self.D["issues"] if any(self.D["items"][k]["_source"] in self.other26 for k in self.D["by"].get(r["issue_id"], [])))
        if not self.rep26:
            head = (f'<b>2026 update:</b> {AWAIT} No 2026 country report on {escape(self.cname)} is in the project yet, so every issue shows its 2025 position and '
                    'the current validated judgements, and its 2026 update is marked as awaiting the package. ')
        else:
            head = (f'<b>2026 update:</b> 2026 country report added. {n["assessed"]} issues assessed, {n["proposed"]} with proposed changes, '
                    f'{n["no_new"]} with no new report item. ')
        return (f'<div class="banner26">{head}{held} issues already draw on other 2026 official EU evidence '
                + self.T.get("other26", f"({len(self.other26)} document{'s' if len(self.other26) != 1 else ''}), which is part of the validated run") +
                ' and is not a substitute for the Enlargement Package. Open <b>2025 &rarr; 2026 comparison</b> on any issue card.</div>')

    def u26(self, x):
        """State of the 2026 update for an issue: awaiting (no 2026 country report registered or no item from it on this issue),
        proposed (2026 report items exist, comparison not yet validated) or assessed."""
        ks = self.D["by"].get(x, [])
        new = [k for k in ks if self.D["items"][k]["_source"] in self.rep26]
        if not self.rep26:
            return "awaiting", new
        if not new:
            return "no_new", new
        js = [j for j in self.alljs if j["object_id"] == f"{x}@{self.cc}" and any(k in new for k in split_list(j["evidence_item_ids"]))]
        return ("assessed" if js and all(j["review_status"] in ("validated", "overridden") for j in js) else "proposed"), new

    def progression(self, x):
        """2025 position, 2026 update, what changed, current direction and priority. Presentation of existing records only."""
        it = self.D["items"]
        ks = self.D["by"].get(x, [])
        p25 = [k for k in ks if it[k]["_source"] in self.rep25]
        o26 = [k for k in ks if it[k]["_source"] in self.other26]
        state, new = self.u26(x)
        J = self.views[x]["J"]
        latest = max(ks, key=lambda k: (it[k]["dates"].get("publication_date") or "", k)) if ks else None
        def summ(ids, n=4):
            return "<ul class=\"ints\">" + "".join(f'<li>{escape(it[k]["summary"])} <code>{escape(k)}</code></li>' for k in ids[:n]) + "</ul>" + \
                   (f'<p class="note">and {len(ids) - n} more in the references below.</p>' if len(ids) > n else "")
        if p25:
            pos25 = f'<p class="note">{len(p25)} item{"s" if len(p25) != 1 else ""} from the Commission\'s 2025 report on {escape(self.cname)}.</p>' + summ(p25) + self.refs(p25, "2025 report quotes")
        else:
            pos25 = '<p class="note">The 2025 report has no in-scope item on this issue; the alpha position rests on other sources (see the evidence below).</p>'
        if state == "awaiting":
            up26 = f'<p>{AWAIT}</p>'
        elif state == "no_new":
            up26 = '<p class="note">The 2026 report has no in-scope item on this issue.</p>'
        else:
            up26 = f'<p class="note">{len(new)} item{"s" if len(new) != 1 else ""} from the 2026 report.</p>' + summ(new) + self.refs(new, "2026 report quotes")
        if o26:
            up26 += (f'<p class="note">{VAL} Other 2026 official EU evidence already in the alpha, and already reflected in the current judgements '
                     f'({len(o26)} item{"s" if len(o26) != 1 else ""}; not the Enlargement Package):</p>' + summ(o26, 3) + self.refs(o26, "2026 official EU quotes held"))
        if state == "awaiting":
            chg = f'<p class="note">Not yet assessed. {AWAIT}</p>'
        elif state == "no_new":
            chg = '<p class="note">No new evidence on this issue in the 2026 report, so the judgements stand.</p>'
        else:
            rows = []
            for k in new:
                ls = [l for l in self.D["links"] if l["from_id"] == k and l["link_type"] in ("corroborates", "contradicts", "same_as_earlier", "replaces", "amends")]
                kind = ", ".join(sorted({l["link_type"].replace("_", " ") + ("" if l["review_status"] == "validated" else " (proposed)") for l in ls})) or "new: no earlier item linked"
                rows.append(f'<li><code>{escape(k)}</code> · {escape(kind)}</li>')
            sup = [j for j in self.alljs if j["object_id"] == f"{x}@{self.cc}" and j["supersedes"] and any(n in new for n in split_list(j["evidence_item_ids"]))]
            for j in sup:
                old = next((o for o in self.alljs if o["judgement_id"] == j["supersedes"]), {})
                lab = VAL if j["review_status"] in ("validated", "overridden") else lbl("Proposed", "synth")
                rows.append(f'<li><b>{escape(pretty(j["judgement_type"]))}</b>: {escape(pretty(old.get("value")))} &rarr; {escape(pretty(j["value"]))} {lab}</li>')
            chg = (lbl("Proposed", "synth") + " " if state == "proposed" else "") + f'<ul class="ints">{"".join(rows)}</ul>'
        def cur(t):
            j = J.get(t, {})
            pend = [n for n in self.alljs if n["supersedes"] == j.get("judgement_id") and n["review_status"] == "proposed"] if j else []
            extra = "".join(f' &rarr; <b>{escape(pretty(n["value"]))}</b> {lbl("Proposed", "synth")}' for n in pend)
            return f'<b>{escape(pretty(j.get("value")))}</b> {VAL}{extra}'
        latest_html = (f'{escape((it[latest]["dates"].get("publication_date") or "")[:10])}, {escape(self.D["reg"].get(it[latest]["_source"], {}).get("title", "")[:90])} '
                       f'<code>{escape(latest)}</code>') if latest else "none"
        strip = (f'<div class="prog"><span><b>2025 report:</b> {len(p25)} item{"s" if len(p25) != 1 else ""}</span>'
                 f'<span><b>2026 update:</b> {AWAIT if state == "awaiting" else escape({"no_new": "no new item", "proposed": "proposed", "assessed": "assessed"}[state])}</span></div>')
        block = (f'<details class="more prog26"><summary>2025 &rarr; 2026 comparison</summary><div class="detail"><dl class="kv">'
                 f'<dt>Latest evidence</dt><dd>{latest_html}</dd>'
                 f'<dt>2025 position</dt><dd>{pos25}</dd>'
                 f'<dt>2026 update</dt><dd>{up26}</dd>'
                 f'<dt>What changed</dt><dd>{chg}</dd>'
                 f'<dt>Current direction of travel</dt><dd>{cur("direction_of_travel")}</dd>'
                 f'<dt>Current priority</dt><dd>{cur("priority")}</dd></dl></div></details>')
        return state, strip, block

    def parse_options(self, x):
        body = narrative(self.root, self.run, f"comparator_{x}").get("Draft policy options", "")
        opts, cur = [], None
        for line in body.splitlines():
            m = re.match(r"^\*\*(Option \d+: .+?)\*\*\s*$", line)
            w = re.match(r"^\*\*(A warning[^*]+?)\*\*\s*$", line)
            n = re.match(r"^\*\*(Related step[^*]+?)\*\*\s*(.*)$", line)
            if m or w:
                cur = {"title": (m or w).group(1).rstrip("."), "fields": {}, "text": "", "warning": bool(w)}
                opts.append(cur)
            elif n:
                cur = {"title": n.group(1).rstrip("."), "fields": {}, "text": n.group(2), "note": True}
                opts.append(cur)
            elif cur is not None:
                fm = re.match(r"^- \*(.+?):\*\s*(.*)$", line)
                if fm:
                    cur["fields"][fm.group(1)] = fm.group(2)
                elif line.strip():
                    cur["text"] = (cur["text"] + " " + line.strip()).strip()
        return opts

    # Sections -----------------------------------------------------------------

    def overview(self):
        n_src = Counter(r["role"] for r in self.D["reg"].values())
        items = self.D["items"]
        mkd = sum(1 for i in items.values() if i["country"] == self.cc)
        pri = Counter(self.jv(r["issue_id"], "priority").get("value") for r in self.D["issues"])
        ncase = sum(len(v) for v in self.cases.values())
        nopt = sum(1 for v in self.opts.values() for o in v if o["title"].startswith("Option"))
        nwarn = sum(1 for v in self.opts.values() for o in v if o.get("warning"))
        rec = self.p.rec
        summ = narrative(self.root, self.run, "scope_overview").get("Summary", "")
        stats = [(f"{n_src['target'] + n_src['comparator']}", f"sources ({n_src['target']} {self.cname}, {n_src['comparator']} comparator)"),
                 (f"{len(items):,}", f"evidence items ({mkd:,} {self.cname})"),
                 (str(len(self.D["issues"])), f"reform issues ({sum(1 for r in self.D['issues'] if self.strand(r['issue_id']) == 'fmw')} Chapter 2, "
                                              f"{sum(1 for r in self.D['issues'] if self.strand(r['issue_id']) == 'tec')} technology)"),
                 (f"{pri['High']} / {pri['Medium']} / {pri['Low']}", "High / Medium / Low priority"),
                 (str(ncase), "comparator cases"),
                 (f"{nopt}" + (f" + {nwarn}" if nwarn else ""), "draft policy options" + (" + warning" if nwarn else ""))]
        hrefs = ["#evidence", "#evidence", "#issues", "#priority", "#comparators", "#options"]
        st = "".join(f'<div class="stat"><a href="{h}"><div class="n">{escape(a)}</div><div class="l">{escape(b)}</div></a></div>' for (a, b), h in zip(stats, hrefs))
        says = "".join(f"<li>{text(s)}</li>" for s in sentences(summ))
        return "overview", "Overview", (
            f'<p>{VAL} Outputs signed off at G7 ({escape(self.g7["gate_decision_id"])}); judgements validated at G6 and G6b. Draft policy options stay {DRAFT}.</p>'
            f'<dl class="kv"><dt>Country</dt><dd>{escape(rec.get("Target country", ""))}</dd>'
            f'<dt>Scope</dt><dd>Chapter 2 (Freedom of movement for workers) and the cross-cutting technology and AI theme; comparator pilot on {NUM.get(len(self.cases), len(self.cases))} issue{"s" if len(self.cases) != 1 else ""}</dd>'
            f'<dt>Evidence window</dt><dd>{escape(rec.get("Time window", "").split(";")[0])}; freeze date {escape(rec.get("Evidence freeze date", "").split(" ")[0])}</dd></dl>'
            f'<div class="stats">{st}</div>'
            f'<h3>What this analysis says {VAL}</h3><ul class="says">{says}</ul>'
            + self.banner() +
            '<p class="note">Jump straight to: <a href="#priority">the High-priority issues</a> · <a href="#issues">all issues, with filters</a> · '
            '<a href="#comparators">comparator lessons</a> · <a href="#options">draft policy options</a>.</p>')

    def issue_card(self, r):
        x, V, N = r["issue_id"], self.views[r["issue_id"]], self.narr[r["issue_id"]]
        J = V["J"]
        gap = what_remains(J.get("unresolved_gap", {}).get("reason", ""))
        ints = []
        for n in V["iids"]:
            j = V["status"].get(n, {})
            ints.append(f'<li>{escape(self.names.get(n, n))} <span class="st">· {escape(pretty(j.get("value")))}</span></li>')
        ints_html = f'<ul class="ints">{"".join(ints)}</ul>' if ints else '<p class="note">No country intervention is linked to this issue in the evidence.</p>'
        if len(ints) > 8:
            ints_html = f'<details class="refs"><summary>{len(ints)} interventions and their validated implementation status</summary>{ints_html}</details>'
        outc = []
        for l, s, a in V["outc"]:
            outc.append(f'<li>{escape(self.names.get(l["from_id"], l["from_id"]))}: {escape(self.D["items"][l["to_id"]]["summary"])} '
                        f'<span class="st">· success {escape(pretty(s["value"] if s else ""))}, attribution {escape(pretty(a["value"] if a else ""))}</span></li>')
        outc_html = f'<ul class="ints">{"".join(outc)}</ul>' if outc else '<p class="note">No stated outcome is linked to an intervention under this issue, so no success judgement was made.</p>'
        reasons = "".join(f'<p><b>{h}:</b> {text(J[t]["reason"])}</p>' for t, h in
                          (("unresolved_gap", "Unresolved gap"), ("direction_of_travel", "Direction of travel"), ("priority", "Priority"), ("tractability", "Tractability")) if t in J)
        conflicts = "".join(f'<li>{text(l["basis"])}</li>' for l in V["conflicts"])
        ids = list(V["key"]) + self.ids_in(N.get("In brief", ""), N.get("How the EU requirement has changed", ""), N.get("Open questions", ""))
        ids += [k for l in V["conflicts"] for k in (l["from_id"], l["to_id"])]
        kw = [self.themes.get(t, t) for t in split_list(r.get("themes", ""))] + [self.mechs.get(m, m) for m in split_list(r.get("mechanism_ids", ""))]
        brief = sentences(no_refs(N.get("In brief", "")))
        assess = brief[0] if brief else ""
        search = " ".join([x, r["label"], r["definition"], STRAND[self.strand(x)], gap, N.get("In brief", "")] + kw).lower()
        search = re.sub(r"\s+", " ", ITEM.sub("", search))
        oq = N.get("Open questions", "")
        oq_html = "<ul>" + "".join(f"<li>{text(l[2:])}</li>" for l in oq.splitlines() if l.startswith("- ")) + "</ul>" if oq else ""
        mt = lbl("Evidence limit: relies partly on machine translation", "limit") if V["mt"] else ""
        u_state, u_strip, u_block = self.progression(x)
        o26 = "held" if any(self.D["items"][k]["_source"] in self.other26 for k in self.D["by"].get(x, [])) else ""
        return (f'<article class="issue" id="{escape(x)}" data-strand="{self.strand(x)}" data-priority="{escape(J.get("priority", {}).get("value", ""))}" '
                f'data-direction="{escape(J.get("direction_of_travel", {}).get("value", ""))}" data-gap="{escape(J.get("unresolved_gap", {}).get("value", ""))}" '
                f'data-status="{" ".join(self.status(x))}" data-u26="{u_state} {o26}" data-search="{escape(search)}">'
                f'<div class="top"><a class="idlink" href="#{escape(x)}" title="Link to this issue">{escape(x)} · {STRAND[self.strand(x)]}</a><span>{self.status_labels(x)}</span></div>'
                f'<h4>{escape(r["label"])}</h4><div>{self.chips(x)}</div>'
                f'<p class="assess"><b>Assessment:</b> {text(assess)}</p>{u_strip}{u_block}'
                f'<p class="gap"><b>Unresolved gap ({escape(pretty(J.get("unresolved_gap", {}).get("value")))}):</b> {text(gap)}</p>'
                f'<details class="more"><summary>View detail</summary><div class="detail">'
                f'<h5>Assessment in brief</h5><p>{text(N.get("In brief", ""))}</p>'
                f'<h5>EU requirement</h5><p>{text(N.get("How the EU requirement has changed", ""))}</p>'
                f'<h5>Country response</h5>{ints_html}'
                f'<h5>Implementation and outcome</h5>{outc_html}'
                + (f'<h5>Conflicting evidence</h5><ul>{conflicts}</ul>' if conflicts else "")
                + f'<h5>Rationale for the judgements</h5>{reasons}'
                + (f'<h5>Open questions</h5>{oq_html}' if oq_html else "")
                + f'<h5>Evidence</h5><p class="note">{len(V["mine"])} in-scope items from {len(V["srcs"])} sources; {V["mt"]} machine translated. {mt}</p>'
                + self.refs(ids)
                + f'<p class="note">Full brief: <a href="{self.up}outputs/{escape(self.run)}/issue_brief_{escape(x)}.md">issue_brief_{escape(x)}.md</a></p>'
                + '</div></details></article>')

    def issues(self):
        dirs = sorted({self.jv(r["issue_id"], "direction_of_travel").get("value", "") for r in self.D["issues"]})
        gaps = sorted({self.jv(r["issue_id"], "unresolved_gap").get("value", "") for r in self.D["issues"]})
        opt = lambda vals: "".join(f'<option value="{escape(v)}">{escape(pretty(v))}</option>' for v in vals if v)
        filt = ('<div class="filters" role="search">'
                '<label>Search<input id="f-q" type="search" placeholder="Title, ID or keyword"></label>'
                '<label>Area<select id="f-strand"><option value="">All</option><option value="fmw">Chapter 2</option><option value="tec">Technology &amp; AI</option></select></label>'
                '<label>Priority<select id="f-pri"><option value="">All</option><option>High</option><option>Medium</option><option>Low</option></select></label>'
                f'<label>Direction of travel<select id="f-dir"><option value="">All</option>{opt(dirs)}</select></label>'
                f'<label>Unresolved gap<select id="f-gap"><option value="">All</option>{opt(gaps)}</select></label>'
                '<label>Judgement status<select id="f-st"><option value="">All</option>'
                + "".join(f'<option value="{k}">{escape(v)}</option>' for k, v in STATUS.items()) + '</select></label>'
                '<label>2026 update<select id="f-u26"><option value="">All</option><option value="awaiting">Awaiting 2026 Enlargement Package</option>'
                '<option value="held">Has 2026 official EU evidence already held</option><option value="proposed">2026 change proposed</option>'
                '<option value="assessed">2026 change validated</option><option value="no_new">No new 2026 report item</option></select></label>'
                '<button id="f-reset" type="button">Reset</button></div>'
                f'<p class="count" id="f-count" aria-live="polite">Showing {len(self.D["issues"])} of {len(self.D["issues"])} reform issues</p>')
        key = lambda r: (PRI.get(self.jv(r["issue_id"], "priority").get("value"), 3), r["issue_id"])
        groups = ""
        for s, gid in (("fmw", "chapter2"), ("tec", "tech")):
            rs = sorted((r for r in self.D["issues"] if self.strand(r["issue_id"]) == s), key=key)
            groups += (f'<div class="group" id="{gid}"><h3>{STRAND[s]} ({len(rs)} issues)</h3>'
                       + "".join(self.issue_card(r) for r in rs) + "</div>")
        return "issues", "Reform issues", (
            '<p class="note">Cards are sorted by priority. Each shows the validated judgements and the unresolved gap; <b>View detail</b> opens the EU requirement, '
            'country response, outcomes, rationale and the quoted evidence. Every card has its own link (the ID at the top left).</p>' + filt + groups)

    def priority(self):
        out = []
        hi = sorted((r for r in self.D["issues"] if self.jv(r["issue_id"], "priority").get("value") == "High"), key=lambda r: r["issue_id"])
        for r in hi:
            x = r["issue_id"]
            J = self.views[x]["J"]
            d, p_, g = J.get("direction_of_travel", {}), J.get("priority", {}), J.get("unresolved_gap", {})
            pids = split_list(p_.get("evidence_item_ids", ""))
            main = "".join(f'<li>{escape(self.D["items"][k]["summary"])} <code>{escape(k)}</code></li>' for k in pids if k in self.D["items"])
            ov = " (set by the analyst at G6)" if p_.get("review_status") == "overridden" else ""
            out.append(f'<div class="pcard" id="p-{escape(x)}"><div class="top"><a class="idlink" href="#{escape(x)}">{escape(x)} · {STRAND[self.strand(x)]} · open the issue card</a><span>{self.status_labels(x)}</span></div>'
                       f'<h4>{escape(r["label"])}</h4>'
                       f'<dl class="kv"><dt>Problem</dt><dd>{escape(r["definition"])}</dd>'
                       f'<dt>Why it matters</dt><dd>{text(p_.get("reason", ""))}{escape(ov)}</dd>'
                       f'<dt>Direction of travel</dt><dd><b>{escape(pretty(d.get("value")))}.</b> {text(" ".join(sentences(d.get("reason", ""))[:2]))}</dd>'
                       f'<dt>Main evidence</dt><dd><ul>{main}</ul>{self.refs(pids, "Quotes")}</dd>'
                       f'<dt>Unresolved gap</dt><dd><b>{escape(pretty(g.get("value")))}.</b> {text(what_remains(g.get("reason", "")))}</dd>'
                       f'<dt>2026 update</dt><dd>{AWAIT if self.u26(x)[0] == "awaiting" else escape(pretty(self.u26(x)[0]))} '
                       f'<a href="#{escape(x)}">2025 &rarr; 2026 comparison on the issue card</a></dd></dl></div>')
        idx = "".join(f'<li><a href="#p-{escape(r["issue_id"])}">{escape(r["label"])}</a> <span class="idlink">{escape(r["issue_id"])}</span></li>' for r in hi)
        return "priority", f"Priority issues ({len(hi)} High)", (
            f'<p>{VAL} The issues rated High priority at G6, in ID order. Every statement is taken from the validated judgements; '
            '"Why it matters" is the priority rationale.</p>'
            f'<details class="refs" open><summary>The {len(hi)} High-priority issues at a glance</summary><ol class="pindex">{idx}</ol></details>' + "".join(out))

    def comparators(self):
        parts = [("problem_addressed", "Problem addressed", False), ("reform_or_mechanism", "What was tried", False),
                 ("how_implemented", "How it was implemented", False), ("evidence_of_results", "Observed result", False),
                 ("limitations_of_evidence", "Limitations of the evidence", False),
                 ("practical_lesson", f"Practical lesson for {self.cname}", True),
                 ("transferable", "What could transfer", True), ("not_transferable", "Conditions and what does not transfer", True)]
        out = ""
        for x, cases in self.cases.items():
            r = next(i for i in self.D["issues"] if i["issue_id"] == x)
            body = ""
            for c in cases:
                cid = c["case_id"]
                rel, tr = self.J.get((cid, "comparator_relevance"), {}), self.J.get((cid, "transferability"), {})
                ids = [k for f in ("reform_items", "implementation_items", "outcome_items") for k in split_list(c.get(f, ""))]
                parts[5] = (lesson_field({0: c}), parts[5][1], True)
                rows = "".join(f'<dt>{escape(h)}{" " + SYN if syn else ""}</dt><dd>{text(c.get(f, ""))}</dd>' for f, h, syn in parts)
                body += (f'<div class="case" id="{escape(cid)}"><div class="top"><span class="idlink">{escape(cid)}</span><span>{VAL}</span></div>'
                         f'<h4>{escape(COUNTRIES.get(c["country"], c["country"]))}</h4>'
                         f'<div><span class="chip">Comparator relevance <b>{escape(rel.get("value", ""))}</b></span>'
                         f'<span class="chip">Transferability <b>{escape(tr.get("value", ""))}</b></span> {SYN}</div>'
                         f'<p>{text(self.ent.get(cid, {}).get("description", ""))}</p>'
                         f'<details class="more"><summary>View case</summary><div class="detail"><dl class="kv">{rows}'
                         f'<dt>Transferability judgement {SYN}</dt><dd><b>{escape(tr.get("value", ""))}.</b> {text(tr.get("reason", ""))}</dd>'
                         f'<dt>Why this comparator</dt><dd>{text(rel.get("reason", ""))}</dd></dl>'
                         + self.refs(ids, "Case evidence") + "</div></details></div>")
            lessons = narrative(self.root, self.run, f"comparator_{x}").get("Lessons across the cases", "")
            out += (f'<div class="compbox"><h3>{escape(r["label"])} <a class="idlink" href="#{escape(x)}">{escape(x)}</a></h3>'
                    f'<p><b>Lessons across the cases</b> {SYN} {text(lessons)}</p>{self.refs(self.ids_in(lessons))}{body}'
                    f'<p class="note">Full brief: <a href="{self.up}outputs/{escape(self.run)}/comparator_brief_{escape(x)}.md">comparator_brief_{escape(x)}.md</a></p></div>')
        return "comparators", "Comparators", (
            f'<p>{VAL} Comparator cases validated at G6b. The cases show what was tried, not what worked: no case shows a reform that measurably raised '
            f'use or changed access. Fields marked {SYN} are the tool\'s own reading across the evidence, validated by the analyst as conditional hypotheses; '
            'they are not stated by the sources.</p>' + out)

    def options(self):
        out = ""
        fields = [("Gap addressed", "Gap it addresses"), ("Mechanism targeted", "Problem it targets"),
                  ("Conditions and preconditions", "Preconditions"), ("Main risks", "Risks"), ("Who would need to act", "Responsible actor")]
        for x, opts in self.opts.items():
            r = next(i for i in self.D["issues"] if i["issue_id"] == x)
            cards = ""
            for o in opts:
                f = o["fields"]
                if o.get("note"):
                    cards += f'<p class="note"><b>{escape(o["title"])}.</b> {text(o["text"])}</p>'
                    continue
                comp = f.get("Comparator evidence", "") or o["text"]
                rationale, _, transfer = comp.partition("Transferability conditional")
                transfer = ("Conditional" + transfer) if transfer else ""
                countries = sorted(n for n in COUNTRIES.values() if n != self.cname and n in comp)
                kv = (f'<dt>{escape(self.cname)} issue</dt><dd><a href="#{escape(x)}">{escape(r["label"])}</a> ({escape(x)})</dd>'
                      f'<dt>Comparator it draws on</dt><dd>{escape(", ".join(countries) or "see rationale")}</dd>')
                if f.get("Gap addressed"):
                    kv += f'<dt>Gap it addresses</dt><dd>{text(f["Gap addressed"])}</dd>'
                kv += f'<dt>Rationale</dt><dd>{text(rationale.strip())}</dd>'
                if transfer:
                    kv += f'<dt>Transferability conditions {SYN}</dt><dd>{text(transfer.strip())}</dd>'
                for k, h in fields[1:]:
                    if f.get(k):
                        kv += f'<dt>{escape(h)}</dt><dd>{text(f[k])}</dd>'
                ids = self.ids_in(comp, *f.values())
                cards += (f'<div class="option"><div class="top"><span>{escape(x)}</span><span>{DRAFT} {SYN}</span></div>'
                          f'<h4>{escape(o["title"])}</h4><dl class="kv">{kv}</dl>{self.refs(ids)}</div>')
            out += f'<div class="compbox"><h3>{escape(r["label"])} <a class="idlink" href="#{escape(x)}">{escape(x)}</a></h3>{cards}</div>'
        return "options", "Draft policy options", (
            f'<p>{DRAFT} These options were signed off at G7 as <b>internal drafts</b>. They are not validated recommendations and have not been '
            'prepared for an external audience. Each rests on a validated unresolved gap and on comparator lessons that are agent synthesis, rated conditional. '
            'None is proposed because another country adopted it, and none is shown by the evidence to work.</p>' + out)

    def evidence(self):
        N = narrative(self.root, self.run, "coverage_and_limits")
        lim = [r for r in read_csv(self.root / "registers" / "limits_log.csv")[1] if r["run_id"] == self.run and r["status"] == "active"]
        rows = "".join(f'<li><code>{escape(r["limit_id"])}</code> <span class="st">{escape(r["limit_type"])}</span> · {escape(r["description"])}</li>' for r in lim)
        mkd = [i for i in self.D["items"].values() if i["country"] == self.cc and i["pass2"]["classification_status"] != "out_of_scope"]
        mt = sum(1 for i in mkd if i.get("machine_translated"))
        return "evidence", "Evidence and limits", (
            f'<p>{VAL} From the coverage and limits report signed off at G7.</p>'
            f'<h3>Source coverage</h3><p>{text(N.get("Summary", ""))}</p>'
            f'<p>{lbl("Evidence limit", "limit")} {mt:,} of {len(mkd):,} in-scope {escape(self.cname)} items ({100 * mt / max(len(mkd), 1):.0f}%) are machine translated, '
            'and their evidence confidence is capped at Medium. Source quality, evidence confidence and relevance are kept as separate judgements and never combined.</p>'
            f'<h3>Methodological limitations</h3><p>{text(N.get("Methodological limitations", ""))}</p>'
            f'<details class="refs"><summary>Active limits for this run ({len(lim)})</summary><ul class="ints">{rows}</ul></details>'
            f'<p class="note">Reports: <a href="{self.up}outputs/{escape(self.run)}/coverage_and_limits_report.md">coverage and limits report</a> · '
            f'<a href="{self.up}outputs/{escape(self.run)}/scope_overview.md">scope overview</a> · <a href="{self.up}runs/{escape(self.run)}/run_review.md">run review</a></p>')

    def render(self, css, version, today):
        secs = [self.overview(), self.issues(), self.priority(), self.comparators(), self.options(), self.evidence()]
        nav = ('<a href="#overview">Overview</a><a href="#chapter2" data-strand="fmw">Chapter 2</a><a href="#tech" data-strand="tec">Technology &amp; AI</a>'
               '<a href="#priority">Priority issues</a><a href="#comparators">Comparators</a><a href="#options">Policy options</a><a href="#evidence">Evidence and limits</a>')
        body = "".join(f'<section id="{sid}"><h2>{escape(title)}</h2>{content}<a class="totop" href="#top">Back to top</a></section>' for sid, title, content in secs)
        country = self.p.rec.get("Target country", "")
        status = self.T.get("status") or ("Completed run" if gate_passed(self.p.decisions, "G8") else "Outputs validated at G7")
        summ = self.T.get("summary") or f"summary/{self.cc}.html"
        summ = (f' · <a href="{self.up}{summ}">{escape(self.T.get("summary_label", "Country summary"))}</a>'
                if (self.root / summ).exists() else "")
        lang = self.T.get("lang", "translations from languages other than English are machine translations")
        return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(self.T.get("title", f"{self.cname} Accession Analysis"))}</title>
<!-- Generated by tools/build_review_page.py {version} on {today} from validated records only. Do not edit by hand: rebuild instead. -->
<style>{css}{CSS_EXTRA}</style>
</head>
<body>
<div class="wrap" id="top">
<header>
<h1>Analysis: {escape(country)}</h1>
<p class="sub">{escape(self.run)} · {escape(status)} · Page updated {escape(today)} · <a href="{self.up}analysis.html">All countries</a> · <a href="{self.up}index.html">Review page</a>{summ}</p>
</header>
<nav class="top" aria-label="Sections">{nav}</nav>
{body}
<footer><p>Generated from the validated records of {escape(self.run)} by <code>tools/build_review_page.py</code> {version}. Presentation only: it adds no analysis. Quotes are shown word for word with their item IDs; {lang}. <a href="#top">Back to top</a></p></footer>
</div>
<script>{JS}</script>
</body>
</html>
"""
