"""The analysis page once a run's outputs have passed G7: an easy-to-navigate product page built only from validated
records (issue judgements, signed-off outputs and their narrative inputs, comparator cases and draft options).
Called by build_review_page.py; adds no analysis of its own. One self-contained file with inline CSS and JavaScript."""

import json
import re
from collections import Counter
from html import escape

from build_outputs import COUNTRIES, issue_view, lesson_field, load, narrative, names_of, quality
from common import gate_decisions, gate_passed, read_csv, review_page_name, split_list
from frontend import CSS as FE_CSS, STATUSES, badge, chip, display, header, issue_status, judgement_status, run_status_text, tag

ITEM = re.compile(r"\b[A-Z]{3}-(?:EU|GOV|CSO|IO|RES|MED|INT)-\d{4}-\d{3}-\d{4}\b")
PRI = {"High": 0, "Medium": 1, "Low": 2}
STRAND = {"fmw": "Chapter 2", "tec": "Technology and AI"}
STEP_KEYS = ("eu_requirement", "country_response", "implementation", "outcome", "unresolved_gap", "lesson")

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
.igrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 12px; }
.igrid .issue { margin: 0; display: flex; flex-direction: column; border-radius: var(--radius); }
.tags { margin: 0 0 6px; } .tags .tag { margin: 0 4px 2px 0; }
.req { font-size: .92rem; } .eu { display: inline-block; font-size: .7rem; font-weight: 700; color: var(--in); background: var(--in-bg); border-radius: 4px; padding: 0 5px; margin-right: 4px; }
.badges { margin: 4px 0 6px; } .meta { font-size: .86rem; color: var(--muted); margin: 4px 0; }
.clamp p { display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 2px; }
.clamp.expanded p { -webkit-line-clamp: unset; display: block; }
.moret, .evb, .pclose, #dr-close, #dr-all, .fchip { font: inherit; font-size: .86rem; border: 1px solid var(--border); border-radius: 999px; padding: 3px 11px; background: var(--surface); color: var(--accent); cursor: pointer; }
.evb { font-weight: 600; border-color: var(--accent); }
a.open { display: inline-block; font-weight: 700; text-decoration: none; border: 1px solid var(--accent); border-radius: 999px; padding: 4px 14px; margin-top: auto; }
.issue > p:last-of-type { margin-top: auto; }
.fchips { display: flex; flex-wrap: wrap; gap: 6px; margin: 0 0 6px; } .fchip.clear { color: var(--muted); }
.panel { display: none; }
.issue.open .panel { display: block; position: fixed; inset: 0; z-index: 30; background: var(--bg); overflow-y: auto; padding: 16px; }
body.noscroll { overflow: hidden; }
.pin { max-width: 1000px; margin: 0 auto; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 18px 22px; }
.ptop { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
.pin h2 { font-size: 1.45rem; margin: 6px 0; } .def { color: var(--muted); }
.hbs { display: flex; flex-wrap: wrap; gap: 6px 16px; margin: 6px 0 10px; } .hb { display: flex; align-items: center; gap: 4px; }
.brief { border-left: 4px solid var(--accent); padding-left: 12px; }
ol.chain { list-style: none; padding: 0; margin: 14px 0; counter-reset: st; }
.step { display: grid; grid-template-columns: 200px 1fr auto; gap: 6px 16px; padding: 12px 0; border-top: 1px solid var(--border); }
.step .sl b { display: block; } .step .ss > :last-child { margin-bottom: 0; }
.step > .se { text-align: right; }
.kind { display: inline-block; font-size: .72rem; font-weight: 700; padding: 1px 7px; border-radius: 4px; margin-top: 2px; }
.k-stated .kind { background: var(--in-bg); color: var(--in); } .k-assessed .kind { background: var(--judg-bg); color: var(--judg); }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.small { font-size: .8rem; color: var(--muted); }
.cgrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 10px; }
.tgrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; margin: 8px 0 14px; }
.tcard { display: flex; flex-direction: column; gap: 6px; text-decoration: none; color: inherit; border: 1px solid var(--border); border-radius: var(--radius); padding: 10px 12px; background: var(--surface); }
.tcard:hover, .tcard:focus { border-color: var(--accent); } .tcard .tl { font-weight: 700; }
.lists { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px; }
.flist { border: 1px solid var(--border); border-radius: 10px; padding: 8px 12px; } .flist ul { margin: 4px 0; padding-left: 18px; font-size: .92rem; }
.overall p { font-size: 1.02rem; }
.drawer { position: fixed; top: 0; right: 0; bottom: 0; width: min(560px, 100%); z-index: 40; background: var(--surface); border-left: 1px solid var(--border); box-shadow: var(--shadow); display: flex; flex-direction: column; }
.drawer[hidden] { display: none; }
.dhead { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; border-bottom: 1px solid var(--border); } .dhead h3 { margin: 0; }
#dr-body { overflow-y: auto; padding: 12px 16px; }
.evi { border-bottom: 1px solid var(--border); padding: 10px 0; } .evi .q p { margin: 0; font-size: .95rem; }
.evi .src { font-size: .85rem; margin: 6px 0 2px; } .evi .r3 .bd { font-size: .78rem; } .evi .rid { font-size: .75rem; color: var(--ink-3); margin: 2px 0 0; }
.evi .tr { font-size: .85rem; color: var(--muted); }
.conflict { border: 1px solid var(--gate); background: var(--gate-bg); border-radius: 10px; padding: 8px 12px; margin-bottom: 10px; } .conflict h4 { margin: 0 0 4px; color: var(--gate); }
.conflict .evi { background: var(--surface); border-radius: 8px; padding: 8px 10px; margin: 6px 0; }
@media (max-width: 700px) { .step { grid-template-columns: 1fr; } .step > .se { text-align: left; } .two { grid-template-columns: 1fr; } .igrid { grid-template-columns: 1fr; } }
"""

JS = r"""
(function () {
  var EV = JSON.parse(document.getElementById('ev').textContent);
  var cards = Array.prototype.slice.call(document.querySelectorAll('.issue'));
  var NAMES = { 'f-strand': 'Theme', 'f-pri': 'Priority', 'f-dir': 'Direction of travel', 'f-gap': 'Unresolved gap', 'f-st': 'Status', 'f-comp': 'Comparator analysis', 'f-u26': '2026 update' };
  var f = { q: document.getElementById('f-q'), strand: document.getElementById('f-strand'), pri: document.getElementById('f-pri'), dir: document.getElementById('f-dir'),
            gap: document.getElementById('f-gap'), st: document.getElementById('f-st'), comp: document.getElementById('f-comp'), u26: document.getElementById('f-u26') };
  var count = document.getElementById('f-count'), chips = document.getElementById('f-chips');
  function h(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function apply() {
    var q = f.q.value.trim().toLowerCase(), n = 0;
    cards.forEach(function (c) {
      var ok = (!f.strand.value || c.dataset.strand === f.strand.value) && (!f.pri.value || c.dataset.priority === f.pri.value) &&
               (!f.dir.value || c.dataset.direction === f.dir.value) && (!f.gap.value || c.dataset.gap === f.gap.value) &&
               (!f.st.value || c.dataset.status === f.st.value) && (!f.comp.value || c.dataset.comp === f.comp.value) &&
               (!f.u26.value || (' ' + c.dataset.u26 + ' ').indexOf(' ' + f.u26.value + ' ') !== -1) &&
               (!q || c.dataset.search.indexOf(q) !== -1);
      c.classList.toggle('hidden', !ok);
      if (ok) n++;
    });
    count.textContent = 'Showing ' + n + ' of ' + cards.length + ' reform issues';
    var html = '';
    Object.keys(f).forEach(function (k) {
      var e = f[k]; if (!e.value) return;
      var txt = k === 'q' ? 'Search: ' + e.value : NAMES[e.id] + ': ' + e.options[e.selectedIndex].text;
      html += '<button type="button" class="fchip" data-k="' + k + '">' + h(txt) + ' <span aria-hidden="true">&times;</span><span class="vh"> remove</span></button>';
    });
    chips.innerHTML = html ? html + '<button type="button" class="fchip clear" data-k="*">Clear all</button>' : '';
  }
  function reset() { Object.keys(f).forEach(function (k) { f[k].value = ''; }); apply(); }
  ['input', 'change'].forEach(function (ev) { Object.keys(f).forEach(function (k) { f[k].addEventListener(ev, apply); }); });
  chips.addEventListener('click', function (e) {
    var b = e.target.closest('.fchip'); if (!b) return;
    if (b.dataset.k === '*') reset(); else { f[b.dataset.k].value = ''; apply(); }
  });
  document.querySelectorAll('a[data-strand]').forEach(function (a) {
    a.addEventListener('click', function () { reset(); f.strand.value = a.dataset.strand; apply(); });
  });
  document.addEventListener('click', function (e) {
    var b = e.target.closest('.moret'); if (!b) return;
    var p = b.parentNode; p.classList.toggle('expanded'); b.textContent = p.classList.contains('expanded') ? 'Show less' : 'Show more';
  });
  // Issue detail panel
  var savedY = null, crumb = document.getElementById('crumb-issue');
  function current() { return document.querySelector('.issue.open'); }
  function openIssue(id, fromClick) {
    var el = id && document.getElementById(id);
    if (!el || !el.classList.contains('issue')) return false;
    if (el.classList.contains('hidden')) reset();
    var cur = current(); if (cur && cur !== el) cur.classList.remove('open');
    if (savedY === null) savedY = fromClick != null ? fromClick : window.scrollY;
    el.classList.add('open'); document.body.classList.add('noscroll');
    if (crumb) crumb.innerHTML = ' <span aria-hidden="true">›</span> ' + h(el.dataset.label);
    var c = el.querySelector('.pclose'); if (c && c.focus) c.focus();
    return true;
  }
  function closeIssue(keepHash) {
    var cur = current(); if (!cur) return;
    cur.classList.remove('open'); document.body.classList.remove('noscroll'); closeDrawer();
    if (crumb) crumb.innerHTML = '';
    if (!keepHash && history.replaceState) history.replaceState(null, '', location.pathname + location.search);
    if (savedY !== null) window.scrollTo(0, savedY);
    savedY = null;
  }
  document.querySelectorAll('a.open').forEach(function (a) { a.addEventListener('click', function () { savedY = window.scrollY; }); });
  document.querySelectorAll('.pclose').forEach(function (b) { b.addEventListener('click', function () { closeIssue(false); }); });
  function onHash() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (!openIssue(id, savedY)) { if (current()) closeIssue(true); var t = id && document.getElementById(id); if (t && t.scrollIntoView) t.scrollIntoView(); }
  }
  window.addEventListener('hashchange', onHash);
  // Evidence drawer
  var drawer = document.getElementById('drawer'), dbody = document.getElementById('dr-body'), dtitle = document.getElementById('dr-title');
  var RANK = { High: 0, Medium: 1, Low: 2 };
  function lab(v) { return v === 'insufficient_evidence' ? 'Insufficient evidence' : (!v || v === 'not rated' ? 'Not rated' : v); }
  function item(id, rel, sq) {
    var it = EV.items[id]; if (!it) return '';
    var s = EV.src[it[1]] || [];
    var long = it[0].length > 420;
    return '<div class="evi"><div class="q' + (long ? ' clamp' : '') + '"><p>&ldquo;' + h(it[0]) + '&rdquo;</p>' + (long ? '<button type="button" class="moret">Show full quote</button>' : '') + '</div>' +
      (it[4] && it[5] ? '<p class="tr">Machine translation: ' + h(it[5]) + '</p>' : '') +
      '<p class="src">' + h(s[0]) + (s[1] ? ' · ' + h(s[1]) : '') + (s[2] ? ' · ' + h(s[2]) : '') + (it[2] ? ' · ' + h(it[2]) : '') + '</p>' +
      '<p class="r3"><span class="bd">Source quality <b>' + h(lab(sq)) + '</b></span><span class="bd">Evidence confidence <b>' + h(lab(it[3])) + '</b></span>' +
      '<span class="bd">Relevance <b>' + h(lab(rel)) + '</b></span>' + (it[4] ? '<span class="tag">Machine translation</span>' : '') + '</p>' +
      '<p class="rid">' + h(id) + (s[3] ? ' · <a href="' + h(s[3]) + '" target="_blank" rel="noopener">Original source</a>' : '') + '</p></div>';
  }
  function openDrawer(key, title) {
    var p = key.split('|'), I = EV.issues[p[0]] || { s: {}, c: [] }, rows = (I.s[p[1]] || []).slice();
    rows.sort(function (a, b) { return ((RANK[a[1]] == null ? 3 : RANK[a[1]]) - (RANK[b[1]] == null ? 3 : RANK[b[1]])) ||
      ((RANK[(EV.items[a[0]] || [])[3]] == null ? 3 : RANK[EV.items[a[0]][3]]) - (RANK[(EV.items[b[0]] || [])[3]] == null ? 3 : RANK[EV.items[b[0]][3]])); });
    var ids = {}; rows.forEach(function (r) { ids[r[0]] = r; });
    var html = '';
    var cf = I.c.filter(function (c) { return ids[c[0]] || ids[c[1]]; });
    if (cf.length) {
      html += '<div class="conflict"><h4>Conflicting evidence</h4>';
      cf.forEach(function (c) { html += '<p class="note">' + h(c[2]) + '</p><div class="pair">' + item(c[0], (ids[c[0]] || [])[1], (ids[c[0]] || [])[2]) + item(c[1], (ids[c[1]] || [])[1], (ids[c[1]] || [])[2]) + '</div>'; });
      html += '</div>';
    }
    if (!rows.length) html += '<p class="note">No evidence recorded for this step in this run.</p>';
    rows.forEach(function (r, i) { html += '<div class="evw' + (i >= 5 ? ' hidden more5' : '') + '">' + item(r[0], r[1], r[2]) + '</div>'; });
    if (rows.length > 5) html += '<button type="button" id="dr-all">Show all (' + rows.length + ')</button>';
    dtitle.textContent = title || 'Evidence'; dbody.innerHTML = html; drawer.hidden = false; dbody.scrollTop = 0;
    var all = document.getElementById('dr-all');
    if (all) all.addEventListener('click', function () { dbody.querySelectorAll('.more5').forEach(function (e) { e.classList.remove('hidden'); }); all.remove(); });
    document.getElementById('dr-close').focus();
  }
  function closeDrawer() { drawer.hidden = true; }
  document.addEventListener('click', function (e) { var b = e.target.closest('.evb'); if (b) openDrawer(b.dataset.ev, b.dataset.title); });
  document.getElementById('dr-close').addEventListener('click', closeDrawer);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { if (!drawer.hidden) closeDrawer(); else closeIssue(false); } });
  var links = Array.prototype.slice.call(document.querySelectorAll('nav.top a'));
  function spy() {
    var cur = null;
    links.forEach(function (a) { var t = document.getElementById(a.getAttribute('href').slice(1)); if (t && t.getBoundingClientRect().top <= 90) cur = a; });
    links.forEach(function (a) { a.classList.toggle('active', a === cur); });
  }
  window.addEventListener('scroll', spy, { passive: true });
  apply();
  onHash();
  spy();
})();
"""


def lbl(text, cls=""):
    """The five content labels are coloured status chips; any other label is a neutral tag (spec 10.1)."""
    return chip(text) if text in STATUSES else tag(text)


VAL = chip("Validated")
DRAFT = tag("Internal draft")
AWAIT = tag("Awaiting 2026 Enlargement Package")
SYN = tag("Agent synthesis")


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
        self.alljs = [j for j in read_csv(self.root / "judgements" / "judgements.csv")[1] if j.get("run_id") == self.run]  # PC-31: this run's rows only
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

    def years(self, ks):
        ys = sorted({(self.D["items"][k]["dates"].get("publication_date") or "")[:4] for k in ks} - {""})
        return "" if not ys else (ys[0] if ys[0] == ys[-1] else f"{ys[0]} to {ys[-1]}")

    def count_line(self, ks, what):
        n = len(ks)
        y = self.years(ks)
        return f'{n} {what}{"" if n == 1 else "s"}' + (f", {y}" if y else "")

    def istatus(self, x):
        return issue_status(self.views[x]["J"], gate_passed(self.p.decisions, "G6"))

    def status_html(self, x):
        st, rr = self.istatus(x)
        return chip(st) + (" " + tag("Flagged for re-review") if rr else "")

    def jstat(self, j):
        s = chip(judgement_status(j, gate_passed(self.p.decisions, "G6"))) if j else ""
        return s + (" " + tag("Flagged for re-review") if j.get("rereview_flag") == "yes" else "")

    def impl_counts(self, x):
        c = Counter(j.get("value", "") for j in self.views[x]["status"].values())
        order = ("proposed", "adopted", "implemented", "in_practice", "replaced", "reversed", "unclear", "insufficient_evidence")
        return " · ".join(f"{c[v]} {display('implementation_status', v)[0].lower()}" for v in order if c[v])

    def impl_gap(self, x):
        vals = {j.get("value") for j in self.views[x]["status"].values()}
        return bool(vals & {"adopted", "implemented"}) and "in_practice" not in vals

    def country_link(self, cc):
        """Link to a comparator country's page, labelled when it is still a draft (spec 6.4)."""
        from regional_page import planned_runs
        name = COUNTRIES.get(cc, cc)
        if not (self.root / "analysis" / f"{cc}.html").exists() or cc == self.cc:
            return escape(name)
        run = next((r for r, c, _ in planned_runs(self.root) if c == cc), "")
        done = bool(run) and gate_passed(gate_decisions(self.root, run), "G7")
        return (f'<a href="{escape(cc)}.html">{escape(name)}</a>' if done else
                f'{escape(name)} <a href="{escape(cc)}.html">{tag("Draft country page")}</a>')

    def ev_data(self):
        """Evidence for the drawer, embedded once as JSON: items, sources and, per issue, the items of each chain step."""
        it, src, si = self.D["items"], [], {}
        conf = {j["object_id"]: j["value"] for j in self.D["js"] if j["judgement_type"] == "evidence_confidence"}
        items, issues = {}, {}

        def add(k):
            if k in items or k not in it:
                return k in it
            i = it[k]
            s = i["_source"]
            if s not in si:
                r = self.D["reg"].get(s, {})
                si[s] = len(src)
                src.append([r.get("title", s), r.get("institution", ""), r.get("publication_date", ""), r.get("url", "")])
            loc = i["location"]
            where = (f"p. {loc['page']}" + (f"-{loc['page_end']}" if loc.get("page_end") else "")) if loc.get("page") else (loc.get("section") or "")
            items[k] = [i["stated_text"], si[s], where, conf.get(k, ""), 1 if i.get("machine_translated") else 0, i.get("translation_en") or ""]
            return True

        for r in self.D["issues"]:
            x, V = r["issue_id"], self.views[r["issue_id"]]
            steps = {}
            for k in sorted(V["mine"]):
                cl = it[k]["pass2"]["chain_link"]
                if cl in STEP_KEYS:
                    steps.setdefault(cl, []).append(k)
            pid = [k for t in ("priority", "tractability") for k in split_list(V["J"].get(t, {}).get("evidence_item_ids", ""))]
            steps["priority"] = list(dict.fromkeys(pid))
            for c in self.cases.get(x, []):
                ids = [k for f in ("reform_items", "implementation_items", "outcome_items") for k in split_list(c.get(f, ""))]
                steps["case:" + c["case_id"]] = list(dict.fromkeys(ids))
                steps.setdefault("comparator", [])
                steps["comparator"] += [k for k in ids if k not in steps["comparator"]]
            out = {}
            for s, ks in steps.items():
                out[s] = [[k, V["rel"].get(k, ""), quality(self.D, k, r)] for k in ks if add(k)]
            cf = [[l["from_id"], l["to_id"], l["basis"]] for l in V["conflicts"] if add(l["from_id"]) and add(l["to_id"])]
            issues[x] = {"s": out, "c": cf}
        return {"items": items, "src": src, "issues": issues}

    def ev_button(self, x, step, label=None):
        n = len(self.EV["issues"].get(x, {}).get("s", {}).get(step, []))
        if not n:
            return '<span class="note">No evidence recorded for this step in this run.</span>'
        return (f'<button type="button" class="evb" data-ev="{escape(x)}|{escape(step)}" data-title="{escape(label or "")}">'
                f'{n} evidence item{"s" if n != 1 else ""}</button>')

    def overview(self):
        rec = self.p.rec
        g7 = gate_passed(self.p.decisions, "G7")
        summ = narrative(self.root, self.run, "scope_overview").get("Summary", "") if g7 else ""
        assess = (f'<div class="overall"><h3>Overall assessment {tag("Agent synthesis, validated at G7")}</h3>'
                  + "".join(f"<p>{text(no_refs(s))}</p>" for s in [" ".join(sentences(summ))]) + "</div>") if summ else \
                 f'<div class="overall"><h3>Overall assessment {chip("Not started")}</h3></div>'
        order = sorted(self.D["issues"], key=self.sort_key)
        top = "".join(
            f'<a class="tcard" href="#{escape(r["issue_id"])}"><span class="tl">{escape(r["label"])}</span>'
            f'<span>{badge("priority", self.jv(r["issue_id"], "priority").get("value"))}{badge("direction_of_travel", self.jv(r["issue_id"], "direction_of_travel").get("value"))}'
            f'{badge("unresolved_gap", self.jv(r["issue_id"], "unresolved_gap").get("value"))}</span><span>{self.status_html(r["issue_id"])}</span></a>' for r in order[:5])
        def lst(title, rs, note):
            li = "".join(f'<li><a href="#{escape(r["issue_id"])}">{escape(r["label"])}</a></li>' for r in rs)
            return (f'<details class="flist"{" open" if len(rs) <= 6 else ""}><summary><b>{escape(title)}</b> ({len(rs)})</summary>'
                    f'<p class="note">{escape(note)}</p><ul>{li or "<li>None</li>"}</ul></details>')
        dv = lambda r: self.jv(r["issue_id"], "direction_of_travel").get("value")
        gv = lambda r: self.jv(r["issue_id"], "unresolved_gap").get("value")
        lists = (lst("What is improving", [r for r in order if dv(r) in ("improving", "largely_resolved")], "Direction of travel improving or largely resolved.")
                 + lst("What remains stuck", [r for r in order if dv(r) in ("persistent", "worsening") or gv(r) == "open"], "Direction of travel persistent or worsening, or the gap is open.")
                 + lst("Major implementation gaps", [r for r in order if self.impl_gap(r["issue_id"])], "A linked intervention is adopted or implemented, and none is shown in practice."))
        freeze = rec.get("Evidence freeze date", "").split(" ")[0]
        return "overview", "Overview", (
            f'<p class="runline">Evidence cut-off {escape(freeze)} · Scope: Chapter 2 (Freedom of movement for workers) and Technology and AI recommendations'
            f'{"; comparator step on " + NUM.get(len(self.cases), str(len(self.cases))) + " issues" if self.cases else ""}</p>'
            f'{assess}<h3>Top priority issues</h3><div class="tgrid">{top}</div>'
            f'<div class="lists">{lists}</div>' + self.banner())

    def sort_key(self, r):
        x = r["issue_id"]
        p = self.jv(x, "priority").get("value")
        g = self.jv(x, "unresolved_gap").get("value")
        return ({"High": 0, "Medium": 1, "Low": 2, "insufficient_evidence": 4}.get(p, 3),
                {"open": 0, "partly_addressed": 1, "largely_closed": 2, "insufficient_evidence": 4}.get(g, 3), x)

    def step(self, name, kind, summary, ev="", extra=""):
        return (f'<li class="step k-{kind.lower()}"><div class="sl"><b>{escape(name)}</b> <span class="kind">{escape(kind)}</span></div>'
                f'<div class="ss">{summary}</div><div class="se">{ev}</div>{extra}</li>')

    def panel(self, r, u_block):
        x, V, N = r["issue_id"], self.views[r["issue_id"]], self.narr[r["issue_id"]]
        J = V["J"]
        ev = self.EV["issues"][x]["s"]
        heads = "".join(f'<div class="hb">{badge(t, J.get(t, {}).get("value"))} {self.jstat(J.get(t, {}))}</div>'
                        for t in ("direction_of_travel", "unresolved_gap", "priority", "tractability"))
        brief = N.get("In brief", "") if gate_passed(self.p.decisions, "G7") else ""
        brief_html = f'<p class="brief">{text(no_refs(brief))} {tag("Agent synthesis, validated at G7")}</p>' if brief else ""
        reqn = N.get("How the EU requirement has changed", "") if gate_passed(self.p.decisions, "G7") else ""
        eu = f'<p>{escape(self.count_line(ev.get("eu_requirement", []) and [k for k, *_ in ev["eu_requirement"]], "EU requirement item"))}.</p>' if ev.get("eu_requirement") else "<p>No EU requirement item recorded.</p>"
        if reqn:
            eu += f'<p>{text(no_refs(reqn))} {tag("Agent synthesis, validated at G7")}</p>'
        cr = ev.get("country_response", [])
        crs = f'<p>{escape(self.count_line([k for k, *_ in cr], "item"))} on what the country has done.</p>' if cr else "<p>No country response item recorded.</p>"
        ints = "".join(f'<li>{escape(self.names.get(n, n))} {badge("implementation_status", V["status"].get(n, {}).get("value"), False)}</li>' for n in V["iids"])
        ints = (f'<ul class="ints">{ints}</ul>' if len(V["iids"]) <= 8 else
                f'<details><summary>{len(V["iids"])} interventions</summary><ul class="ints">{ints}</ul></details>') if ints else \
               '<p class="note">No country intervention is linked to this issue in the evidence.</p>'
        ic = self.impl_counts(x)
        outc = "".join(f'<li>{escape(self.names.get(l["from_id"], l["from_id"]))}: {badge("success", s["value"] if s else "")} {badge("attribution", a["value"] if a else "")}</li>'
                       for l, s, a in V["outc"])
        outc = (f'<ul class="ints">{outc}</ul>' if outc else '<p class="note">No stated outcome is linked to an intervention under this issue.</p>') + \
               '<p class="small">Adoption is not success.</p>'
        g, d = J.get("unresolved_gap", {}), J.get("direction_of_travel", {})
        gap = (f'<p>{badge("unresolved_gap", g.get("value"))} {self.jstat(g)}</p><p>{text(no_refs(g.get("reason", "")))}</p>'
               f'<p>{badge("direction_of_travel", d.get("value"))} {self.jstat(d)}</p><p>{text(no_refs(d.get("reason", "")))}</p>')
        cases = self.cases.get(x, [])
        none_c = '<p class="note">No comparator analysis for this issue in this run.</p>'
        comp = "".join(self.case_card(x, c) for c in cases) if cases else none_c
        lessons = narrative(self.root, self.run, f"comparator_{x}").get("Lessons across the cases", "") if cases else ""
        lesson = f'<p>{text(no_refs(lessons))} {tag("Agent synthesis, validated at G6b")}</p>' if lessons else none_c
        p_, t_ = J.get("priority", {}), J.get("tractability", {})
        pri = (f'<div class="two"><div><p>{badge("priority", p_.get("value"))} {self.jstat(p_)}</p><p>{text(no_refs(p_.get("reason", "")))}</p></div>'
               f'<div><p>{badge("tractability", t_.get("value"))} {self.jstat(t_)}</p><p>{text(no_refs(t_.get("reason", "")))}</p></div></div>')
        opts = self.option_cards(x) or '<p class="note">No policy options for this issue in this run.</p>'
        chain = (self.step("EU requirement", "Stated", eu, self.ev_button(x, "eu_requirement", "EU requirement"))
                 + self.step("Country response", "Stated", crs, self.ev_button(x, "country_response", "Country response"))
                 + self.step("Implementation", "Assessed", (f"<p>{escape(ic)}</p>" if ic else "") + ints, self.ev_button(x, "implementation", "Implementation"))
                 + self.step("Outcome", "Assessed", outc, self.ev_button(x, "outcome", "Outcome"))
                 + self.step("Unresolved gap", "Assessed", gap, self.ev_button(x, "unresolved_gap", "Unresolved gap"))
                 + self.step("Comparator evidence", "Stated", comp, self.ev_button(x, "comparator", "Comparator evidence") if cases else "")
                 + self.step("Lesson", "Assessed", lesson, self.ev_button(x, "lesson", "Lesson") if cases or ev.get("lesson") else "")
                 + self.step("Priority", "Assessed", pri, self.ev_button(x, "priority", "Priority and tractability"))
                 + self.step("Policy option", "Assessed", opts))
        return (f'<div class="panel" role="dialog" aria-modal="true" aria-label="{escape(r["label"])}"><div class="pin">'
                f'<div class="ptop"><span class="idlink">{escape(x)} · {escape(self.cname)}</span><button type="button" class="pclose">Close</button></div>'
                f'<h2>{escape(r["label"])}</h2><div class="tags">{self.theme_tags(r)}</div>'
                f'<p class="def">{escape(r["definition"])}</p><div class="hbs">{heads}</div>{brief_html}'
                f'<ol class="chain">{chain}</ol>{u_block}'
                f'<p class="note"><a href="{self.up}outputs/{escape(self.run)}/issue_brief_{escape(x)}.md">Full issue brief</a></p></div></div>')

    def theme_tags(self, r):
        if self.strand(r["issue_id"]) == "fmw":
            return tag("Chapter 2")
        return tag("Technology and AI") + "".join(" " + tag(self.themes.get(t, t)) for t in split_list(r.get("themes", "")))

    def issue_card(self, r):
        x, V = r["issue_id"], self.views[r["issue_id"]]
        J = V["J"]
        reqs = [k for k, *_ in self.EV["issues"][x]["s"].get("eu_requirement", [])]
        reason = no_refs(J.get("priority", {}).get("reason", ""))
        ic = self.impl_counts(x)
        st, rr = self.istatus(x)
        u_state, u_strip, u_block = self.progression(x)
        o26 = "held" if any(self.D["items"][k]["_source"] in self.other26 for k in self.D["by"].get(x, [])) else ""
        kw = [self.themes.get(t, t) for t in split_list(r.get("themes", ""))]
        search = re.sub(r"\s+", " ", " ".join([x, r["label"], r["definition"], STRAND[self.strand(x)]] + kw).lower())
        return (f'<article class="issue" id="{escape(x)}" data-strand="{self.strand(x)}" data-priority="{escape(J.get("priority", {}).get("value", ""))}" '
                f'data-direction="{escape(J.get("direction_of_travel", {}).get("value", ""))}" data-gap="{escape(J.get("unresolved_gap", {}).get("value", ""))}" '
                f'data-status="{escape(st)}" data-comp="{"yes" if x in self.cases else "no"}" data-u26="{u_state} {o26}" data-label="{escape(r["label"])}" data-search="{escape(search)}">'
                f'<div class="top"><span class="idlink">{escape(x)}</span><span>{self.status_html(x)}</span></div>'
                f'<h4>{escape(r["label"])}</h4><div class="tags">{self.theme_tags(r)}</div>'
                f'<p class="req"><span class="eu">EU</span> {escape(r["definition"])} <span class="note">{escape(self.count_line(reqs, "EU requirement"))}.</span></p>'
                f'<div class="badges">{badge("direction_of_travel", J.get("direction_of_travel", {}).get("value"))}{badge("unresolved_gap", J.get("unresolved_gap", {}).get("value"))}'
                f'{badge("priority", J.get("priority", {}).get("value"))}{badge("tractability", J.get("tractability", {}).get("value"))}</div>'
                + (f'<div class="assess clamp"><p>{text(reason)}</p><button type="button" class="moret">Show more</button></div>' if reason else "")
                + f'<p class="meta">{(escape("Interventions: " + ic) + " · ") if ic else ""}{len(V["mine"])} evidence items'
                + (" · " + tag("Comparator analysis available") if x in self.cases else "") + f'</p>{u_strip}'
                f'<p><a class="open" href="#{escape(x)}">Open</a></p>{self.panel(r, u_block)}</article>')

    def issues(self):
        o = lambda t, vals: "".join(f'<option value="{escape(v)}">{escape(display(t, v)[0])}</option>' for v in vals)
        filt = ('<div class="filters" role="search">'
                '<label>Search<input id="f-q" type="search" placeholder="Issue name or definition"></label>'
                '<label>Theme<select id="f-strand"><option value="">All</option><option value="fmw">Chapter 2</option><option value="tec">Technology and AI</option></select></label>'
                f'<label>Priority<select id="f-pri"><option value="">All</option>{o("priority", ("High", "Medium", "Low", "insufficient_evidence"))}</select></label>'
                f'<label>Direction of travel<select id="f-dir"><option value="">All</option>{o("direction_of_travel", ("new", "worsening", "persistent", "improving", "largely_resolved", "insufficient_evidence"))}</select></label>'
                f'<label>Unresolved gap<select id="f-gap"><option value="">All</option>{o("unresolved_gap", ("open", "partly_addressed", "largely_closed", "insufficient_evidence"))}</select></label>'
                '<label>Status<select id="f-st"><option value="">All</option>' + "".join(f"<option>{s}</option>" for s in STATUSES) + '</select></label>'
                '<label>Comparator analysis<select id="f-comp"><option value="">All</option><option value="yes">Available</option><option value="no">Not available</option></select></label>'
                '<label>2026 update<select id="f-u26"><option value="">All</option><option value="awaiting">Awaiting 2026 Enlargement Package</option>'
                '<option value="held">Has 2026 official EU evidence already held</option><option value="proposed">2026 change proposed</option>'
                '<option value="assessed">2026 change validated</option><option value="no_new">No new 2026 report item</option></select></label>'
                '</div><div class="fchips" id="f-chips"></div>'
                f'<p class="count" id="f-count" aria-live="polite">Showing {len(self.D["issues"])} of {len(self.D["issues"])} reform issues</p>')
        cards = "".join(self.issue_card(r) for r in sorted(self.D["issues"], key=self.sort_key))
        return "issues", "Reform issues", (
            '<p class="note">Sorted by priority, then by unresolved gap. <b>Open</b> shows the analytical chain and the evidence for each step. '
            'Every issue has its own link.</p>' + filt + f'<div class="igrid">{cards}</div>')

    def case_card(self, x, c):
        cid = c["case_id"]
        rel, tr = self.J.get((cid, "comparator_relevance"), {}), self.J.get((cid, "transferability"), {})
        lesson = c.get(lesson_field({0: c}), "")
        return (f'<div class="case" id="{escape(cid)}-{escape(x)}"><div class="top"><span class="idlink">{escape(cid)}</span></div>'
                f'<h4>{self.country_link(c["country"])}</h4>'
                f'<div class="clamp"><p><b>What was done:</b> {text(no_refs(self.ent.get(cid, {}).get("description", "")))}</p><button type="button" class="moret">Show more</button></div>'
                f'<div class="clamp"><p><b>Lesson</b> {tag("Agent synthesis, validated at G6b")} {text(no_refs(lesson))}</p><button type="button" class="moret">Show more</button></div>'
                f'<p>{badge("comparator_relevance", rel.get("value"))} {self.jstat(rel)} {badge("transferability", tr.get("value"))} {self.jstat(tr)}</p>'
                f'<p>{self.ev_button(x, "case:" + cid, "Comparator case: " + COUNTRIES.get(c["country"], c["country"]))}</p></div>')

    def comparators(self):
        out = ""
        for x, cases in self.cases.items():
            r = next(i for i in self.D["issues"] if i["issue_id"] == x)
            lessons = narrative(self.root, self.run, f"comparator_{x}").get("Lessons across the cases", "")
            out += (f'<div class="compbox"><h3><a href="#{escape(x)}">{escape(r["label"])}</a></h3>'
                    f'<p><b>Lessons across the cases</b> {tag("Agent synthesis, validated at G6b")} {text(no_refs(lessons))}</p>'
                    f'<div class="cgrid">{"".join(self.case_card(x, c) for c in cases)}</div>'
                    f'<p class="note"><a href="{self.up}outputs/{escape(self.run)}/comparator_brief_{escape(x)}.md">Full comparator brief</a></p></div>')
        return "comparators", "Comparators", (
            f'<p>{VAL} Comparator cases validated at G6b. The cases show what was tried, not what worked. Lessons are the tool\'s own reading across the '
            'evidence, validated by the analyst as conditional hypotheses; they are not stated by the sources.</p>' + out)

    def option_cards(self, x):
        r = next(i for i in self.D["issues"] if i["issue_id"] == x)
        cards = ""
        fields = [("Mechanism targeted", "Problem it targets"), ("Conditions and preconditions", "Preconditions"), ("Main risks", "Risks"), ("Who would need to act", "Responsible actor")]
        for o in self.opts.get(x, []):
            f = o["fields"]
            if o.get("note"):
                cards += f'<p class="note"><b>{escape(o["title"])}.</b> {text(no_refs(o["text"]))}</p>'
                continue
            comp = f.get("Comparator evidence", "") or o["text"]
            rationale, _, transfer = comp.partition("Transferability conditional")
            transfer = ("Conditional" + transfer) if transfer else ""
            countries = sorted(n for n in COUNTRIES.values() if n != self.cname and n in comp)
            kv = f'<dt>Comparator it draws on</dt><dd>{escape(", ".join(countries) or "see rationale")}</dd>'
            if f.get("Gap addressed"):
                kv += f'<dt>Gap it addresses</dt><dd>{text(no_refs(f["Gap addressed"]))}</dd>'
            kv += f'<dt>Rationale</dt><dd>{text(no_refs(rationale.strip()))}</dd>'
            if transfer:
                kv += f'<dt>Transferability conditions {SYN}</dt><dd>{text(no_refs(transfer.strip()))}</dd>'
            for k, h in fields:
                if f.get(k):
                    kv += f'<dt>{escape(h)}</dt><dd>{text(no_refs(f[k]))}</dd>'
            cards += (f'<div class="option"><div class="top"><span class="idlink">{escape(x)}</span><span>{DRAFT} {SYN}</span></div>'
                      f'<h4>{escape(o["title"])}</h4><details><summary>Details</summary><dl class="kv">{kv}</dl></details></div>')
        return cards

    def options(self):
        out = ""
        for x in self.opts:
            r = next(i for i in self.D["issues"] if i["issue_id"] == x)
            out += f'<div class="compbox"><h3><a href="#{escape(x)}">{escape(r["label"])}</a></h3>{self.option_cards(x)}</div>'
        return "options", "Draft policy options", (
            f'<p>{DRAFT} These options were signed off at G7 as <b>internal drafts</b>. They are not validated recommendations and have not been '
            'prepared for an external audience. Each rests on a validated unresolved gap and on comparator lessons that are agent synthesis, rated conditional. '
            'None is proposed because another country adopted it, and none is shown by the evidence to work.</p>' + out)

    def evidence(self):
        N = narrative(self.root, self.run, "coverage_and_limits")
        lim = [r for r in read_csv(self.root / "registers" / "limits_log.csv")[1] if r["run_id"] == self.run and r["status"] == "active"]
        rows = "".join(f'<li>{escape(r["description"])} <span class="idlink">{escape(r["limit_id"])}</span></li>' for r in lim)
        mkd = [i for i in self.D["items"].values() if i["country"] == self.cc and i["pass2"]["classification_status"] != "out_of_scope"]
        mt = sum(1 for i in mkd if i.get("machine_translated"))
        return "evidence", "Evidence and limits", (
            f'<p>{VAL} From the coverage and limits report signed off at G7.</p>'
            f'<h3>Source coverage {SYN}</h3><p>{text(no_refs(N.get("Summary", "")))}</p>'
            f'<p>{tag("Evidence limit")} {mt:,} of {len(mkd):,} in-scope {escape(self.cname)} evidence items ({100 * mt / max(len(mkd), 1):.0f}%) are machine translated, '
            'and their evidence confidence is capped at Medium. Source quality, evidence confidence and relevance are kept as separate judgements and never combined.</p>'
            f'<h3>Methodological limitations {SYN}</h3><p>{text(no_refs(N.get("Methodological limitations", "")))}</p>'
            f'<details class="refs"><summary>Active limits for this run ({len(lim)})</summary><ul class="ints">{rows}</ul></details>'
            f'<p class="note">Reports: <a href="{self.up}outputs/{escape(self.run)}/coverage_and_limits_report.md">coverage and limits report</a> · '
            f'<a href="{self.up}outputs/{escape(self.run)}/scope_overview.md">scope overview</a> · <a href="{self.up}runs/{escape(self.run)}/run_review.md">run review</a></p>')

    def render(self, css, version, today):
        self.EV = self.ev_data()
        secs = [self.overview(), self.issues(), self.comparators(), self.options(), self.evidence()]
        nav = ('<a href="#overview">Overview</a><a href="#issues" data-strand="fmw">Chapter 2</a><a href="#issues" data-strand="tec">Technology and AI</a>'
               '<a href="#issues">All issues</a><a href="#comparators">Comparators</a><a href="#options">Policy options</a><a href="#evidence">Evidence and limits</a>')
        body = "".join(f'<section id="{sid}"><h2>{escape(title)}</h2>{content}<a class="totop" href="#top">Back to top</a></section>' for sid, title, content in secs)
        from regional_page import country_menu
        status = run_status_text(self.p.decisions, True, alpha=self.run == "RUN-2026-01")
        head = header(self.up, [("Region", self.up + "analysis.html"), (self.cname, "")], country_menu(self.root), self.cc)
        ev = json.dumps(self.EV, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(self.T.get("title", f"{self.cname} Accession Analysis"))}</title>
<!-- Generated by tools/build_review_page.py {version} on {today} from validated records only. Do not edit by hand: rebuild instead. -->
<style>{css}{FE_CSS}{CSS_EXTRA}</style>
</head>
<body>
<div class="wrap" id="top">
{head}
<div class="pagehead"><h1>{escape(self.cname)}</h1>
<p class="runline">{escape(status)} · <span class="idlink">{escape(self.run)}</span> · Page updated {escape(today)} · <a href="{self.up}{review_page_name(self.root, self.run)}">Review page</a></p></div>
<nav class="top" aria-label="Sections">{nav}</nav>
{body}
<footer><p>Generated from the validated records of {escape(self.run)} by <code>tools/build_review_page.py</code> {version}. Presentation only: it adds no analysis. <a href="#top">Back to top</a></p></footer>
</div>
<aside id="drawer" class="drawer" hidden aria-labelledby="dr-title"><div class="dhead"><h3 id="dr-title">Evidence</h3><button type="button" id="dr-close">Close</button></div><div id="dr-body"></div></aside>
<script type="application/json" id="ev">{ev}</script>
<script>{JS}</script>
</body>
</html>
"""
