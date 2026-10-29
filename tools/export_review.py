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

__version__ = "1.0.0"
TOOLS = ["hash_file.py", "next_id.py", "convert_to_text.py", "verify_quotes.py", "validate_data.py",
         "export_review.py", "build_review_page.py"]


def write_workbook(path, sheets):
    """sheets: list of (title, header, rows). Header bold, top row frozen, filters on, text wrapped."""
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


BUILDERS = {"G0": g0, "G1": g1, "G2": g2}


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Build the review spreadsheet for a gate in review/<run_id>/, with the items needing a decision first, "
                    "so the analyst never reads raw JSON. Version 1.0.0 builds G0, G1 and G2; sheets for later gates are added and "
                    "tested before those gates are reached.")
    p.add_argument("gate", choices=sorted(BUILDERS), help="gate to build the package for")
    p.add_argument("--run", default="RUN-2026-01", help="run ID (default RUN-2026-01)")
    p.add_argument("--root", help="project root (default: the folder above tools/)")
    p.add_argument("--version", action="version", version=__version__)
    a = p.parse_args(argv)
    root = project_root(a.root)
    name, sheets = BUILDERS[a.gate](root, a.run)
    out = root / "review" / a.run / name
    write_workbook(out, sheets)
    print(f"wrote {out} ({len(sheets)} sheets)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
