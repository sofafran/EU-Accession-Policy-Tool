#!/usr/bin/env python3
"""Return the next free permanent ID of a given type. Never reuses an ID."""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (FAMILIES, ITEM_ID_RE, SOURCE_ID_RE, evidence_files,  # noqa: E402
                    project_root, read_csv, read_json)

__version__ = "1.0.0"

# type: (csv path, id column, prefix template, digits)
SIMPLE = {
    "requirement": ("registers/source_requirements.csv", "requirement_id", "REQ-", 3),
    "limit": ("registers/limits_log.csv", "limit_id", "LIM-", 4),
    "gate": ("registers/gate_log.csv", "gate_decision_id", "GATE-", 4),
    "mechanism": ("taxonomy/mechanisms.csv", "mechanism_id", "MEC-", 2),
    "comparator": ("entities/comparator_cases.csv", "case_id", "CMP-", 4),
    "link": ("links/links.csv", "link_id", "LNK-", 6),
    "judgement": ("judgements/judgements.csv", "judgement_id", "JDG-", 6),
    "sq": ("judgements/source_quality.csv", "sq_id", "SQ-", 5),
}


def max_seq(ids, prefix, digits):
    pat = re.compile(rf"^{re.escape(prefix)}(\d{{{digits}}})$")
    nums = [int(m.group(1)) for i in ids if (m := pat.match(i))]
    return max(nums, default=0)


def fmt(prefix, n, digits):
    if n >= 10 ** digits:
        raise SystemExit(f"error: {prefix} sequence exhausted at {digits} digits")
    return f"{prefix}{n:0{digits}d}"


def ids_in(root, rel, col):
    _, rows = read_csv(Path(root) / rel)
    return [r.get(col, "") for r in rows]


def next_source(root, country, family, year):
    prefix = f"{country}-{family}-{year}-"
    seen = ids_in(root, "registers/source_register.csv", "source_id")
    # Files already on disk count too, in case a register row is still being written.
    for f in (Path(root) / "sources").glob(f"{country}/{family}/*/*"):
        m = re.match(r"^([A-Z]{2,3}-[A-Z]+-\d{4}-\d{3})", f.name)
        if m:
            seen.append(m.group(1))
    seen += [f.stem for f in evidence_files(root)]
    return fmt(prefix, max_seq(seen, prefix, 3) + 1, 3)


def next_item(root, source_id):
    m = SOURCE_ID_RE.match(source_id)
    if not m:
        raise SystemExit(f"error: not a source ID: {source_id}")
    path = Path(root) / "evidence" / m.group(1) / f"{source_id}.json"
    ids = []
    if path.exists():
        ids = [it.get("item_id", "") for it in read_json(path).get("items", [])]
    nums = [int(mm.group(2)) for i in ids if (mm := ITEM_ID_RE.match(i)) and mm.group(1) == source_id]
    return fmt(f"{source_id}-", max(nums, default=0) + 1, 4)


def next_with_country(root, rel, col, kind, code):
    return fmt(f"{kind}-{code}-", max_seq(ids_in(root, rel, col), f"{kind}-{code}-", 4) + 1, 4)


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Print the next free ID of a given type, reading the relevant CSV or evidence folder. "
                    "IDs are never reused: the next ID is one more than the highest ever recorded, including excluded or retired records.")
    p.add_argument("type", choices=sorted(list(SIMPLE) + ["source", "item", "issue", "intervention", "actor", "lesson"]))
    p.add_argument("--country", help="country code (source, intervention, actor; actor also accepts EU or INT)")
    p.add_argument("--family", choices=FAMILIES, help="source family (source)")
    p.add_argument("--year", help="publication year (source)")
    p.add_argument("--source-id", help="source ID (item)")
    p.add_argument("--area", help="reform issue area code (issue)")
    p.add_argument("--run", default="RUN-2026-01", help="run ID (lesson); default RUN-2026-01")
    p.add_argument("--root", help="project root (default: the folder above tools/)")
    p.add_argument("--version", action="version", version=__version__)
    a = p.parse_args(argv)
    root = project_root(a.root)

    def need(*names):
        missing = [n for n in names if not getattr(a, n.replace("-", "_"))]
        if missing:
            p.error(f"{a.type} needs --{', --'.join(missing)}")

    if a.type in SIMPLE:
        rel, col, prefix, digits = SIMPLE[a.type]
        print(fmt(prefix, max_seq(ids_in(root, rel, col), prefix, digits) + 1, digits))
    elif a.type == "source":
        need("country", "family", "year")
        if not re.fullmatch(r"[A-Z]{2,3}", a.country) or not re.fullmatch(r"\d{4}", a.year):
            p.error("country must be 2 or 3 capital letters and year four digits")
        print(next_source(root, a.country, a.family, a.year))
    elif a.type == "item":
        need("source-id")
        print(next_item(root, a.source_id))
    elif a.type == "issue":
        need("area")
        prefix = f"RI-{a.area}-"
        print(fmt(prefix, max_seq(ids_in(root, "taxonomy/reform_issues.csv", "issue_id"), prefix, 3) + 1, 3))
    elif a.type == "intervention":
        need("country")
        print(next_with_country(root, "entities/interventions.csv", "intervention_id", "INT", a.country))
    elif a.type == "actor":
        need("country")
        print(next_with_country(root, "entities/actors.csv", "actor_id", "ACT", a.country))
    elif a.type == "lesson":
        rel = f"runs/{a.run}/alpha_learning_log.csv"
        print(fmt("ALN-", max_seq(ids_in(root, rel, "lesson_id"), "ALN-", 4) + 1, 4))
    return 0


if __name__ == "__main__":
    sys.exit(main())
