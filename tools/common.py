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


# Countries (E19). One list for every tool: the accession countries in the rollout plan and the comparator countries
# used so far. Kosovo uses XKX, the code in common use; the EU designation "Kosovo*" and its footnote are set in the run record.
COUNTRIES = {
    "MKD": "North Macedonia", "MNE": "Montenegro", "ALB": "Albania", "MDA": "Moldova", "UKR": "Ukraine",
    "SRB": "Serbia", "BIH": "Bosnia and Herzegovina", "GEO": "Georgia", "TUR": "Türkiye", "XKX": "Kosovo",
    "HRV": "Croatia",
}


MULTI = "multi"  # register country of a horizontal EU document that covers several enlargement countries (PC-26)

# Optional columns added by data dictionary 1.7 (PC-27, PC-28). Tools read them when present and work without them.
OPTIONAL_COLUMNS = {
    "registers/source_requirements.csv": ("run_ids",),
    "registers/source_register.csv": ("used_in_runs",),
    "entities/actors.csv": ("successor_id",),
    "entities/interventions.csv": ("successor_id",),
}


def run_country(root, run_id):
    """Country code of a run, from the `Target country` field of its run record, written as `Name (CCC)`."""
    fields, _ = run_record(root, run_id)
    m = re.search(r"\(([A-Z]{3})\)", fields.get("Target country", ""))
    if not m:
        raise ValueError(f"{run_id}: the run record's Target country must end with the country code in brackets, for example 'Montenegro (MNE)'")
    return m.group(1)


def country_name(code):
    return COUNTRIES.get(code, code)


def lessons_path(root, run_id):
    """The run's curated lessons file: learning_log.csv from RUN-2026-02 on, alpha_learning_log.csv in the alpha (E19)."""
    d = Path(root) / "runs" / run_id
    return d / "learning_log.csv" if (d / "learning_log.csv").exists() or not (d / "alpha_learning_log.csv").exists() else d / "alpha_learning_log.csv"


def gate_id(root, run_id, gate):
    """Gate decision ID of the latest pass of a gate for a run, or ''."""
    r = gate_decisions(root, run_id).get(gate)
    return r["gate_decision_id"] if r and r.get("decision") in ("pass", "pass_with_conditions") else ""


def runs_with_records(root):
    """Run IDs that have a run record, in ID order (the template folder is skipped)."""
    return sorted(p.parent.name for p in (Path(root) / "runs").glob("RUN-*/run_record.md"))


def review_page_name(root, run_id):
    """File name of a run's review page: index.html for the active run, review_<run_id>.html for an earlier run (E19, E20)."""
    runs = runs_with_records(root)
    return "index.html" if runs and run_id == runs[-1] else f"review_{run_id}.html"


# Several runs per evidence file (evidence schema 1.3, decision E21). The file's `extraction` is the latest run's;
# earlier runs' records sit unchanged in `earlier_extractions`, each with the item IDs that run created.
def extraction_runs(data):
    """One entry per run that extracted this source, oldest first: run_id, run_country, role, item_ids (set), extraction, classification."""
    out, earlier_ids = [], set()
    for e in data.get("earlier_extractions", []):
        out.append({**e, "item_ids": set(e["item_ids"])})
        earlier_ids |= set(e["item_ids"])
    ext = data.get("extraction", {})
    own = {it["item_id"] for it in data.get("items", []) if it["item_id"] not in earlier_ids}
    out.append({"run_id": ext.get("run_id"), "run_country": ext.get("run_country"), "role": ext.get("role"),
                "item_ids": own, "extraction": ext, "classification": data.get("classification", {})})
    return out


def run_extraction(data, run_id):
    """This run's entry from extraction_runs, or None if the run has not extracted the source."""
    return next((e for e in extraction_runs(data) if e["run_id"] == run_id), None)


def run_items(data, run_id):
    """Items created by this run's extraction of the source. Each item belongs to exactly one run."""
    e = run_extraction(data, run_id)
    return [it for it in data.get("items", []) if e and it["item_id"] in e["item_ids"]]


def register_role(row, run_id, run_cc):
    """A register row's role in one run, or None if the run did not use the source (E21). The first role listed belongs
    to the run that registered the source (`added_in_run`); a later `target` role belongs to the later run whose target
    country the source is about, or to any later run for a horizontal document (country `multi`, PC-26). Where `used_in_runs`
    is filled in (data dictionary 1.7, PC-27), it decides instead: the run's role is the one at the same position in `role`."""
    roles = [x for x in row.get("role", "").split(";") if x]
    if not roles:
        return None
    used = split_list(row.get("used_in_runs"))
    if used:  # data dictionary 1.7 (PC-27): the run is stated, with roles in the same order
        if run_id not in used:
            return None
        k = used.index(run_id)
        return roles[k] if k < len(roles) else roles[-1]
    if row.get("added_in_run") == run_id:
        return roles[0]
    if (row.get("added_in_run") or "") < run_id and "target" in roles[1:] and row.get("country") in (run_cc, MULTI):
        return "target"
    return None


def run_requirements(root, run_id, rows=None):
    """Requirement lines of one run (E21): lines approved at one of the run's gates, plus unapproved lines about the run's
    target country. Where `run_ids` is filled in (data dictionary 1.7, PC-27) it decides instead; until then the gate that
    approved a line identifies its run."""
    if rows is None:
        rows = read_csv(Path(root) / "registers" / "source_requirements.csv")[1]
    gates = {r["gate_decision_id"] for r in read_csv(Path(root) / "registers" / "gate_log.csv")[1] if r.get("run_id") == run_id}
    cc = run_country(root, run_id)

    def mine(r):
        if split_list(r.get("run_ids")):  # data dictionary 1.7 (PC-27): the run is stated
            return run_id in split_list(r.get("run_ids"))
        return r.get("approved_at") in gates or (not r.get("approved_at") and r.get("country") == cc and r.get("role") == "target")
    return [r for r in rows if mine(r)]


def run_sources(root, run_id, rows=None):
    """Register rows of the sources one run used, with `role` set to the role in that run (see register_role)."""
    if rows is None:
        rows = read_csv(Path(root) / "registers" / "source_register.csv")[1]
    cc = run_country(root, run_id)
    return [{**r, "role": role} for r in rows for role in [register_role(r, run_id, cc)] if role]
