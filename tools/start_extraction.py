#!/usr/bin/env python3
"""Start a run's own extraction of a source already extracted by an earlier run (evidence schema 1.3, decision E21).

Moves the file's current `extraction` and `classification` records, unchanged, into `earlier_extractions` with the
earlier run, its target country, the source's role in it and the item IDs it created, then writes a new `extraction`
record for this run. No item is changed or removed. New items continue the numbering; a passage the earlier run already quoted gets a new item of
this run, so each item, and its classification, belongs to one run only. Tier 1: logged in run_notes.
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import extraction_runs, project_root, read_json, run_country, run_record  # noqa: E402

__version__ = "1.0.0"


def start(root, path, run, role, today):
    data = read_json(path)
    cur = data["extraction"]
    if cur.get("run_id") == run:
        raise SystemExit(f"{path.name}: already holds {run}'s extraction")
    if any(e["run_id"] == run for e in data.get("earlier_extractions", [])):
        raise SystemExit(f"{path.name}: {run} is already among the earlier extractions")
    latest = extraction_runs(data)[-1]
    prev_run = cur["run_id"]
    item_roles = {it["role"] for it in data["items"] if it["item_id"] in latest["item_ids"]}
    earlier = {"run_id": prev_run, "run_country": cur.get("run_country") or run_country(root, prev_run),
               "role": cur.get("role") or (item_roles.pop() if len(item_roles) == 1 else "target"),
               "item_ids": sorted(latest["item_ids"]), "moved_on": today,
               "extraction": cur, "classification": data["classification"]}
    rec, _ = run_record(root, run)
    data["earlier_extractions"] = data.get("earlier_extractions", []) + [earlier]
    data["extraction"] = {"run_id": run, "rules_version": rec.get("Extraction rules version", ""), "extracted_at": today,
                          "status": "partial", "codebook_version": rec.get("Codebooks version", "").split(" ")[0],
                          "themes_version": rec.get("Theme list version", ""), "run_country": run_country(root, run), "role": role}
    data["classification"] = {"status": "not_started", "run_id": run}
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return earlier


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("source_ids", nargs="+")
    p.add_argument("--run", required=True)
    p.add_argument("--role", default="target", choices=["target", "comparator"])
    p.add_argument("--root")
    p.add_argument("--date")
    p.add_argument("--version", action="version", version=__version__)
    a = p.parse_args(argv)
    root = project_root(a.root)
    for sid in a.source_ids:
        path = root / "evidence" / sid.split("-")[0] / f"{sid}.json"
        e = start(root, path, a.run, a.role, a.date or dt.date.today().isoformat())
        print(f"{sid}: {e['run_id']} ({e['run_country']}, {e['role']}, {len(e['item_ids'])} items) kept in earlier_extractions; {a.run} extraction started")


if __name__ == "__main__":
    main()
