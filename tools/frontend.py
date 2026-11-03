"""Shared front-end layer for the product pages (frontend/FRONT_END_SPEC.md 0.2): design tokens taken from tool-explainer.html,
the shared header, the five content status labels, plain-text run status and the display mapping of the stored judgement values.
Presentation only: it maps stored values to labels, icons and colours and adds no value or analysis of its own."""

from html import escape

from common import gate_passed

# Display mapping (spec 10.3). Values are those in rules/judgement_rules.md 0.5 and schemas/data_dictionary.md 1.6; every scale
# also allows insufficient_evidence. Each entry: stored value -> (display label, icon, tone).
HML = {"High": ("High", "▲", "hi"), "Medium": ("Medium", "◆", "med"), "Low": ("Low", "▽", "lo")}
VALUES = {
    "direction_of_travel": {"new": ("New", "●", "flat"), "worsening": ("Worsening", "↓", "bad"), "persistent": ("Persistent", "→", "flat"),
                            "improving": ("Improving", "↑", "good"), "largely_resolved": ("Largely resolved", "✓", "good")},
    "unresolved_gap": {"open": ("Open", "■", "gap3"), "partly_addressed": ("Partly addressed", "◧", "gap2"), "largely_closed": ("Largely closed", "□", "gap1")},
    "priority": HML, "tractability": HML, "attribution": HML, "comparator_relevance": HML,
    "evidence_confidence": HML, "relevance": HML, "source_quality": HML,
    "implementation_status": {"proposed": ("Proposed", "○", "flat"), "adopted": ("Adopted", "◐", "med"), "implemented": ("Implemented", "◕", "med"),
                              "in_practice": ("In practice", "●", "good"), "reversed": ("Reversed", "↺", "bad"), "unclear": ("Unclear", "?", "flat")},
    "success": {"worked": ("Worked", "✓", "good"), "failed": ("Failed", "✗", "bad"), "mixed": ("Mixed", "◐", "med"), "too_early": ("Too early to tell", "…", "flat")},
    "transferability": {"likely": ("Likely", "▲", "hi"), "conditional": ("Conditional", "◆", "med"), "unlikely": ("Unlikely", "▽", "lo")},
}
INSUFFICIENT = ("Insufficient evidence", "∅", "ie")
TYPE_LABEL = {"direction_of_travel": "Direction of travel", "unresolved_gap": "Unresolved gap", "priority": "Priority", "tractability": "Tractability",
              "implementation_status": "Implementation", "success": "Success", "attribution": "Attribution", "comparator_relevance": "Comparator relevance",
              "transferability": "Transferability", "evidence_confidence": "Evidence confidence", "relevance": "Relevance", "source_quality": "Source quality"}


def display(t, v):
    """(label, icon, tone) for a stored value; never invents a value."""
    if v == "insufficient_evidence":
        return INSUFFICIENT
    if not v:
        return ("No judgement recorded", "", "none")
    return VALUES.get(t, {}).get(v, (v.replace("_", " "), "", "flat"))


def badge(t, v, prefix=True):
    lab, icon, tone = display(t, v)
    pre = f'{escape(TYPE_LABEL.get(t, ""))} ' if prefix else ""
    ic = f'<span class="ic" aria-hidden="true">{icon}</span>' if icon else ""
    return f'<span class="bd t-{tone}" data-type="{escape(t)}">{ic}{pre}<b>{escape(lab)}</b></span>'


# Content status labels (spec 10.1): the only coloured status chips.
STATUSES = ("Validated", "Pending review", "Proposed", "Draft", "Not started")
_SC = {"Validated": "validated", "Pending review": "pending", "Proposed": "proposed", "Draft": "draft", "Not started": "notstarted"}


def chip(label):
    return f'<span class="sc sc-{_SC[label]}">{escape(label)}</span>'


def tag(text):
    """Neutral, uncoloured tag for notes that are not content status (agent synthesis, internal draft, evidence limits, re-review)."""
    return f'<span class="tag">{escape(text)}</span>'


RANK = {"Not started": 0, "Draft": 1, "Proposed": 2, "Pending review": 3, "Validated": 4}


def judgement_status(j, g6_passed):
    if not j:
        return "Not started"
    if j.get("review_status") in ("validated", "overridden"):
        return "Validated" if g6_passed else "Pending review"
    return "Proposed"


def issue_status(J, g6_passed, run_started=True):
    """Spec 10.4: the lowest status among the four main issue judgements; re-review is reported separately."""
    js = [J[t] for t in ("priority", "direction_of_travel", "unresolved_gap", "tractability") if J.get(t)]
    if not js:
        return ("Draft" if run_started else "Not started"), False
    st = min((judgement_status(j, g6_passed) for j in js), key=RANK.get)
    return st, any(j.get("rereview_flag") == "yes" for j in js)


def run_status_text(decisions, started, stage="", alpha=False):
    """Spec 10.2: plain-text run status, first match wins."""
    if not started:
        return "Not started"
    if gate_passed(decisions, "G8"):
        return "Closed: alpha complete" if alpha else "Closed"
    if gate_passed(decisions, "G7"):
        return "Outputs signed off"
    if gate_passed(decisions, "G6"):
        return "Judgements validated"
    return f"In progress: {stage}" if stage else "In progress"


def header(up, crumbs, countries, current=""):
    """Shared header: product name, breadcrumb, country switcher, link to the explainer.
    crumbs: [(label, href or '')]; countries: [(code, name, href or '', is_draft)]."""
    bc = " <span aria-hidden=\"true\">›</span> ".join(
        (f'<a href="{escape(h)}">{escape(l)}</a>' if h else f'<span>{escape(l)}</span>') for l, h in crumbs)
    opts = '<option value="">Choose a country</option>'
    for cc, name, href, draft in countries:
        if href:
            sel = " selected" if cc == current else ""
            opts += f'<option value="{escape(up + href)}"{sel}>{escape(name)}{" (draft)" if draft else ""}</option>'
        else:
            opts += f'<option value="" disabled>{escape(name)} (not started)</option>'
    return (f'<header class="fe-head"><div class="fe-bar"><a class="fe-brand" href="{escape(up)}analysis.html">EU Accession Reform Intelligence</a>'
            f'<nav class="crumbs" aria-label="Breadcrumb">{bc}<span id="crumb-issue"></span></nav>'
            f'<label class="fe-sw"><span class="vh">Country</span><select aria-label="Country" onchange="if(this.value)location.href=this.value">{opts}</select></label>'
            f'<a class="fe-how" href="{escape(up)}tool-explainer.html">How the tool works</a></div></header>')


# Tokens from tool-explainer.html, mapped onto the variable names the shared page CSS already uses. The existing dark-mode
# block keeps precedence because its selectors are more specific.
CSS = """
:root { --bg:#f6f5f1; --surface:#ffffff; --text:#15202e; --muted:#465263; --border:#e2dfd7; --accent:#2c4f78;
  --ink-3:#7a8392; --brand:#18324f;
  --in:#776d5e; --in-bg:#f0ece4; --ai:#0d6e69; --ai-bg:#e2f1ee; --data:#284a7a; --data-bg:#e7edf6;
  --gate:#a86400; --gate-bg:#fcefd6; --judg:#664a98; --judg-bg:#eee8f7; --out:#22663f; --out-bg:#e1efe6;
  --good:#22663f; --bad:#a3312a; --flat:#5f6873; --radius:14px; --shadow:0 1px 2px rgba(21,32,46,.05),0 6px 20px rgba(21,32,46,.06); }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --ink-3:#a2a8b1; --brand:#cfe0f5; --in:#cbbfae; --in-bg:#2c2924; --ai:#7fd0c7; --ai-bg:#16302d;
  --data:#a9c3ea; --data-bg:#1b2738; --gate:#f0c27a; --gate-bg:#3a2c12; --judg:#cdb8ec; --judg-bg:#2b2340; --out:#a8dcb3; --out-bg:#1b3324;
  --good:#8fd3a2; --bad:#f0a39c; --flat:#b4bac3; } }
:root[data-theme="dark"] { --ink-3:#a2a8b1; --brand:#cfe0f5; --in:#cbbfae; --in-bg:#2c2924; --ai:#7fd0c7; --ai-bg:#16302d; --data:#a9c3ea; --data-bg:#1b2738;
  --gate:#f0c27a; --gate-bg:#3a2c12; --judg:#cdb8ec; --judg-bg:#2b2340; --out:#a8dcb3; --out-bg:#1b3324; --good:#8fd3a2; --bad:#f0a39c; --flat:#b4bac3; }
body { font-family: "Inter","Segoe UI",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif; }
.wrap { max-width: 1180px; }
section { border-radius: var(--radius); box-shadow: var(--shadow); }
.vh { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
.fe-head { position: sticky; top: 0; z-index: 20; background: var(--bg); border-bottom: 1px solid var(--border); padding: 0; margin: 0 0 12px; }
.fe-bar { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 18px; padding: 10px 0; }
.fe-brand { font-weight: 700; font-size: .95rem; color: var(--brand); text-decoration: none; white-space: nowrap; }
.crumbs { display: flex; flex-wrap: wrap; gap: 6px; margin: 0; font-size: .9rem; color: var(--muted); flex: 1 1 260px; }
.crumbs a { text-decoration: none; }
.fe-sw select { font: inherit; font-size: .9rem; padding: 5px 8px; border: 1px solid var(--border); border-radius: 8px; background: var(--surface); color: var(--text); }
.fe-how { font-size: .9rem; font-weight: 600; text-decoration: none; border: 1px solid var(--accent); border-radius: 999px; padding: 5px 12px; white-space: nowrap; }
.pagehead h1 { font-size: 1.7rem; margin: 6px 0 4px; }
.runline { color: var(--muted); margin: 0 0 4px; }
.sc { display: inline-block; font-size: .78rem; font-weight: 700; padding: 2px 9px; border-radius: 999px; white-space: nowrap; vertical-align: middle; }
.sc-validated { background: var(--out-bg); color: var(--out); } .sc-pending { background: var(--gate-bg); color: var(--gate); }
.sc-proposed { background: var(--judg-bg); color: var(--judg); } .sc-draft { background: var(--data-bg); color: var(--data); }
.sc-notstarted { background: transparent; color: var(--muted); border: 1px solid var(--border); }
.tag { display: inline-block; font-size: .76rem; font-weight: 600; padding: 1px 8px; border-radius: 6px; border: 1px solid var(--border); color: var(--muted); white-space: nowrap; vertical-align: middle; background: transparent; }
.bd { display: inline-flex; align-items: center; gap: 4px; font-size: .84rem; padding: 2px 9px; margin: 2px 6px 2px 0; border-radius: 8px; border: 1px solid var(--border); background: var(--surface); white-space: nowrap; }
.bd b { font-weight: 700; } .bd .ic { font-size: .9em; }
.bd.t-good { border-color: var(--good); color: var(--good); } .bd.t-bad { border-color: var(--bad); color: var(--bad); } .bd.t-flat { color: var(--flat); }
.bd.t-hi { border-color: var(--bad); } .bd.t-med { border-color: var(--gate); } .bd.t-lo { border-color: var(--border); }
.bd.t-gap3 { background: var(--gate-bg); border-color: var(--gate); } .bd.t-gap2 { background: color-mix(in srgb, var(--gate-bg) 50%, var(--surface)); } .bd.t-gap1 { background: var(--surface); }
.bd.t-ie, .hm td.ie { background: repeating-linear-gradient(135deg, transparent 0 5px, var(--border) 5px 7px); color: var(--muted); }
.bd.t-none { color: var(--muted); border-style: dashed; }
@media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto !important; transition: none !important; } }
@media (max-width: 700px) { .fe-bar { gap: 6px 10px; } .crumbs { flex-basis: 100%; order: 3; } }
"""
