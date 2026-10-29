#!/usr/bin/env python3
"""Check the project data before a gate package is prepared."""

import argparse
import csv
import io
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (ITEM_ID_RE, SOURCE_ID_RE, dictionary_tables, evidence_files,  # noqa: E402
                    project_root, read_csv, read_json, split_list)

__version__ = "1.0.0"

ID_COLUMNS = {
    "registers/source_requirements.csv": "requirement_id",
    "registers/source_register.csv": "source_id",
    "registers/limits_log.csv": "limit_id",
    "registers/gate_log.csv": "gate_decision_id",
    "taxonomy/reform_issues.csv": "issue_id",
    "taxonomy/mechanisms.csv": "mechanism_id",
    "taxonomy/themes.csv": "theme_code",
    "taxonomy/unmatched_queue.csv": "queue_id",
    "taxonomy/ambiguous_queue.csv": "queue_id",
    "entities/interventions.csv": "intervention_id",
    "entities/actors.csv": "actor_id",
    "entities/comparator_cases.csv": "case_id",
    "links/links.csv": "link_id",
    "judgements/source_quality.csv": "sq_id",
    "judgements/judgements.csv": "judgement_id",
}

ENUMS = {
    ("registers/limits_log.csv", "status"): {"active", "lifted", "superseded"},
    ("registers/gate_log.csv", "decision"): {"pass", "pass_with_conditions", "fail"},
    ("taxonomy/themes.csv", "status"): {"draft", "approved", "retired"},
    ("taxonomy/reform_issues.csv", "status"): {"draft", "approved", "merged", "retired"},
    ("judgements/judgements.csv", "review_status"): {"proposed", "validated", "overridden"},
    ("judgements/source_quality.csv", "review_status"): {"proposed", "validated", "overridden"},
    ("links/links.csv", "review_status"): {"proposed", "validated", "rejected"},
    ("ALN", "status"): {"open", "accepted", "implemented", "deferred", "rejected"},
    ("ALN", "area"): {"workflow", "sources", "extraction", "classification", "taxonomy_matching", "review_gates",
                      "assessment", "outputs", "review_page", "tooling"},
    ("ALN", "lesson_type"): {"worked", "did_not_work", "methodological_issue", "technical_issue", "change_made",
                             "limitation_found", "recommendation"},
}


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def load_tables(root, run_ids):
    tables = {}
    for rel in list(ID_COLUMNS) + [f"runs/{r}/alpha_learning_log.csv" for r in run_ids]:
        tables[rel] = read_csv(Path(root) / rel)
    return tables


def check_headers(root, tables, rep):
    expected = dictionary_tables(root)
    for rel, (header, _) in tables.items():
        key = "runs/<run_id>/alpha_learning_log.csv" if rel.endswith("alpha_learning_log.csv") else rel
        if key not in expected:
            rep.warn(f"{rel}: not described in the data dictionary")
            continue
        if not header:
            rep.error(f"{rel}: file missing or empty")
        elif header != expected[key]:
            rep.error(f"{rel}: header does not match the data dictionary\n    expected {expected[key]}\n    found    {header}")
    for key in expected:
        if "<" not in key and key not in tables:
            rep.warn(f"{key}: in the data dictionary but not checked by this tool")


def check_ids_unique(tables, rep):
    ids = {}
    for rel, (_, rows) in tables.items():
        col = ID_COLUMNS.get(rel, "lesson_id")
        seen = set()
        for r in rows:
            v = r.get(col, "")
            if not v:
                rep.error(f"{rel}: row with empty {col}")
            elif v in seen:
                rep.error(f"{rel}: duplicate {col} {v}")
            seen.add(v)
        ids[rel] = seen
    return ids


def check_enums(tables, rep):
    for rel, (_, rows) in tables.items():
        key_rel = "ALN" if rel.endswith("alpha_learning_log.csv") else rel
        for (t, col), allowed in ENUMS.items():
            if t != key_rel:
                continue
            for r in rows:
                if r.get(col, "") and r[col] not in allowed:
                    rep.error(f"{rel}: {r.get(ID_COLUMNS.get(rel, 'lesson_id'))} has {col} '{r[col]}', not one of {sorted(allowed)}")


def check_evidence(root, schema_path, rep):
    try:
        import jsonschema
    except ImportError:
        rep.error("jsonschema is not installed; evidence files not checked against the schema")
        jsonschema = None
    schema = read_json(schema_path)
    items, files = {}, {}
    for path in evidence_files(root):
        try:
            data = read_json(path)
        except ValueError as e:
            rep.error(f"{path}: not valid JSON ({e})")
            continue
        if jsonschema:
            for err in jsonschema.Draft202012Validator(schema).iter_errors(data):
                where = "/".join(str(x) for x in err.absolute_path)
                rep.error(f"{path.name}: schema: {where}: {err.message}")
        sid = data.get("source_id", "")
        if path.stem != sid:
            rep.error(f"{path.name}: file name does not match source_id {sid}")
        m = SOURCE_ID_RE.match(sid)
        if m and path.parent.name != m.group(1):
            rep.error(f"{path.name}: stored under evidence/{path.parent.name}/ but the source ID country is {m.group(1)}")
        files[sid] = data
        for it in data.get("items", []):
            iid = it.get("item_id", "")
            mm = ITEM_ID_RE.match(iid)
            if not mm or mm.group(1) != sid:
                rep.error(f"{path.name}: item ID {iid} does not belong to source {sid}")
            if iid in items:
                rep.error(f"{path.name}: duplicate item ID {iid}")
            items[iid] = it
            if it.get("quote_verified") is False:
                rep.warn(f"{iid}: quote_verified is false; must be fixed before the item reaches a review sheet as final")
    return items, files


def check_references(tables, ids, items, files, rep):
    themes = ids["taxonomy/themes.csv"]
    sources = ids["registers/source_register.csv"] | set(files)
    issues = ids["taxonomy/reform_issues.csv"]
    mechs = ids["taxonomy/mechanisms.csv"]
    ints = ids["entities/interventions.csv"]
    actors = ids["entities/actors.csv"]
    cases = ids["entities/comparator_cases.csv"]
    gates = ids["registers/gate_log.csv"]
    reqs = ids["registers/source_requirements.csv"]
    judgements = ids["judgements/judgements.csv"]
    links = ids["links/links.csv"]
    limits = ids["registers/limits_log.csv"]
    known = set().union(sources, issues, mechs, ints, actors, cases, set(items), judgements, links, themes)

    def refs(rel, col, valid, label, multi=True):
        for r in tables[rel][1]:
            vals = split_list(r.get(col)) if multi else ([r[col]] if r.get(col) else [])
            for v in vals:
                if v not in valid:
                    rep.error(f"{rel}: {r.get(ID_COLUMNS.get(rel, 'lesson_id'))} refers to unknown {label} {v} in {col}")

    refs("registers/source_requirements.csv", "themes", themes, "theme")
    refs("registers/source_requirements.csv", "matched_source_ids", sources, "source")
    refs("registers/source_requirements.csv", "approved_at", gates, "gate decision", multi=False)
    refs("registers/source_register.csv", "themes_covered", themes, "theme")
    refs("registers/source_register.csv", "requirement_id", reqs, "requirement", multi=False)
    refs("registers/source_register.csv", "version_of", sources, "source", multi=False)
    refs("registers/limits_log.csv", "gate_id", gates, "gate decision", multi=False)
    refs("taxonomy/reform_issues.csv", "themes", themes, "theme")
    refs("taxonomy/reform_issues.csv", "mechanism_ids", mechs, "mechanism")
    refs("taxonomy/reform_issues.csv", "example_item_ids", set(items), "item")
    refs("taxonomy/reform_issues.csv", "merged_into", issues, "issue", multi=False)
    refs("taxonomy/unmatched_queue.csv", "item_id", set(items), "item", multi=False)
    refs("taxonomy/unmatched_queue.csv", "similar_issue_ids", issues, "issue")
    refs("taxonomy/ambiguous_queue.csv", "item_id", set(items), "item", multi=False)
    refs("taxonomy/ambiguous_queue.csv", "candidate_issue_ids", issues, "issue")
    refs("entities/interventions.csv", "responsible_actor_ids", actors, "actor")
    refs("entities/interventions.csv", "first_item_id", set(items), "item", multi=False)
    refs("entities/actors.csv", "parent_actor_id", actors, "actor", multi=False)
    refs("entities/comparator_cases.csv", "reform_issue_id", issues, "issue", multi=False)
    refs("entities/comparator_cases.csv", "intervention_ids", ints, "intervention")
    refs("entities/comparator_cases.csv", "selected_at", gates, "gate decision", multi=False)
    refs("links/links.csv", "from_id", known, "record", multi=False)
    refs("links/links.csv", "to_id", known, "record", multi=False)
    refs("judgements/source_quality.csv", "source_id", sources, "source", multi=False)
    refs("judgements/judgements.csv", "evidence_item_ids", set(items), "item")
    refs("judgements/judgements.csv", "supersedes", judgements, "judgement", multi=False)
    for rel in tables:
        if rel.endswith("alpha_learning_log.csv"):
            refs(rel, "decided_at", gates, "gate decision", multi=False)

    for r in tables["registers/limits_log.csv"][1]:
        at = r.get("applies_to", "")
        if at and at != "all":
            kind, _, val = at.partition(":")
            target = {"requirement": reqs, "source": sources, "theme": themes}.get(kind)
            if target is not None and val not in target:
                rep.error(f"registers/limits_log.csv: {r['limit_id']} applies to unknown {kind} {val}")
    for r in tables["judgements/judgements.csv"][1]:
        ot, oid = r.get("object_type"), r.get("object_id", "")
        if ot == "item" and oid not in items:
            rep.error(f"judgements.csv: {r['judgement_id']} object {oid} is not a known item")
        elif ot == "intervention" and oid not in ints:
            rep.error(f"judgements.csv: {r['judgement_id']} object {oid} is not a known intervention")
        elif ot == "link" and oid not in links:
            rep.error(f"judgements.csv: {r['judgement_id']} object {oid} is not a known link")
        elif ot == "issue_comparator" and oid not in cases:
            rep.error(f"judgements.csv: {r['judgement_id']} object {oid} is not a known comparator case")
        elif ot == "issue_country" and oid.split("@")[0] not in issues:
            rep.error(f"judgements.csv: {r['judgement_id']} object {oid} names an unknown issue")
    for iid, it in items.items():
        for code in it.get("themes", []):
            if code not in themes:
                rep.error(f"{iid}: unknown theme code {code}")
        p2 = it.get("pass2", {})
        for v in p2.get("reform_issue_ids", []):
            if v not in issues:
                rep.error(f"{iid}: unknown reform issue {v}")
        for v in p2.get("mechanism_ids", []):
            if v not in mechs:
                rep.error(f"{iid}: unknown mechanism {v}")
        for v in p2.get("intervention_ids", []):
            if v not in ints:
                rep.error(f"{iid}: unknown intervention {v}")
        for actor in [it.get("speaker") or {}] + list(it.get("subjects", [])):
            if actor.get("actor_id") and actor["actor_id"] not in actors:
                rep.error(f"{iid}: unknown actor {actor['actor_id']}")
        if "exception" in it.get("scope_basis", []) and not re.search(r"LIM-\d{4}", it.get("extraction_note") or ""):
            rep.error(f"{iid}: scope_basis 'exception' needs the limit ID in extraction_note")
        cited = set(re.findall(r"LIM-\d{4}", it.get("extraction_note") or ""))
        for lim in cited - limits:
            rep.error(f"{iid}: extraction_note cites unknown limit {lim}")


def check_protected_judgements(root, rep):
    """Warn if value, reason or review status of a validated or overridden judgement changed since the last commit."""
    for rel, key in (("judgements/judgements.csv", "judgement_id"), ("judgements/source_quality.csv", "sq_id")):
        try:
            old = subprocess.run(["git", "-C", str(root), "show", f"HEAD:{rel}"], capture_output=True, text=True, check=True).stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            rep.warn(f"{rel}: no committed version to compare with; protection check skipped")
            continue
        old_rows = {r[key]: r for r in csv.DictReader(io.StringIO(old)) if r.get(key)}
        _, new_rows = read_csv(Path(root) / rel)
        new_by_id = {r[key]: r for r in new_rows}
        value_col = "value" if key == "judgement_id" else "overall"
        for jid, o in old_rows.items():
            if o.get("review_status") not in ("validated", "overridden"):
                continue
            n = new_by_id.get(jid)
            if n is None:
                rep.error(f"{rel}: protected row {jid} has been deleted")
                continue
            for col in (value_col, "reason", "review_status"):
                if o.get(col) != n.get(col):
                    rep.warn(f"{rel}: {jid} is {o['review_status']} but its {col} has changed; restore it and propose a new row instead")


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Check evidence files against the JSON schema, CSV headers against the data dictionary, that IDs are unique and that "
                    "every ID referred to exists (including theme codes), and warn if a validated or overridden judgement has changed "
                    "since the last commit. Exits with status 1 if any error is found.")
    p.add_argument("--root", help="project root (default: the folder above tools/)")
    p.add_argument("--version", action="version", version=__version__)
    a = p.parse_args(argv)
    root = project_root(a.root)
    run_ids = sorted(d.name for d in (root / "runs").iterdir() if d.is_dir()) if (root / "runs").exists() else []
    rep = Report()
    tables = load_tables(root, run_ids)
    check_headers(root, tables, rep)
    ids = check_ids_unique(tables, rep)
    check_enums(tables, rep)
    items, files = check_evidence(root, root / "schemas" / "evidence_item.schema.json", rep)
    check_references(tables, ids, items, files, rep)
    check_protected_judgements(root, rep)
    print(f"validate_data {__version__}: {len(files)} evidence file(s), {len(items)} item(s), {sum(len(t[1]) for t in tables.values())} CSV row(s)")
    for w in rep.warnings:
        print(f"warning: {w}")
    for e in rep.errors:
        print(f"error: {e}")
    print(f"{len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
