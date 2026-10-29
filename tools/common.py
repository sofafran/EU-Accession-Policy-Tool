"""Shared helpers for the project tools. Not a command-line tool itself."""

import csv
import json
import re
import unicodedata
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent
FAMILIES = ("EU", "GOV", "IO", "RES", "CSO")
SOURCE_ID_RE = re.compile(r"^([A-Z]{2,3})-(EU|GOV|IO|RES|CSO)-(\d{4})-(\d{3})$")
ITEM_ID_RE = re.compile(r"^([A-Z]{2,3}-(?:EU|GOV|IO|RES|CSO)-\d{4}-\d{3})-(\d{4})$")
PAGE_RE = re.compile(r"^=== PAGE (\d+) ===$")
SECTION_RE = re.compile(r"^=== SECTION: (.*) ===$")


def project_root(arg=None):
    return Path(arg).resolve() if arg else DEFAULT_ROOT


def read_csv(path):
    """Return (header, rows as dicts). Missing file gives ([], [])."""
    path = Path(path)
    if not path.exists():
        return [], []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return [], []
    header = rows[0]
    return header, [dict(zip(header, r)) for r in rows[1:] if any(c.strip() for c in r)]


def write_csv(path, header, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow([r.get(h, "") for h in header])


def read_json(path):
    with Path(path).open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def split_list(value):
    """Split a semicolon-separated cell into a list, ignoring blanks."""
    return [v.strip() for v in (value or "").split(";") if v.strip()]


def nfc(text):
    return unicodedata.normalize("NFC", text)


def evidence_files(root):
    return sorted((Path(root) / "evidence").glob("*/*.json"))


def text_path_for(root, source_id):
    m = SOURCE_ID_RE.match(source_id)
    if not m:
        raise ValueError(f"not a source ID: {source_id}")
    return Path(root) / "sources" / m.group(1) / m.group(2) / "text" / f"{source_id}.txt"


def parse_markdown_table(lines):
    """Parse consecutive Markdown table lines into a list of row lists (header first)."""
    rows = []
    for line in lines:
        line = line.strip()
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            continue
        rows.append(cells)
    return rows


def dictionary_tables(root):
    """Map each CSV path in the data dictionary to its list of field names, in order."""
    text = (Path(root) / "schemas" / "data_dictionary.md").read_text(encoding="utf-8").splitlines()
    tables = {}
    for i, line in enumerate(text):
        m = re.match(r"^## (\S+\.csv)\s*$", line)
        if not m:
            continue
        j = i + 1
        while j < len(text) and not text[j].lstrip().startswith("|"):
            j += 1
        rows = parse_markdown_table(text[j:])
        tables[m.group(1)] = [r[0] for r in rows[1:]]
    return tables


def run_record(root, run_id):
    """Return the field/value table of a run record as a dict, plus the raw text."""
    path = Path(root) / "runs" / run_id / "run_record.md"
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("| Field |"))
    rows = parse_markdown_table(lines[start:])
    return {r[0]: r[1] for r in rows[1:] if len(r) >= 2}, text


def gate_decisions(root, run_id):
    """Latest decision row per gate for the run, from the gate log."""
    _, rows = read_csv(Path(root) / "registers" / "gate_log.csv")
    latest = {}
    for r in rows:
        if r.get("run_id") == run_id:
            latest[r["gate"]] = r
    return latest


def gate_passed(decisions, gate):
    r = decisions.get(gate)
    return bool(r) and r.get("decision") in ("pass", "pass_with_conditions")
