"""The regional landing page, analysis.html (decision E19): country selection, headline findings by country, priority reform
issues, technology and AI themes and the same issue compared across countries, with links into each country page
analysis/<country code>.html.

Called by build_review_page.py. Presentation only: it adds no analysis. A country's judgements appear only once its run has
passed G6, and only judgements that are validated or overridden and not superseded by a later validated row. Headline text
appears only once G7 has signed off the outputs it comes from. Countries come from the table in runs/rollout_plan.md.
One self-contained file with inline CSS and JavaScript."""

import re
from collections import Counter
from html import escape
from pathlib import Path

from build_outputs import narrative
from common import country_name, gate_decisions, gate_passed, parse_markdown_table, read_csv, run_record, split_list
from product_page import CSS_EXTRA, NUM, PRI, VAL, lbl, sentences, text

TYPES = ("priority", "direction_of_travel", "unresolved_gap", "tractability")
DIRS = ("worsening", "persistent", "new", "improving", "largely_resolved", "insufficient_evidence")
GAPS = ("open", "partly_addressed", "largely_closed", "closed", "insufficient_evidence")

CSS_REGION = """
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 10px; margin: 10px 0; }
.ccard { border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; background: var(--surface); }
.ccard h3 { margin: 0 0 4px; font-size: 1rem; }
.ccard .meta { font-size: .82rem; color: var(--muted); margin: 2px 0 6px; }
.ccard.off { opacity: .72; }
.ccard.sel { border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent); }
.lbl.draft { background: var(--proposed-bg); color: var(--proposed-fg); }
.lbl.none { background: var(--notstarted-bg); color: var(--notstarted-fg); }
.mx { overflow-x: auto; border: 1px solid var(--border); border-radius: 8px; }
.mx table { border-collapse: collapse; width: 100%; font-size: .86rem; }
.mx th, .mx td { border-bottom: 1px solid var(--border); padding: 6px 8px; text-align: left; vertical-align: top; }
.mx th { position: sticky; top: 0; background: var(--bg); font-weight: 600; }
.mx td.issue-l { min-width: 220px; }
.cell a { text-decoration: none; color: inherit; display: block; }
.cell a:hover .chip, .cell a:focus .chip { border-color: var(--accent); }
.cell .nj { color: var(--muted); font-size: .8rem; }
.headline { border: 1px solid var(--border); border-left: 4px solid var(--accent); border-radius: 8px; padding: 10px 14px; margin: 10px 0; background: var(--surface); }
.headline h3 { margin: 0 0 6px; }
.theme { border: 1px solid var(--border); border-radius: 8px; padding: 8px 14px; margin: 10px 0; background: var(--surface); }
"""

JS_REGION = r"""
(function () {
  var sel = document.getElementById('f-country');
  var f = { q: document.getElementById('m-q'), area: document.getElementById('m-area'), theme: document.getElementById('m-theme'), hi: document.getElementById('m-hi') };
  var rows = Array.prototype.slice.call(document.querySelectorAll('#compare tbody tr'));
  var count = document.getElementById('m-count');
  function country() { return sel.value; }
  function applyCountry() {
    var c = country();
    document.querySelectorAll('[data-country]').forEach(function (el) {
      if (el.classList.contains('ccard')) { el.classList.toggle('sel', !!c && el.dataset.country === c); return; }
      el.classList.toggle('hidden', !!c && el.dataset.country !== c);
    });
    var open = document.getElementById('open-country');
    var card = c && document.querySelector('.ccard[data-country="' + c + '"] a.country-page');
    open.classList.toggle('hidden', !card);
    if (card) open.setAttribute('href', card.getAttribute('href'));
    applyMatrix();
  }
  function applyMatrix() {
    var q = f.q.value.trim().toLowerCase(), c = country(), n = 0;
    rows.forEach(function (r) {
      var hi = f.hi.checked ? (c ? (' ' + r.dataset.high + ' ').indexOf(' ' + c + ' ') !== -1 : r.dataset.high !== '') : true;
      var ok = (!f.area.value || r.dataset.area === f.area.value) && (!f.theme.value || (' ' + r.dataset.themes + ' ').indexOf(' ' + f.theme.value + ' ') !== -1) &&
               hi && (!q || r.dataset.search.indexOf(q) !== -1);
      r.classList.toggle('hidden', !ok);
      if (ok) n++;
    });
    count.textContent = 'Showing ' + n + ' of ' + rows.length + ' reform issues';
  }
  sel.addEventListener('change', applyCountry);
  ['input', 'change'].forEach(function (ev) { Object.keys(f).forEach(function (k) { f[k].addEventListener(ev, applyMatrix); }); });
  document.getElementById('m-reset').addEventListener('click', function () { f.q.value = ''; f.area.value = ''; f.theme.value = ''; f.hi.checked = false; applyMatrix(); });
  document.querySelectorAll('.ccard button[data-pick]').forEach(function (b) {
    b.addEventListener('click', function () { sel.value = b.dataset.pick; applyCountry(); document.getElementById('headlines').scrollIntoView(); });
  });
  var links = Array.prototype.slice.call(document.querySelectorAll('nav.top a'));
  function spy() {
    var cur = null;
    links.forEach(function (a) { var t = document.getElementById(a.getAttribute('href').slice(1)); if (t && t.getBoundingClientRect().top <= 90) cur = a; });
    links.forEach(function (a) { a.classList.toggle('active', a === cur); });
  }
  window.addEventListener('scroll', spy, { passive: true });
  var m = /[?&]country=([A-Z]{3})/.exec(location.search);
  if (m && sel.querySelector('option[value="' + m[1] + '"]')) sel.value = m[1];
  applyCountry();
  spy();
})();
"""


def planned_runs(root):
    """(run_id, country code, country name) for every run in the rollout plan table, in plan order."""
    path = Path(root) / "runs" / "rollout_plan.md"
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    for i, line in enumerate(lines):
        if line.startswith("| Run |"):
            for r in parse_markdown_table(lines[i:])[1:]:
                if re.fullmatch(r"RUN-\d{4}-\d{2}", r[0]) and len(r) >= 3:
                    out.append((r[0], r[2], r[1]))
            break
    return out


def current_judgements(rows, run, cc):
    """Validated or overridden issue judgements of one run and country that no later validated row supersedes,
    as {(issue_id, type): row}."""
    ok = [j for j in rows if j["run_id"] == run and j["object_type"] == "issue_country" and j["object_id"].endswith("@" + cc)
          and j["review_status"] in ("validated", "overridden")]
    gone = {s for j in ok for s in split_list(j.get("supersedes", ""))}
    cur = {}
    for j in sorted(ok, key=lambda j: j["judgement_id"]):
        if j["judgement_id"] not in gone:
            cur[(j["object_id"].split("@")[0], j["judgement_type"])] = j
    return cur


class RegionalPage:
    def __init__(self, root, today, version):
        self.root, self.today, self.version = Path(root), today, version
        alljs = read_csv(self.root / "judgements" / "judgements.csv")[1]
        self.issues = [r for r in read_csv(self.root / "taxonomy" / "reform_issues.csv")[1] if r["status"] == "approved"]
        self.themes = {r["theme_code"]: r["label"] for r in read_csv(self.root / "taxonomy" / "themes.csv")[1]}
        self.countries = []
        for run, cc, name in planned_runs(self.root):
            c = dict(run=run, cc=cc, name=name or country_name(cc), started=(self.root / "runs" / run / "run_record.md").exists())
            c["dec"] = gate_decisions(self.root, run) if c["started"] else {}
            c["g6"] = gate_passed(c["dec"], "G6")
            c["g7"] = gate_passed(c["dec"], "G7")
            c["J"] = current_judgements(alljs, run, cc) if c["g6"] else {}
            c["page"] = f"analysis/{cc}.html" if (self.root / "analysis" / f"{cc}.html").exists() else ""
            c["summary"] = next((p for p in ("alpha_summary.html" if run == "RUN-2026-01" else "", f"summary/{cc}.html") if p and (self.root / p).exists()), "")
            c["stage"] = run_record(self.root, run)[0].get("Current stage", "").split(";")[0].split(" (")[0].strip() if c["started"] else ""
            self.countries.append(c)
        self.done = [c for c in self.countries if c["g6"]]

    # Helpers ------------------------------------------------------------------

    def v(self, c, x, t):
        return c["J"].get((x, t), {}).get("value", "")

    def status(self, c):
        if c["g6"]:
            g = "G8" if gate_passed(c["dec"], "G8") else ("G7" if c["g7"] else "G6")
            return VAL + f' <span class="note">{ {"G6": "judgements validated at G6", "G7": "outputs signed off at G7", "G8": "run completed"}[g] }</span>'
        if c["started"]:
            return lbl("Draft", "draft") + f' <span class="note">in progress: {escape(c["stage"])}</span>'
        return lbl("Not started", "none")

    def href(self, c, x=None):
        return (c["page"] + (f"#{x}" if x else "")) if c["page"] and c["g7"] else ""  # issue anchors exist only on the product page, after G7

    def cell(self, c, x):
        p, d, g = self.v(c, x, "priority"), self.v(c, x, "direction_of_travel"), self.v(c, x, "unresolved_gap")
        if not (p or d or g):
            return '<td class="cell" data-country="{0}"><span class="nj">not raised</span></td>'.format(escape(c["cc"]))
        chips = (f'<span class="chip {escape(p)}">Priority <b>{escape(p or "n/a")}</b></span>'
                 f'<span class="chip">{escape((d or "n/a").replace("_", " "))}</span><span class="chip">gap {escape((g or "n/a").replace("_", " "))}</span>')
        h = self.href(c, x)
        inner = f'<a href="{escape(h)}" title="Open {escape(x)} on the {escape(c["name"])} page">{chips}</a>' if h else chips
        return f'<td class="cell" data-country="{escape(c["cc"])}">{inner}</td>'

    def area(self, x):
        return "fmw" if x.startswith("RI-FMW") else "tec"

    # Sections -----------------------------------------------------------------

    def countries_sec(self):
        cards = ""
        for c in self.countries:
            n = len({x for x, _ in c["J"]})
            hi = sum(1 for (x, t), j in c["J"].items() if t == "priority" and j["value"] == "High")
            links = ""
            if c["page"]:
                links += (f'<a class="country-page" href="{escape(c["page"])}">Country page</a>' if c["g7"]
                          else f'<a href="{escape(c["page"])}">Work-in-progress page (draft review aid)</a>')
            if c["summary"]:
                links += (" · " if links else "") + f'<a href="{escape(c["summary"])}">Summary</a>'
            pick = f' · <button type="button" data-pick="{escape(c["cc"])}">Show here</button>' if c["g6"] else ""
            cards += (f'<div class="ccard{"" if c["g6"] else " off"}" data-country="{escape(c["cc"])}"><h3>{escape(c["name"])}</h3>'
                      f'<div class="meta">{escape(c["run"])} · {escape(c["cc"])}</div><div>{self.status(c)}</div>'
                      + (f'<p class="note">{n} reform issues judged, {hi} High priority</p>' if c["g6"] else "")
                      + (f'<p class="note">{links}{pick}</p>' if links or pick else "") + "</div>")
        opts = "".join(f'<option value="{escape(c["cc"])}">{escape(c["name"])}</option>' for c in self.done)
        return "countries", "Countries", (
            f'<p>{len(self.countries)} countries are planned, one run each, with the same method. A country\'s results appear here only after its '
            'judgements are validated at G6; until then it is shown as <b>Draft</b> or <b>Not started</b>.</p>'
            f'<div class="filters"><label>Country<select id="f-country"><option value="">All countries with validated results</option>{opts}</select></label>'
            '<a id="open-country" class="hidden" href="#">Open the country page</a></div>'
            f'<div class="grid">{cards}</div>')

    def headlines(self):
        out = ""
        for c in self.done:
            cnt = lambda t: Counter(j["value"] for (x, tt), j in c["J"].items() if tt == t)
            p, d, g = cnt("priority"), cnt("direction_of_travel"), cnt("unresolved_gap")
            n = len({x for x, _ in c["J"]})
            summ = narrative(self.root, c["run"], "scope_overview").get("Summary", "") if c["g7"] else ""
            says = "".join(f"<li>{text(s)}</li>" for s in sentences(summ)[:4])
            out += (f'<div class="headline" data-country="{escape(c["cc"])}"><h3>{escape(c["name"])} {VAL}</h3>'
                    f'<p>{n} reform issues: {p["High"]} High, {p["Medium"]} Medium and {p["Low"]} Low priority; '
                    f'{d["persistent"]} persistent, {d["improving"]} improving and {d["worsening"]} worsening; '
                    f'{g["open"]} gaps open and {g["partly_addressed"]} partly addressed.</p>'
                    + (f'<ul class="says">{says}</ul><p class="note">From the scope overview signed off at G7.</p>' if says else "")
                    + (f'<p><a href="{escape(c["page"])}">Open the {escape(c["name"])} page</a></p>' if self.href(c) else "") + "</div>")
        return "headlines", "Headline findings by country", out or '<p class="note">No country has validated results yet.</p>'

    def priority(self):
        hi = [r for r in self.issues if any(self.v(c, r["issue_id"], "priority") == "High" for c in self.done)]
        hi.sort(key=lambda r: (-sum(self.v(c, r["issue_id"], "priority") == "High" for c in self.done), r["issue_id"]))
        head = "".join(f'<th data-country="{escape(c["cc"])}">{escape(c["name"])}</th>' for c in self.done)
        body = "".join(f'<tr><td class="issue-l"><b>{escape(r["label"])}</b><br><span class="idlink">{escape(r["issue_id"])}</span></td>'
                       + "".join(self.cell(c, r["issue_id"]) for c in self.done) + "</tr>" for r in hi)
        return "priority", "Priority reform issues", (
            f'<p>Issues rated High priority in at least one country ({len(hi)}), with the most widely shared first. Open a cell to go to that issue '
            'on the country page.</p>' + (f'<div class="mx"><table><thead><tr><th>Reform issue</th>{head}</tr></thead><tbody>{body}</tbody></table></div>' if hi else ""))

    def tech(self):
        out = ""
        for code, label in self.themes.items():
            rs = [r for r in self.issues if code in split_list(r["themes"])]
            if not rs:
                continue
            per = ""
            for c in self.done:
                judged = [r for r in rs if self.v(c, r["issue_id"], "priority")]
                hi = [r for r in judged if self.v(c, r["issue_id"], "priority") == "High"]
                per += (f'<li data-country="{escape(c["cc"])}"><b>{escape(c["name"])}:</b> {len(judged)} issue{"s" if len(judged) != 1 else ""} judged, '
                        f'{len(hi)} High priority' + (": " + ", ".join(f'<a href="{escape(self.href(c, r["issue_id"]) or "#compare")}">{escape(r["label"])}</a>' for r in hi) if hi else "")
                        + "</li>")
            out += (f'<div class="theme" id="theme-{escape(code)}"><h3>{escape(label)} <span class="idlink">{escape(code)}</span></h3>'
                    f'<p class="note">{len(rs)} reform issues in the shared taxonomy carry this theme.</p><ul class="ints">{per}</ul></div>')
        return "tech", "Technology and AI themes", (
            '<p>The cross-cutting technology and AI theme, by area. An issue can carry more than one theme.</p>' + out)

    def compare(self):
        areas = '<option value="fmw">Chapter 2</option><option value="tec">Technology and AI</option>'
        themes = "".join(f'<option value="{escape(k)}">{escape(v)}</option>' for k, v in self.themes.items())
        head = "".join(f'<th data-country="{escape(c["cc"])}">{escape(c["name"])}</th>' for c in self.done)
        body = ""
        for r in self.issues:
            x = r["issue_id"]
            high = " ".join(c["cc"] for c in self.done if self.v(c, x, "priority") == "High")
            search = " ".join([x, r["label"], r["definition"], *[self.themes.get(t, t) for t in split_list(r["themes"])]]).lower()
            body += (f'<tr data-area="{self.area(x)}" data-themes="{escape(" ".join(split_list(r["themes"])))}" data-high="{escape(high)}" data-search="{escape(search)}">'
                     f'<td class="issue-l"><b>{escape(r["label"])}</b><br><span class="idlink">{escape(x)}</span></td>'
                     + "".join(self.cell(c, x) for c in self.done) + "</tr>")
        return "compare", "Compare an issue across countries", (
            f'<p>Every reform issue in the shared taxonomy ({len(self.issues)}), with each country\'s validated priority, direction of travel and unresolved gap. '
            '"Not raised" means the country\'s evidence produced no judgement on that issue. Choosing a country above narrows the columns.</p>'
            '<div class="filters"><label>Search<input type="search" id="m-q" placeholder="Issue, ID or theme"></label>'
            f'<label>Area<select id="m-area"><option value="">All</option>{areas}</select></label>'
            f'<label>Theme<select id="m-theme"><option value="">All</option>{themes}</select></label>'
            '<label><span>High priority only</span><input type="checkbox" id="m-hi"></label><button type="button" id="m-reset">Reset</button></div>'
            '<p class="count" id="m-count"></p>'
            + (f'<div class="mx"><table><thead><tr><th>Reform issue</th>{head}</tr></thead><tbody>{body}</tbody></table></div>' if self.done else
               '<p class="note">No country has validated results yet.</p>'))

    def about(self):
        return "about", "How to read this page", (
            '<ul class="says"><li>All countries are analysed with the same method and one shared list of reform issues, so the same issue can be compared '
            'across countries. A new country can add issues to the shared list only through a gate.</li>'
            '<li>Only judgements validated at a country\'s G6 are shown, with the latest validated value where a judgement was re-run. Nothing proposed or '
            'in progress is compared.</li>'
            '<li>Priority, direction of travel and gap are judgements about each country on its own evidence. A difference between countries is a prompt to '
            'read both country pages, not a ranking.</li>'
            '<li>The country pages hold the evidence, quotes, comparator cases and draft policy options (internal drafts).</li></ul>')

    def render(self, css):
        secs = [self.countries_sec(), self.headlines(), self.priority(), self.tech(), self.compare(), self.about()]
        nav = "".join(f'<a href="#{sid}">{escape(t)}</a>' for sid, t, _ in secs)
        body = "".join(f'<section id="{sid}"><h2>{escape(t)}</h2>{c}<a class="totop" href="#top">Back to top</a></section>' for sid, t, c in secs)
        n = len(self.done)
        return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Accession Reform Analysis</title>
<!-- Generated by tools/build_review_page.py {self.version} on {self.today} from validated records only. Do not edit by hand: rebuild instead. -->
<style>{css}{CSS_EXTRA}{CSS_REGION}</style>
</head>
<body>
<div class="wrap" id="top">
<header>
<h1>EU accession reform analysis</h1>
<p class="sub">Chapter 2 (Freedom of movement for workers) and technology and AI · {NUM.get(n, n)} of {NUM.get(len(self.countries), len(self.countries))} countries with validated results · Page updated {escape(self.today)} · <a href="index.html">Review page</a></p>
</header>
<nav class="top" aria-label="Sections">{nav}</nav>
{body}
<footer><p>Generated from validated records by <code>tools/build_review_page.py</code> {self.version}. Presentation only: it adds no analysis. <a href="#top">Back to top</a></p></footer>
</div>
<script>{JS_REGION}</script>
</body>
</html>
"""
