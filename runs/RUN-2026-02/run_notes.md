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
