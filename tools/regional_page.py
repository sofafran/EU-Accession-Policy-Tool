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
from frontend import CSS as FE_CSS, badge, chip, display, header, run_status_text, tag
from product_page import CSS_EXTRA, NUM, PRI, VAL, lbl, no_refs, sentences, text

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
.grid { grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 12px; }
.ccard { border-radius: var(--radius); padding: 12px 14px; } .ccard.off { opacity: 1; background: var(--bg); }
.ccard .rs { font-weight: 600; color: var(--muted); margin: 0 0 4px; } .top3 { margin: 2px 0 8px; padding-left: 20px; font-size: .92rem; }
.ocb { font-weight: 700; text-decoration: none; border: 1px solid var(--accent); border-radius: 999px; padding: 3px 12px; display: inline-block; }
.dbar { display: flex; height: 10px; border-radius: 5px; overflow: hidden; border: 1px solid var(--border); margin: 4px 0 2px; }
.dbar .seg { display: block; height: 100%; } .seg.t-good { background: var(--good); } .seg.t-bad { background: var(--bad); } .seg.t-flat { background: var(--flat); opacity: .55; }
.seg.t-ie { background: repeating-linear-gradient(135deg, transparent 0 3px, var(--border) 3px 5px); }
.hm table { font-size: .86rem; } .hm th[scope=row] { font-weight: 500; min-width: 240px; } .hm th[scope=row] a { text-decoration: none; }
.hm td { min-width: 140px; } .hm td a { color: inherit; text-decoration: none; display: block; }
.hm-c.g-open { background: var(--gate-bg); box-shadow: inset 4px 0 0 var(--gate); } .hm-c.g-partly_addressed { background: color-mix(in srgb, var(--gate-bg) 45%, var(--surface)); box-shadow: inset 4px 0 0 color-mix(in srgb, var(--gate) 50%, transparent); }
.hm-c.g-largely_closed { background: var(--surface); }
.hm-c.t-good .ar { color: var(--good); } .hm-c.t-bad .ar { color: var(--bad); } .hm-c.t-flat .ar { color: var(--flat); } .hm-c .ar { font-weight: 700; }
.hm-e { background: transparent; outline: 1px dashed var(--border); outline-offset: -4px; }
.hm-all { font: inherit; font-size: .86rem; border: 1px solid var(--border); border-radius: 999px; padding: 3px 11px; background: var(--surface); color: var(--accent); cursor: pointer; margin-top: 8px; }
.lists { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px; margin: 10px 0; }
.flist { border: 1px solid var(--border); border-radius: 10px; padding: 8px 12px; } .flist ul { margin: 4px 0; padding-left: 18px; font-size: .92rem; }
"""

JS_REGION = r"""
(function () {
  var sel = document.getElementById('f-country');
  var f = { q: document.getElementById('m-q'), area: document.getElementById('m-area'), hi: document.getElementById('m-hi') };
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
      var ok = (!f.area.value || r.dataset.area === f.area.value) && hi && (!q || r.dataset.search.indexOf(q) !== -1);
      r.classList.toggle('hidden', !ok);
      if (ok) n++;
    });
    count.textContent = 'Showing ' + n + ' of ' + rows.length + ' reform issues';
  }
  sel.addEventListener('change', applyCountry);
  ['input', 'change'].forEach(function (ev) { Object.keys(f).forEach(function (k) { f[k].addEventListener(ev, applyMatrix); }); });
  document.getElementById('m-reset').addEventListener('click', function () { f.q.value = ''; f.area.value = ''; f.hi.checked = false; applyMatrix(); });
  document.querySelectorAll('.ccard button[data-pick]').forEach(function (b) {
    b.addEventListener('click', function () { sel.value = b.dataset.pick; applyCountry(); document.getElementById('headlines').scrollIntoView(); });
  });
  var links = Array.prototype.slice.call(document.querySelectorAll('nav.top a'));
  function spy() {
    var cur = null;
    links.forEach(function (a) { var t = document.getElementById(a.getAttribute('href').slice(1)); if (t && t.getBoundingClientRect().top <= 90) cur = a; });
    links.forEach(function (a) { a.classList.toggle('active', a === cur); });
  }
  document.querySelectorAll('.hm-all').forEach(function (b) {
    b.addEventListener('click', function () { document.querySelectorAll('#' + b.dataset.for + ' .hm-more').forEach(function (r) { r.classList.remove('hidden'); }); b.remove(); });
  });
  document.querySelectorAll('a.hm-row').forEach(function (a) {
    a.addEventListener('click', function () { f.q.value = ''; f.area.value = ''; f.hi.checked = false; f.q.value = a.dataset.issue.toLowerCase(); applyMatrix(); });
  });
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


def country_menu(root):
    """Countries for the shared header switcher: (code, name, page path from the project root or '', page is a draft)."""
    out = []
    for run, cc, name in planned_runs(root):
        page = f"analysis/{cc}.html" if (Path(root) / "analysis" / f"{cc}.html").exists() and (Path(root) / "runs" / run / "run_record.md").exists() else ""
        out.append((cc, name or country_name(cc), page, bool(page) and not gate_passed(gate_decisions(root, run), "G7")))
    return out


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
            rec = run_record(self.root, run)[0] if c["started"] else {}
            c["stage"] = rec.get("Current stage", "").split(";")[0].split(" (")[0].strip()
            c["freeze"] = rec.get("Evidence freeze date", "").split(" ")[0].rstrip(".")
            c["status"] = run_status_text(c["dec"], c["started"], c["stage"], alpha=run == "RUN-2026-01")
            self.countries.append(c)
        self.done = [c for c in self.countries if c["g6"]]

    # Helpers ------------------------------------------------------------------

    def v(self, c, x, t):
        return c["J"].get((x, t), {}).get("value", "")

    def href(self, c, x=None):
        return (c["page"] + (f"#{x}" if x else "")) if c["page"] and c["g7"] else ""  # issue anchors exist only on the product page, after G7

    def cell(self, c, x):
        p, d, g = self.v(c, x, "priority"), self.v(c, x, "direction_of_travel"), self.v(c, x, "unresolved_gap")
        if not (p or d or g):
            return f'<td class="cell" data-country="{escape(c["cc"])}"><span class="nj">Not assessed</span></td>'
        chips = badge("priority", p) + badge("direction_of_travel", d) + badge("unresolved_gap", g)
        h = self.href(c, x)
        inner = f'<a href="{escape(h)}" title="Open {escape(x)} on the {escape(c["name"])} page">{chips}</a>' if h else chips
        return f'<td class="cell" data-country="{escape(c["cc"])}">{inner}</td>'

    def area(self, x):
        return "fmw" if x.startswith("RI-FMW") else "tec"

    def tech_issue(self, r):
        return any(t.startswith("TECH") for t in split_list(r["themes"]))

    # Sections -----------------------------------------------------------------

    def countries_sec(self):
        cards = ""
        for c in self.countries:
            body = ""
            if c["g6"]:
                rs = sorted({x for x, _ in c["J"]}, key=lambda x: ({"High": 0, "Medium": 1, "Low": 2}.get(self.v(c, x, "priority"), 3),
                                                                     {"open": 0, "partly_addressed": 1}.get(self.v(c, x, "unresolved_gap"), 2), x))
                lab = {r["issue_id"]: r["label"] for r in self.issues}
                top = "".join(f'<li><a href="{escape(self.href(c, x) or "#compare")}">{escape(lab.get(x, x))}</a></li>' for x in rs[:3])
                d = Counter(self.v(c, x, "direction_of_travel") for x in rs)
                n = max(len(rs), 1)
                bar = "".join(f'<span class="seg t-{display("direction_of_travel", v)[2]}" style="width:{100 * d[v] / n:.1f}%" title="{escape(display("direction_of_travel", v)[0])}: {d[v]}"></span>'
                              for v in DIRS if d[v])
                legend = " · ".join(f"{escape(display('direction_of_travel', v)[0])} {d[v]}" for v in DIRS if d[v])
                body = (f'<p class="note">Top priority issues</p><ol class="top3">{top}</ol>'
                        f'<div class="dbar" aria-hidden="true">{bar}</div><p class="note">{legend}</p>')
            link = ""
            if c["page"] and c["g7"]:
                link = f'<a class="country-page ocb" href="{escape(c["page"])}">Open country</a>'
            elif c["page"]:
                link = f'{tag("Draft")} <a href="{escape(c["page"])}">Open draft country page</a>'
            if c["summary"]:
                link += f' · <a href="{escape(c["summary"])}">Summary</a>'
            pick = f' <button type="button" data-pick="{escape(c["cc"])}">Show here</button>' if c["g6"] else ""
            meta = f'Evidence cut-off {escape(c["freeze"])}' if c["started"] and c["freeze"] else ""
            cards += (f'<div class="ccard{"" if c["g6"] else " off"}" data-country="{escape(c["cc"])}"><h3>{escape(c["name"])}</h3>'
                      f'<p class="rs">{escape(c["status"])}</p>' + (f'<div class="meta">{meta}</div>' if meta else "")
                      + body + (f'<p>{link}{pick}</p>' if link or pick else "") + "</div>")
        opts = "".join(f'<option value="{escape(c["cc"])}">{escape(c["name"])}</option>' for c in self.done)
        return "countries", "Countries", (
            f'<p class="lede">{len(self.countries)} countries are planned, one run each, with the same method. Results appear here only after a country\'s '
            'judgements are validated at G6.</p>'
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
            says = "".join(f"<li>{text(no_refs(s))}</li>" for s in sentences(summ)[:4])
            out += (f'<div class="headline" data-country="{escape(c["cc"])}"><h3>{escape(c["name"])} {VAL}</h3>'
                    f'<p>{n} reform issues: {p["High"]} High, {p["Medium"]} Medium and {p["Low"]} Low priority; '
                    f'{d["persistent"]} persistent, {d["improving"]} improving and {d["worsening"]} worsening; '
                    f'{g["open"]} gaps open and {g["partly_addressed"]} partly addressed.</p>'
                    + (f'<ul class="says">{says}</ul><p class="note">{tag("Agent synthesis, validated at G7")} From the scope overview signed off at G7.</p>' if says else "")
                    + (f'<p><a href="{escape(c["page"])}">Open the {escape(c["name"])} page</a></p>' if self.href(c) else "") + "</div>")
        return "headlines", "Headline findings by country", out or '<p class="note">No country has validated results yet.</p>'

    def hm_cell(self, c, x):
        d, g = self.v(c, x, "direction_of_travel"), self.v(c, x, "unresolved_gap")
        if not (d or g):
            return f'<td class="hm-e" data-country="{escape(c["cc"])}"><span class="vh">Not assessed in this country</span></td>'
        dl, di, dt = display("direction_of_travel", d)
        gl = display("unresolved_gap", g)[0]
        inner = f'<span class="ar" aria-hidden="true">{di}</span> {escape(dl)}<br><small>Gap: {escape(gl)}</small>'
        h = self.href(c, x)
        inner = f'<a href="{escape(h)}">{inner}</a>' if h else inner
        ie = " ie" if "insufficient_evidence" in (d, g) else ""
        return f'<td class="hm-c t-{dt} g-{escape(g or "none")}{ie}" data-country="{escape(c["cc"])}">{inner}</td>'

    def heatmap(self, rows, sid):
        rows = sorted(rows, key=lambda r: (-sum(self.v(c, r["issue_id"], "priority") == "High" for c in self.done),
                                           -sum(self.v(c, r["issue_id"], "unresolved_gap") == "open" for c in self.done), r["issue_id"]))
        head = "".join(f'<th data-country="{escape(c["cc"])}">{escape(c["name"])}</th>' for c in self.done)
        body = "".join(f'<tr class="{"hm-more hidden" if i >= 12 else ""}"><th scope="row"><a href="#compare" class="hm-row" data-issue="{escape(r["issue_id"])}">{escape(r["label"])}</a></th>'
                       + "".join(self.hm_cell(c, r["issue_id"]) for c in self.done) + "</tr>" for i, r in enumerate(rows))
        more = f'<button type="button" class="hm-all" data-for="{sid}">Show all ({len(rows)})</button>' if len(rows) > 12 else ""
        one = ('<p class="note">Only one country has validated judgements so far, so the heatmap has one column. Comparison grows as further runs are validated.</p>'
               if len(self.done) == 1 else "")
        key = ('<p class="note">Cells show direction of travel (arrow and label) and unresolved gap (fill strength: darker means more open). A blank, outlined cell means the '
               'issue was not assessed in that country. Rows: issues rated High priority in most countries first, then those with an open gap.</p>')
        return (one + key + f'<div class="mx hm" id="{sid}"><table><thead><tr><th>Reform issue</th>{head}</tr></thead><tbody>{body}</tbody></table></div>{more}')

    def pattern(self):
        rows = [r for r in self.issues if any(self.v(c, r["issue_id"], "priority") for c in self.done)]
        return "pattern", "Regional pattern", (self.heatmap(rows, "hm-all") if rows and self.done else '<p class="note">No country has validated results yet.</p>')

    def tech(self):
        rows = [r for r in self.issues if self.tech_issue(r) and any(self.v(c, r["issue_id"], "priority") for c in self.done)]
        if not (rows and self.done):
            return "tech", "Technology and AI", '<p class="note">No country has validated Technology and AI judgements yet.</p>'
        d = Counter(self.v(c, r["issue_id"], "direction_of_travel") for c in self.done for r in rows if self.v(c, r["issue_id"], "direction_of_travel"))
        split = " · ".join(f"{escape(display('direction_of_travel', v)[0])} {d[v]}" for v in DIRS if d[v])
        def li(c, r):
            h = self.href(c, r["issue_id"])
            return f'<li>{escape(c["name"])}: <a href="{escape(h or "#compare")}">{escape(r["label"])}</a></li>'
        prog = "".join(li(c, r) for c in self.done for r in rows if self.v(c, r["issue_id"], "direction_of_travel") in ("improving", "largely_resolved"))
        lag = []
        for c in self.done:
            for r in rows:
                if self.v(c, r["issue_id"], "unresolved_gap") == "open":
                    lag.append(li(c, r))
        shared = [r for r in rows if sum(self.v(c, r["issue_id"], "unresolved_gap") == "open" for c in self.done) >= 2]
        sh = ("<ul>" + "".join(f'<li>{escape(r["label"])}: gap open in {sum(self.v(c, r["issue_id"], "unresolved_gap") == "open" for c in self.done)} of {len(self.done)} countries</li>' for r in shared) + "</ul>"
              if shared else '<p class="note">No shared open gaps yet: this needs validated results from at least two countries.</p>')
        return "tech", "Technology and AI", (
            f'<div class="stats"><div class="stat"><div class="n">{len(rows)}</div><div class="l">Technology and AI issues judged</div></div>'
            f'<div class="stat"><div class="n">{len(self.done)}</div><div class="l">countries with validated results</div></div></div>'
            f'<p class="note">Direction of travel: {split}. Issues carry a Technology and AI theme code from the shared theme list.</p>'
            + self.heatmap(rows, "hm-tech")
            + f'<div class="lists"><details class="flist" open><summary><b>Where governments are making progress</b></summary><p class="note">Direction of travel improving or largely resolved.</p><ul>{prog or "<li>None</li>"}</ul></details>'
            f'<details class="flist"><summary><b>Where implementation is lagging</b> ({len(lag)})</summary><p class="note">Unresolved gap open.</p><ul>{"".join(lag) or "<li>None</li>"}</ul></details>'
            f'<details class="flist" open><summary><b>Shared open gaps</b></summary>{sh}</details></div>'
            '<p class="note">Shared gaps may indicate where advisory support is relevant. That assessment is made by colleagues, not by the tool.</p>'
            '<p class="note">On each country page, the Theme filter has a Technology and AI preset.</p>')

    def compare(self):
        areas = '<option value="fmw">Chapter 2</option><option value="tec">Technology and AI</option>'
        head = "".join(f'<th data-country="{escape(c["cc"])}">{escape(c["name"])}<br><small>{escape(c["status"])}</small></th>' for c in self.done)
        body = ""
        for r in self.issues:
            x = r["issue_id"]
            high = " ".join(c["cc"] for c in self.done if self.v(c, x, "priority") == "High")
            search = " ".join([x, r["label"], r["definition"], *[self.themes.get(t, t) for t in split_list(r["themes"])]]).lower()
            pat = ""
            if len(self.done) > 1:
                n_open = sum(self.v(c, x, "unresolved_gap") == "open" for c in self.done)
                pat = f'<br><small>Gap open in {n_open} of {len(self.done)} countries</small>'
            body += (f'<tr data-area="{self.area(x)}" data-themes="{escape(" ".join(split_list(r["themes"])))}" data-high="{escape(high)}" data-search="{escape(search)}" data-issue="{escape(x)}">'
                     f'<td class="issue-l"><b>{escape(r["label"])}</b><br><span class="idlink">{escape(x)}</span>{pat}</td>'
                     + "".join(self.cell(c, x) for c in self.done) + "</tr>")
        return "compare", "Compare an issue across countries", (
            f'<p>Every reform issue in the shared taxonomy ({len(self.issues)}), with each country\'s validated priority, direction of travel and unresolved gap. '
            '"Not assessed" means the country\'s evidence produced no judgement on that issue. Choosing a country above narrows the columns.</p>'
            '<div class="filters"><label>Search<input type="search" id="m-q" placeholder="Issue name or ID"></label>'
            f'<label>Area<select id="m-area"><option value="">All</option>{areas}</select></label>'
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

    def period(self):
        fz = sorted(c["freeze"] for c in self.done if c.get("freeze"))
        return f"2020 to {fz[-1]}" if fz else "from 2020"

    def render(self, css):
        secs = [self.countries_sec(), self.headlines(), self.pattern(), self.tech(), self.compare(), self.about()]
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
<style>{css}{FE_CSS}{CSS_EXTRA}{CSS_REGION}</style>
</head>
<body>
<div class="wrap" id="top">
{header("", [("Region", "")], country_menu(self.root))}
<div class="pagehead"><h1>EU accession reform analysis</h1>
<p class="runline">Chapter 2 (Freedom of movement for workers) and Technology and AI recommendations · {NUM.get(n, n)} of {NUM.get(len(self.countries), len(self.countries))} countries with validated results · Evidence {escape(self.period())} · Page updated {escape(self.today)} · <a href="index.html">Review page</a></p></div>
<nav class="top" aria-label="Sections">{nav}</nav>
{body}
<footer><p>Generated from validated records by <code>tools/build_review_page.py</code> {self.version}. Presentation only: it adds no analysis. <a href="#top">Back to top</a></p></footer>
</div>
<script>{JS_REGION}</script>
</body>
</html>
"""
