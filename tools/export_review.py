#!/usr/bin/env python3
"""Build the review spreadsheet for a gate from the project CSV and JSON files."""

import argparse
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import parse_markdown_table, project_root, read_csv, run_record  # noqa: E402

__version__ = "1.4.1"
TOOLS = ["hash_file.py", "next_id.py", "convert_to_text.py", "verify_quotes.py", "validate_data.py",
         "export_review.py", "build_review_page.py"]


PROTECTED = ("G3_handcoding.xlsx", "G3_review_sample.xlsx")  # workbooks the analyst fills in: never overwritten without --force


def write_workbook(path, sheets, dropdowns=None):
    """sheets: list of (title, header, rows). Header bold, top row frozen, filters on, text wrapped.
    dropdowns: {sheet title: {column header: [allowed values]}} adds a drop-down list to that column."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    wb = Workbook()
    wb.remove(wb.active)
    for title, header, rows in sheets:
        ws = wb.create_sheet(title[:31])
        ws.append(header)
        for r in rows:
            ws.append(["" if v is None else str(v) for v in r])
        for c in ws[1]:
            c.font = Font(bold=True)
            c.fill = PatternFill("solid", fgColor="DDE6F0")
        for col in range(1, len(header) + 1):
            longest = max([len(str(header[col - 1]))] + [len(str(r[col - 1])) for r in rows if col - 1 < len(r)])
            ws.column_dimensions[get_column_letter(col)].width = min(max(12, longest + 2), 70)
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.freeze_panes = "A2"
        if rows:
            ws.auto_filter.ref = ws.dimensions
        for col_name, values in ((dropdowns or {}).get(title) or {}).items():
            from openpyxl.worksheet.datavalidation import DataValidation
            col = get_column_letter(header.index(col_name) + 1)
            dv = DataValidation(type="list", formula1='"' + ",".join(values) + '"', allow_blank=True)
            ws.add_data_validation(dv)
            dv.add(f"{col}2:{col}{max(2, len(rows) + 1)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def table_sheet(title, header, rows, first=None):
    """A sheet from dict rows, optionally with rows matching `first` sorted to the top."""
    rows = sorted(rows, key=lambda r: 0 if first and first(r) else 1)
    return title, header, [[r.get(h, "") for h in header] for r in rows]


def tool_versions(root):
    out = []
    for t in TOOLS:
        f = root / "tools" / t
        if not f.exists():
            out.append([t, "missing", ""])
            continue
        m = re.search(r'^__version__ = "([^"]+)"', f.read_text(encoding="utf-8"), re.M)
        out.append([t, m.group(1) if m else "unknown", ""])
    report = root / "tools" / "tests" / "last_report.csv"
    if report.exists():
        _, rows = read_csv(report)
        res = Counter((r["tool"], r["result"]) for r in rows)
        for row in out:
            p, f = res.get((row[0], "pass"), 0), res.get((row[0], "fail"), 0)
            row[2] = f"{p} passed, {f} failed" if p or f else "no tests recorded"
    return out


def validation_lines(root):
    r = subprocess.run([sys.executable, str(root / "tools" / "validate_data.py"), "--root", str(root)], capture_output=True, text=True)
    return [[line] for line in r.stdout.splitlines()]


def lessons_sheet(root, run):
    header, rows = read_csv(root / "runs" / run / "alpha_learning_log.csv")
    header = header + ["reviewer_decision", "reviewer_comment"] if header else ["lesson_id"]
    return table_sheet("Alpha lessons", header, rows, first=lambda r: r.get("status") == "open")


def decision_register(root):
    lines = (root / "decisions" / "decision_log.md").read_text(encoding="utf-8").splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("| ID |"))
    rows = parse_markdown_table(lines[start:])
    return rows[0], rows[1:]


def g0(root, run):
    rec, _ = run_record(root, run)
    header, limits = read_csv(root / "registers" / "limits_log.csv")
    active = [r for r in limits if r["run_id"] == run and r["status"] == "active"]
    other = [r for r in limits if r["run_id"] == run and r["status"] != "active"]
    th_header, themes = read_csv(root / "taxonomy" / "themes.csv")
    dec_header, decisions = decision_register(root)
    needed = [
        ["Evidence freeze date", rec.get("Evidence freeze date", ""), "Set the date (G0 cannot pass while it is TBC)"],
        ["Target country", rec.get("Target country", ""), "Approve"],
        ["Thematic scope", rec.get("Thematic scope", ""), "Approve"],
        ["Time window", rec.get("Time window", ""), "Approve"],
        ["Language", rec.get("Language", ""), "Approve"],
        ["Comparator scope", rec.get("Comparator scope", ""), "Approve"],
        ["Formal gate approvers", rec.get("Reviewers", ""), "Approve"],
        ["Alpha reviewers", rec.get("Alpha reviewers", ""), "Approve"],
        ["Theme list", rec.get("Theme list version", ""), "Approve (sheet 'Theme list')"],
        ["Codebooks", rec.get("Codebooks version", ""), "Approve"],
        ["Data dictionary and evidence schema", f"{rec.get('Data dictionary version', '')}; schema {rec.get('Evidence schema version', '')}", "Approve"],
        ["Extraction, classification and judgement rules", f"{rec.get('Extraction rules version', '')}; {rec.get('Classification rules version', '')}; {rec.get('Judgement rules version', '')}", "Approve as drafts for use until G3, G5 and G6"],
        ["Mechanism list", rec.get("Mechanism list version", ""), "Note only: approved at G4"],
        ["Helper tools", rec.get("Tools versions", ""), "Approve (sheet 'Tools')"],
        ["Active limits", ", ".join(r["limit_id"] for r in active), "Approve (sheet 'Active limits')"],
        ["Decisions behind this configuration", "", "Confirm the decisions taken for this run (sheet 'Decision register')"],
        ["Alpha lessons", ", ".join(r["lesson_id"] for r in read_csv(root / "runs" / run / "alpha_learning_log.csv")[1] if r["status"] == "open"), "Set a status for each (sheet 'Alpha lessons')"],
    ]
    return "G0_run_setup.xlsx", [
        ("Decisions needed", ["item", "current value", "decision needed", "reviewer_decision", "reviewer_comment"], [n + ["", ""] for n in needed]),
        ("Run record", ["field", "value"], [[k, v] for k, v in rec.items()]),
        table_sheet("Active limits", header, active),
        table_sheet("Superseded limits", header, other),
        table_sheet("Theme list", th_header, themes),
        ("Decision register", dec_header, decisions),
        lessons_sheet(root, run),
        ("Tools", ["tool", "version", "tests"], tool_versions(root)),
        ("Validation", ["validate_data output"], validation_lines(root)),
    ]


def g1(root, run):
    header, rows = read_csv(root / "registers" / "source_requirements.csv")
    return "G1_source_requirements.xlsx", [
        table_sheet("Requirements", header + ["reviewer_decision", "reviewer_comment"], rows, first=lambda r: not r.get("approved_at")),
        lessons_sheet(root, run),
        ("Validation", ["validate_data output"], validation_lines(root)),
    ]


def g2(root, run):
    reg_h, reg = read_csv(root / "registers" / "source_register.csv")
    req_h, req = read_csv(root / "registers" / "source_requirements.csv")
    sq_h, sq = read_csv(root / "judgements" / "source_quality.csv")
    gaps = {"open", "not_found", "partly_found", "not_public"}
    excluded = [r for r in reg if r.get("status") != "available"]
    coverage = [["family", k, v] for k, v in sorted(Counter(r["source_family"] for r in reg if r.get("status") == "available").items())]
    coverage += [["year", k, v] for k, v in sorted(Counter(r["publication_date"][:4] for r in reg if r.get("status") == "available").items())]
    coverage += [["chapter", k, v] for k, v in sorted(Counter(c for r in reg if r.get("status") == "available" for c in r["chapters_covered"].split(";") if c).items())]
    coverage += [["theme", k, v] for k, v in sorted(Counter(t for r in reg if r.get("status") == "available" for t in r["themes_covered"].split(";") if t).items())]
    coverage += [["language", k, v] for k, v in sorted(Counter(r["language"] for r in reg if r.get("status") == "available").items())]
    coverage += [["requirements with gaps", "", sum(r.get("status") in gaps for r in req)]]
    return "G2_source_review.xlsx", [
        table_sheet("Source register", reg_h, reg),
        table_sheet("Requirements", req_h, req, first=lambda r: r.get("status") in gaps),
        table_sheet("Exclusions", reg_h, excluded),
        table_sheet("Source quality", sq_h + ["reviewer_decision", "reviewer_comment"], sq,
                    first=lambda r: r.get("overall") in ("Low", "insufficient_evidence") or r.get("topic_expertise") != "yes"),
        ("Coverage", ["dimension", "value", "available sources"], coverage),
        lessons_sheet(root, run),
        ("Validation", ["validate_data output"], validation_lines(root)),
    ]


def passage_text(root, source_id, page, start, end):
    """Text of a passage: from `start` up to (not including) `end` on the cited page, or the whole page."""
    from common import PAGE_RE, text_path_for
    lines, cur = [], None
    for line in text_path_for(root, source_id).read_text(encoding="utf-8").splitlines():
        m = PAGE_RE.match(line)
        if m:
            cur = int(m.group(1))
        elif cur == int(page):
            lines.append(line)
    text = "\n".join(lines)
    i = text.find(start) if start else 0
    if i < 0:
        raise SystemExit(f"error: start text not found on page {page} of {source_id}: {start!r}")
    j = text.find(end, i + 1) if end else -1
    return text[i:j if j > 0 else None].strip()


def g3_handcoding(root, run):
    """Hand-coding workbook for stage 5: the proposed sample, the passages and empty item rows (P2, stage 5)."""
    _, passages = read_csv(root / "review" / run / "G3_passages.csv")
    _, sample = read_csv(root / "review" / run / "G3_sample.csv")
    reg = {r["source_id"]: r for r in read_csv(root / "registers" / "source_register.csv")[1]}
    if not passages:
        raise SystemExit(f"error: review/{run}/G3_passages.csv is missing or empty")
    instructions = [
        ["1", "Read a passage in sheet 'Passages'."],
        ["2", "In sheet 'Hand-coded items', add one row for each claim you find in it: pick its type, paste the sentence, and pick its scope."],
        ["3", "Types: finding (judges the situation), recommendation (says what should happen), intervention (a law, strategy, system or programme), barrier (what blocks progress), outcome (result of a named action), lesson, metric (a number)."],
        ["4", "Scope: chapter (Chapter 2, workers), technology (the technology or digital issue itself is the subject), both, or out (not in scope)."],
        ["5", "If one sentence makes two claims of different types, use two rows with the same sentence. Leave the other columns empty."],
        ["6", "Do this before looking at any agent output for these passages."],
    ]
    item_header = ["passage_id", "item_no", "information_type", "stated_text", "scope", "note"]
    items = [[p["passage_id"], str(n), "", "", "", ""] for p in passages for n in range(1, 13)]
    return "G3_handcoding.xlsx", [
        ("Instructions", ["step", "what to do"], instructions),
        ("Passages", ["passage_id", "source_id", "title", "page", "why chosen", "text"],
         [[p["passage_id"], p["source_id"], reg.get(p["source_id"], {}).get("title", ""), p["page"], p["why"],
           passage_text(root, p["source_id"], p["page"], p["start_text"], p["end_text"])] for p in passages]),
        ("Hand-coded items", item_header, items),
    ], {"Hand-coded items": {"information_type": ["finding", "recommendation", "intervention", "barrier", "outcome", "lesson", "metric"],
                             "scope": ["chapter", "technology", "both", "out"]}}


def norm(text):
    import unicodedata
    return " ".join(re.sub(r"[^\w\s]", " ", unicodedata.normalize("NFC", text or "").casefold()).split())


def similar(a, b):
    """Two quotes refer to the same item if one contains the other or most of their words overlap."""
    a, b = norm(a), norm(b)
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    wa, wb = set(a.split()), set(b.split())
    return len(wa & wb) / max(1, min(len(wa), len(wb))) >= 0.6


def handcoded(root, run):
    """Rows filled in by the analyst in the hand-coding workbook, grouped by passage."""
    path = root / "review" / run / "G3_handcoding.xlsx"
    out = {}
    if not path.exists():
        return out
    from openpyxl import load_workbook
    ws = load_workbook(path, data_only=True)["Hand-coded items"]
    header = [c.value for c in ws[1]]
    for row in ws.iter_rows(min_row=2, values_only=True):
        r = dict(zip(header, row))
        if r.get("passage_id") and (r.get("stated_text") or "").strip():
            out.setdefault(r["passage_id"], []).append(r)
    return out


def review_sample(root, run, n_kept=50, n_removed=20, seed="RUN-2026-01-G3"):
    """Stratified sample for a light manual check: kept items spread across sources, with flagged and translated
    items over-represented, plus items removed by the rule revisions. Items inside a passage not yet hand-coded are left out."""
    import random
    from common import evidence_files, read_json
    rng = random.Random(seed)
    _, passages = read_csv(root / "review" / run / "G3_passages.csv")
    hand = handcoded(root, run)
    open_p = [(p, norm(passage_text(root, p["source_id"], p["page"], p["start_text"], p["end_text"]))) for p in passages if p["passage_id"] not in hand]
    kept = {}
    for f in evidence_files(root):
        d = read_json(f)
        for it in d["items"]:
            if any(p["source_id"] == d["source_id"] and it["location"].get("page") == int(p["page"]) and norm(it["stated_text"]) in t for p, t in open_p):
                continue
            kept[it["item_id"]] = {**it, "_source": d["source_id"]}
    removed = {}
    for old in sorted((root / "review" / run).glob("sample_*/*.json")):
        for it in read_json(old)["items"]:
            if it["item_id"] not in kept:
                removed[it["item_id"]] = {**it, "_source": old.stem, "_rules": old.parent.name.replace("sample_", "")}

    def pick(pool, n, risky):
        by_src = {}
        for it in pool.values():
            by_src.setdefault(it["_source"], []).append(it)
        sources = sorted(by_src)
        if not sources:
            return []
        alloc = {s: min(len(by_src[s]), max(2, round(n * len(by_src[s]) / max(1, len(pool))))) for s in sources}
        while sum(alloc.values()) > n:
            s = max(alloc, key=lambda k: alloc[k])
            alloc[s] -= 1
        chosen = []
        for s in sources:
            items = sorted(by_src[s], key=lambda i: i["item_id"])
            hot = [i for i in items if risky(i)]
            take = rng.sample(hot, min(len(hot), (alloc[s] + 1) // 2))
            rest = [i for i in items if i not in take]
            take += rng.sample(rest, min(len(rest), alloc[s] - len(take)))
            chosen += take
        return sorted(chosen, key=lambda i: i["item_id"])

    risky = lambda i: bool(set(i["flags"]) & {"theme_doubtful", "ambiguous_type", "out_of_window", "possible_misread"}) or i.get("machine_translated")
    return pick(kept, n_kept, risky), pick(removed, n_removed, lambda i: "theme" in i["scope_basis"])


def g3_review_sample(root, run):
    reg = {r["source_id"]: r for r in read_csv(root / "registers" / "source_register.csv")[1]}
    kept, removed = review_sample(root, run)

    def src(i):
        r = reg.get(i["_source"], {})
        return f"{r.get('institution', '')}, {(r.get('publication_date') or '')[:4]}"

    def scope(i):
        s = " and ".join("technology" if b == "theme" else b for b in i["scope_basis"])
        return s + (f" ({', '.join(i['themes'])})" if i["themes"] else "")
    start = [
        ["What this is", f"A light check of the extraction method: {len(kept)} items the agent kept and {len(removed)} items the rule changes removed, chosen at random across all sources, with doubtful and translated items over-represented."],
        ["Sheet 'Kept items'", "For each row, answer two questions in the yellow columns: Is the type right? Should it be in scope? If not, say what it should be in 'comment'."],
        ["Sheet 'Removed items'", "For each row, answer one question: Should it have been kept? Say why in 'comment' if yes."],
        ["Sheet 'Missed items'", "Only if you notice something important the agent missed: paste the sentence and its source."],
        ["Time", "About 45 minutes. Short answers are enough: Yes or No from the drop-downs."],
        ["What happens next", "The agent turns your answers into accuracy figures for G3: type accuracy (target about 9 in 10), scope errors, and important items wrongly removed or missed."],
    ]
    kept_rows = [[str(n), i["item_id"], src(i), str(i["location"].get("page") or i["location"].get("section") or ""), i["information_type"],
                  i["stated_text"], i.get("translation_en") or "", scope(i), "", "", ""] for n, i in enumerate(kept, 1)]
    removed_rows = [[str(n), i["item_id"], src(i), i["information_type"], i["stated_text"], i.get("translation_en") or "", scope(i),
                     f"rules {i['_rules']}", "", ""] for n, i in enumerate(removed, 1)]
    kept_header = ["row", "item_id", "source", "page", "type given", "quote", "English (machine translation)", "scope given",
                   "Is the type right?", "Should it be in scope?", "comment"]
    removed_header = ["row", "item_id", "source", "type", "quote", "English (machine translation)", "scope it had", "last kept under",
                      "Should it have been kept?", "comment"]
    return "G3_review_sample.xlsx", [
        ("Start here", ["", ""], start),
        ("Kept items", kept_header, kept_rows),
        ("Removed items", removed_header, removed_rows),
        ("Missed items", ["source_id", "page", "sentence", "comment"], []),
    ], {"Kept items": {"Is the type right?": ["Yes", "No"], "Should it be in scope?": ["Yes", "No"]},
        "Removed items": {"Should it have been kept?": ["Yes", "No"]}}


def g3(root, run):
    """G3 sample review (P2, stage 6). Agent items inside a hand-coding passage are withheld until that passage is hand-coded."""
    from common import evidence_files, read_json
    _, passages = read_csv(root / "review" / run / "G3_passages.csv")
    hand = handcoded(root, run)
    ptext = {p["passage_id"]: (p, passage_text(root, p["source_id"], p["page"], p["start_text"], p["end_text"])) for p in passages}
    items = []
    for f in evidence_files(root):
        data = read_json(f)
        if data["extraction"]["status"] != "sample":
            continue
        for it in data["items"]:
            it["_source"] = data["source_id"]
            it["_passage"] = next((pid for pid, (p, t) in ptext.items() if p["source_id"] == data["source_id"]
                                   and it["location"].get("page") == int(p["page"]) and norm(it["stated_text"]) in norm(t)), "")
            items.append(it)
    withheld = [i for i in items if i["_passage"] and i["_passage"] not in hand]
    shown = [i for i in items if i not in withheld]

    def priority(i):
        return 0 if (set(i["flags"]) & {"theme_doubtful", "ambiguous_type", "possible_misread"} or not i["quote_verified"]) else 1
    verdict_cols = ["verdict (correct, wrong_type, unsupported_interpretation, wrong_reference, wrong_date_or_actor, should_not_extract)", "comment"]
    item_header = ["item_id", "source_id", "passage", "information_type", "stated_text", "translation_en", "summary", "page", "section",
                   "speaker", "subjects", "stated_status", "preparation_level", "progress_level", "event_date", "scope_basis", "themes",
                   "flags", "extraction_note", "quote_verified"] + verdict_cols
    rows = []
    for i in sorted(shown, key=priority):
        rows.append([i["item_id"], i["_source"], i["_passage"], i["information_type"], i["stated_text"], i.get("translation_en") or "",
                     i["summary"], i["location"].get("page"), i["location"].get("section") or "", i["speaker"]["name_as_stated"],
                     "; ".join(s["name_as_stated"] for s in i["subjects"]), i.get("stated_status") or "",
                     (i.get("eu_scale") or {}).get("preparation_level") or "", (i.get("eu_scale") or {}).get("progress_level") or "",
                     i["dates"].get("event_date") or "", "; ".join(i["scope_basis"]), "; ".join(i["themes"]), "; ".join(i["flags"]),
                     i.get("extraction_note") or "", "yes" if i["quote_verified"] else "NO", "", ""])
    comparison = []
    for pid, (p, _) in ptext.items():
        if pid not in hand:
            comparison.append([pid, "awaiting hand-coding", "", "", "", "Agent items for this passage are withheld until it is hand-coded"])
            continue
        agent = [i for i in items if i["_passage"] == pid]
        used = set()
        for h in hand[pid]:
            m = next((a for a in agent if a["item_id"] not in used and similar(a["stated_text"], h["stated_text"])), None)
            if m:
                used.add(m["item_id"])
                same = (h.get("information_type") or "").strip() == m["information_type"]
                comparison.append([pid, "matched" if same else "type disagreement", h["stated_text"], m["item_id"],
                                   f"{h.get('information_type')} / {m['information_type']}", ""])
            else:
                comparison.append([pid, "missed by the agent", h["stated_text"], "", h.get("information_type") or "", ""])
        for a in agent:
            if a["item_id"] not in used:
                comparison.append([pid, "extra in the agent output", a["stated_text"], a["item_id"], a["information_type"], ""])
    quote_rows = []
    qdir = root / "review" / run / "quote_checks"
    for f in sorted(qdir.glob("*.csv")) if qdir.exists() else []:
        quote_rows += [[f.stem, r["item_id"], r["result"], r["detail"]] for r in read_csv(f)[1]]
    quote_rows.sort(key=lambda r: 0 if r[2] != "pass" else 1)
    summary = []
    for sid in sorted({i["_source"] for i in items}):
        mine = [i for i in items if i["_source"] == sid]
        summary.append([sid, len(mine), ", ".join(f"{k} {v}" for k, v in sorted(Counter(i["information_type"] for i in mine).items())),
                        ", ".join(f"{k} {v}" for k, v in sorted(Counter("+".join(i["scope_basis"]) for i in mine).items())),
                        ", ".join(f"{k} {v}" for k, v in sorted(Counter(t for i in mine for t in i["themes"]).items())),
                        sum("theme_doubtful" in i["flags"] for i in mine), sum(not i["quote_verified"] for i in mine),
                        sum(1 for i in mine if i in withheld)])
    changes, removed = [], []
    for old in sorted((root / "review" / run).glob("sample_*/*.json")):
        prev = {i["item_id"]: i for i in read_json(old)["items"]}
        now_items = {i["item_id"]: i for i in items if i["_source"] == old.stem}
        kept = set(prev) & set(now_items)
        changes.append([old.parent.name.replace("sample_", ""), old.stem, len(prev), len(now_items), len(kept),
                        len(set(prev) - kept), len(set(now_items) - kept),
                        sum(1 for k in kept if prev[k]["information_type"] != now_items[k]["information_type"])])
        for k in sorted(set(prev) - kept):
            i = prev[k]
            removed.append([k, i["information_type"], i["stated_text"], "; ".join(i["scope_basis"]), "; ".join(i["themes"]), "; ".join(i["flags"])])
    return "G3_sample_review.xlsx", [
        ("Sample items", item_header, rows),
        ("Missed items", ["source_id", "page", "stated_text", "information_type", "comment"], []),
        ("Hand-coding comparison", ["passage", "result", "quote", "agent item_id", "type (analyst / agent)", "note"], comparison),
        ("Quote verification", ["source_id", "item_id", "result", "detail"], quote_rows),
        ("Summary", ["source_id", "items", "by type", "by scope basis", "themes", "theme_doubtful", "quote failures", "withheld until hand-coding"], summary),
        *[(title, *(lambda h, r: (h, [[x[k] for k in h] for x in r]))(*read_csv(root / "review" / run / "g3_qa" / fname)))
          for title, fname in (("Independent QA metrics", "g3_metrics.csv"), ("Blind coding comparison", "handcoding_comparison.csv"))
          if (root / "review" / run / "g3_qa" / fname).exists()],
        ("Changes since first sample", ["earlier rules", "source_id", "items before", "items now", "kept", "removed", "added", "retyped"], changes),
        ("Removed items", ["item_id", "information_type", "stated_text", "scope_basis", "themes", "flags"], removed),
        ("Rule issues", *(lambda h, r: (h + ["reviewer_decision", "reviewer_comment"] if h else ["issue_id"], [[x[k] for k in h] + ["", ""] for x in r]))(*read_csv(root / "review" / run / "G3_rule_issues.csv"))),
        lessons_sheet(root, run),
        ("Validation", ["validate_data output"], validation_lines(root)),
    ]


BUILDERS = {"G0": g0, "G1": g1, "G2": g2, "G3-handcoding": g3_handcoding, "G3": g3, "G3-review-sample": g3_review_sample}


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Build the review spreadsheet for a gate in review/<run_id>/, with the items needing a decision first, "
                    "so the analyst never reads raw JSON. Version 1.3.0 builds G0, G1, G2, G3 (with a comparison against any earlier sample kept in review/<run_id>/sample_<rules version>/) and the stage 5 hand-coding workbook "
                    "(from review/<run_id>/G3_passages.csv and G3_sample.csv); sheets for later gates are added and tested before those gates are reached.")
    p.add_argument("gate", choices=sorted(BUILDERS), help="gate to build the package for")
    p.add_argument("--run", default="RUN-2026-01", help="run ID (default RUN-2026-01)")
    p.add_argument("--root", help="project root (default: the folder above tools/)")
    p.add_argument("--force", action="store_true", help="overwrite a workbook the analyst fills in (hand-coding, review sample)")
    p.add_argument("--version", action="version", version=__version__)
    a = p.parse_args(argv)
    root = project_root(a.root)
    built = BUILDERS[a.gate](root, a.run)
    name, sheets, dropdowns = built if len(built) == 3 else (*built, None)
    out = root / "review" / a.run / name
    if name in PROTECTED and out.exists() and not a.force:
        raise SystemExit(f"error: {out} exists and may hold the analyst's answers; use --force to overwrite")
    write_workbook(out, sheets, dropdowns)
    print(f"wrote {out} ({len(sheets)} sheets)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
