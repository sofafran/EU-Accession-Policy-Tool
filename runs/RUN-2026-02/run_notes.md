# Run notes: <run_id>

The raw working diary for the run, kept by the agent. The threshold is low: note any problem with the method, recurring error, technical difficulty or idea as soon as it appears. Each note has a date, the stage, and an example (evidence item or source ID).

Notes are not curated and are not shown on the review page. When a note proves material, especially for scaling, the agent proposes a row in `learning_log.csv` that cites the note's date rather than copying it.

## 2026-11-03, stage 0

- Adding the RUN-2026-02 folder made 3 tool tests fail (export_review G0 to G2). The tests copy the project and used the default run, which is the latest run with a record, so they assumed RUN-2026-01 was always active. Fixed by passing `--run RUN-2026-01` in the export and page tests. No tool logic changed for this. Example: `tools/tests/test_tools.py` line 395.
- With two runs, the review page builder still printed alpha wording ("alpha review", "Purpose of the alpha", "Alpha lessons") for any run, and the North Macedonia country page linked "Review page" to `index.html`, which now shows Moldova. Fixed in `build_review_page.py` 1.5.0: labels follow the run, country pages link to their own run's review page (`review_RUN-2026-01.html` for the alpha), and the active review page links to earlier runs' pages. Alpha content unchanged (only date and version stamps changed on its pages).
- Romanian text-recognition data (`ron`) was missing; installed at stage 0. Only `eng`, `mkd` and `sqi` were present, from the alpha. Each later run needs this check (Cyrillic Serbian, Ukrainian, Georgian, Turkish).
- 11 Moldova evidence files from the alpha comparator step cannot take a second extraction record (one extraction per file). Raised as G0-D02; extraction must not start until it is decided.
- 11 Moldova rows already sit in `taxonomy/unmatched_queue.csv` from the comparator step, raised against North Macedonia issues. They are re-examined at this run's G4, not carried over as decided.
- Run IDs: the shared core says "RUN-2026-02" for PC-11 and for the held-sources point; written when Montenegro was planned as RUN-2026-02. With IDs assigned in start order they now apply to Moldova, which is correct in substance (both concern the next run), but a reader of the E19 text could read them as Montenegro. The rollout plan now says so explicitly.
- No territorial-coverage rule exists in the method. Moldova needs one for the Transnistrian region (G0-D03); Georgia, Ukraine, Kosovo and Cyprus-related Türkiye material will need the same. Proposed as a run deviation, not a method change.

## 2026-11-03, G0 and stage 1

- G0 passed (GATE-0014). Building E21 showed that "adopting" an earlier run's item would not work: classification is held on the item (`pass2`), so a Moldova reclassification would overwrite the alpha's. Settled by keeping each item in one run only; a later run quotes the passage again as its own item. Exact-duplicate checks must therefore compare items within a run, not across runs in one file.
- `build_review_page.py` and the G3 export now count only the run's own extraction records and items, so Moldova's page will not show North Macedonia comparator items as Moldova extraction.
- Two more tests assumed one run (next lesson ID read only the alpha log). Fixed; 95 of 95 pass.

## 2026-11-03, stage 2 and 3

- Acquisition by two agents (EU; GOV, IO, RES and CSO), merged by the lead agent: 62 new register rows. Restricted Council documents: the EU agent downloaded the two EU common positions (MDA-EU-2026-001, -002) before seeing the LIMITE marking. The repository is public, so both originals and text files are listed in `.gitignore`, never pushed, registered `excluded` and not used (LIM-0045). Lesson: acquire.py should refuse, or at least warn on, a LIMITE marking before filing.
- Horizontal EU documents (enlargement communications 2023 to 2025, Council conclusions December 2023 and 2024) were byte-identical to sources registered under North Macedonia (MKD-EU-...). They are matched to REQ-076 and REQ-082 by their MKD IDs, not registered again. Their `country` reads MKD although they cover all candidates: a scaling issue for the shared register (scaling note S8).
- legis.md blocks automated access, so no consolidated law text is held (LIM-0046). Chapter 2 depends on these laws; manual retrieval requested from Sofia.
- near_duplicates: MDA-EU-2026-003 and MDA-EU-2026-005 are the second and third release decisions under the Reform and Growth Facility, built on one template; they are different decisions, not versions (tier 1).
- Acquisition log: a failed attempt for Law 200/2010 is logged under MDA-GOV-2026-002, an ID now used by another source. The log is a history of attempts; the register is authoritative.
- MDA-GOV-2026-013 is an ARCOM home page saved by mistake during an access test; registered `excluded`.
- SIGMA Monitoring Report 2023 (MDA-IO-2023-001) is a gov.md copy, because sigmaweb.org blocks automated access; to be checked at G2 as a faithful copy.

## 2026-11-03, stage 5

- Sofia asked (3 Nov) to complete all work that does not depend on the 2026 report. The G2 condition (1), drafted by the agent, said the 2026 report would be registered before the G3 sample was drawn. On this instruction the sample is drawn now from the held 2023 to 2025 reports; the 2026 report is extracted with the approved rules at stage 7, like any other EU source, and checked by the second pass. This does not weaken the rule test, which needs varied sources, not the latest one.
- Missing laws recorded as an evidence gap (LIM-0047, replacing LIM-0046), not retrieved by hand.
- start_extraction.py used for the first time on real data: MDA-EU-2024-001 (11 alpha items) and MDA-EU-2025-001 (12 alpha items) moved to earlier_extractions; validation passes.

## 2026-11-03, stage 7

- Single-run assumptions found in the output and package tools. The output loader (`build_outputs.load`, also used by the country page) counted every evidence item and every register row with role `target` in the project, so the North Macedonia page would have shown 6,024 items and 174 sources instead of 4,988 and 112, and its coverage report would have listed Moldova's requirement lines. The G1 and G2 spreadsheets for Moldova likewise held every country's rows (the gate log summaries were computed correctly by hand). Fixed with run-scoped helpers in `tools/common.py` (`run_sources`, `register_role`, `run_requirements`); `build_outputs.py` 1.2.0, `export_review.py` 1.14.0, `build_review_page.py` 1.6.0. Checked: the North Macedonia review and country pages rebuild identical to the committed versions (apart from dates); its outputs rebuild with identical requirement and source sections; the only differences are the alpha's own limit changes at G8, which predate this run. G1 and G2 packages for Moldova rebuilt (75 sources, 34 lines, 53 ratings).
- Stage 7 extraction (rules 0.5): 103 items from the Opinion, Analytical Report and Association Implementation Reports; 99 items from the Growth Plan, release decisions and annexes, ERP assessments, the news item and six horizontal documents held as North Macedonia evidence (14 Moldova items in three of them; the earlier 54 items checked unchanged). The quality check's view that the release-decision annexes were out of scope was wrong for MDA-EU-2026-004 and -006 (62 items on in-scope Reform Agenda steps); they already had TECH ratings (SQ-00230, SQ-00231), and ratings SQ-00270 to SQ-00272 were added for MDA-EU-2025-004, -2025-005 and -2026-007. Second pass on the stage 7 sources (checker-EU7): 5 misses against 202 items.
- MDA-EU-2023-002-0001 and -0002 sit under Chapter 24 but concern admission of foreign workers, tagged chapter 02; -0024 (outward mobility of Moldovan workers) is under the Chapter 2 heading but outside the boundary unless directly linked: for pass 2.
