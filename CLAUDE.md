# CLAUDE.md: EU Accession Reform Intelligence Tool

You are working on an AI-enabled analytical tool that turns EU accession assessments into reform priorities and practical policy options. Your role is to extract, organise and propose. The analyst decides. The method is set out in seven codebooks; this file tells you how to work within it.

## Start of every session

1. Read the active run record in `runs/` (currently `runs/RUN-2026-01/run_record.md`) and the last entries in `registers/gate_log.csv`.
2. Read `current_stage` in the run record to see which stage the run is at, and check it against the last gate decision. Update `current_stage` every time you start a new stage.
3. Read the procedure for that stage in `procedures/` before doing anything, and the rules file it names.
4. Tell the analyst in one or two sentences where the run stands and what you propose to do next.

| Stages | Procedure | Rules | Gates |
|---|---|---|---|
| 0 to 4: setup and sources | `procedures/P1_setup_and_sources.md` | Codebook 2 | G0, G1, G2 |
| 5 to 8: extraction and taxonomy | `procedures/P2_extraction.md` | `rules/extraction_rules.md` | G3, G4 |
| 9 to 11: classification and assessment | `procedures/P3_classification_and_assessment.md` | `rules/classification_rules.md`, `rules/judgement_rules.md` | G5, G6 |
| Run 1b comparator pilot | `procedures/P4_comparator_pilot.md` | all rules | G1b, G2b, G5b, G6b |
| 12 to 14: outputs, close, next run | `procedures/P5_outputs_and_close.md` | Codebook 7 | G7, G8 |

## Current scope (RUN-2026-01)

- Serbia only, Chapter 5 (Public procurement), from 2014 to the evidence freeze date in the run record.
- Comparator evidence only in run 1b, only for the issues chosen at G6.
- English primary; Serbian only for core documents with no English version.
- Active limits are in `registers/limits_log.csv`. Never work outside them. If something useful falls outside the scope, record it in the limits log and tell the analyst.

## Rules you must never break

1. **Never cross a gate on your own.** A stage may only start when the gate before it has a `pass` or `pass_with_conditions` row in `registers/gate_log.csv`. You prepare the gate package; the reviewer or reviewers named in the run record for that gate decide.
2. **Never decide a tier 3 matter.** You only propose: source requirements, judgement-based exclusions, taxonomy changes, ambiguous classifications, comparator choices, direction of travel, unresolved gap, success, attribution, comparator relevance, transferability, priority, tractability, policy options, and any change to codebooks, rules or scope.
3. **Keep stated and assessed apart.** What a source says goes in evidence items. What you conclude goes in judgements. Adoption is never success.
4. **Quote exactly.** Every evidence item quotes the source word for word with its page or section, and passes the automatic quote check. Never paraphrase in `stated_text`.
5. **Never infer beyond the text in pass 1.** No inferred causes, lessons or dates during extraction.
6. **Never overwrite a validated or overridden judgement.** Set its `rereview_flag` and propose a new row instead.
7. **IDs are permanent.** Never change, reuse or delete an ID or a register row. Mark records excluded, superseded, merged or retired instead.
8. **Never edit an original source file.** Originals in `sources/**/originals/` are read-only.
9. **Never bypass a paywall, login or access restriction.** Record the source as inaccessible.
10. **Never start a new run or widen the scope yourself.**
11. **Never merge source quality, evidence confidence and relevance** into a single score.
12. **Never add to the taxonomy directly.** Propose through `taxonomy/unmatched_queue.csv`.

## What you may decide yourself

- **Tier 1, decide and log:** file naming and IDs, format conversion, exact-duplicate detection, recording retrieval failures, quote verification, structural tags (country, chapter, cluster from the document structure).
- **Tier 2, decide and surface for review at the next gate:** clear-cut exclusions (outside the time window or country), extraction once the rules are approved, source quality ratings, evidence confidence, relevance, and implementation status where sources agree.

Anything else is tier 3.

## Where things are

| What | Where |
|---|---|
| Method (what and why) | `codebooks/CB1` to `CB7` |
| Agreed architecture and decisions | `ARCHITECTURE.md`, `decisions/decision_log.md` |
| Step-by-step instructions | `procedures/` |
| Operational rules (versioned) | `rules/` |
| Field definitions, ID formats, JSON schema | `schemas/data_dictionary.md`, `schemas/evidence_item.schema.json` |
| Source files | `sources/<country>/<family>/originals` and `/text`; manual additions in `sources/_inbox/` |
| Registers and logs | `registers/` (requirements, source register, limits log, gate log) |
| Evidence items | `evidence/<country>/<source_id>.json` |
| Taxonomy | `taxonomy/` (reform issues, mechanisms, unmatched and ambiguous queues) |
| Entities and links | `entities/`, `links/links.csv` |
| Judgements | `judgements/` |
| Gate review spreadsheets | `review/<run_id>/` |
| Outputs | `outputs/<run_id>/` |
| Helper scripts | `tools/` (specified in `tools/README.md`) |

## Working conventions

- **Formats:** CSV for anything a person reviews or edits; one JSON file per source for evidence items. Follow `schemas/data_dictionary.md` exactly. Run `tools/validate_data.py` before preparing any gate package.
- **Review packages:** the analyst never reads raw JSON. Use `tools/export_review.py` to build a spreadsheet in `review/<run_id>/` for each gate, with the items needing a decision first.
- **Versions:** every evidence file records the extraction and classification rules, taxonomy and mechanism list versions used; every judgement records the codebook, judgement rules and taxonomy versions used. Changing a rules file means a new version number and a change log entry, after approval.
- **Version history:** commit the project to git after every gate decision, with a message such as `RUN-2026-01 G3 pass: extraction rules 0.2`.
- **Uncertainty:** when unsure, use `insufficient_evidence`, add a flag or note, or put the item in a review queue. Do not guess.
- **Conflicting evidence:** record it with `contradicts` links and report it. Do not resolve it silently.
- **Writing:** plain British English, full sentences, no em dashes. Outputs cite evidence item IDs in an annex, not in the running text.
- **Talking to the analyst:** keep updates short; say what you did, what needs a decision, and where the file is.

## If the method seems wrong

If a codebook, rule or procedure seems to produce poor results, keep following it, record the problem with examples in `runs/<run_id>/run_notes.md`, and raise it at the next gate as a proposed change. Do not change the method on your own.
