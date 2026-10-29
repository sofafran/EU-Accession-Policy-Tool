# Procedure P1: Run setup and sources (stages 0 to 4)

Read this file before starting any of stages 0 to 4. Gates G0, G1 and G2 sit in this procedure. Do not start a stage until the gate before it has a `pass` or `pass_with_conditions` entry in `registers/gate_log.csv`.

## Around every gate (applies to procedures P1 to P5)

**When a gate package is prepared:**

1. Run `tools/validate_data.py`.
2. Review `runs/<run_id>/run_notes.md` since the last gate and propose rows for `runs/<run_id>/alpha_learning_log.csv` for any material lesson, with status `open`. Add the proposed rows to the gate package.
3. Rebuild the review page with `tools/build_review_page.py`. The material in the package appears on the page as `Pending review`; agent proposals as `Proposed`; unfinished work as `Draft`.

**After the gate decision is recorded in the gate log:**

1. Update the statuses of the alpha learning log rows the reviewer decided on, with the gate decision ID in `decided_at`.
2. Rebuild the review page. Material the gate passed becomes `Validated`; overridden judgements show the reviewer's value.
3. Offer to commit the project, with the gate decision in the commit message.

The review page is never the place where a decision is made. If George's feedback on the page leads to a change, it goes through the analyst and the normal gate route.

## Stage 0: Run setup (gate G0)

**Goal:** fix what this run covers before any work starts.

1. Read `runs/RUN-2026-01/run_record.md`, including its run-specific settings.
2. Check that the helper tools listed in `tools/README.md` exist and work. If they do not exist yet, build them first, test each on a small sample file, and record their versions in the run record.
3. Check that all CSV templates exist with the headers defined in `schemas/data_dictionary.md`.
4. Ask the analyst to set the evidence freeze date. Until it is set, the run record shows `TBC` and G0 cannot pass.
5. Check that `index.html` and the alpha learning log exist, and build and test `tools/build_review_page.py` with the other tools.
6. Present the G0 package: the completed run record, the active entries in the limits log, the versions of the codebooks and rules, and the proposed alpha learning log rows.

**G0 decision (analyst):** approve the scope, freeze date, reviewers and versions. Record it in the gate log.

## Stage 1: Source requirements list (gate G1)

**Goal:** list every type of document the analysis expects to exist, before searching.

1. Draft `registers/source_requirements.csv` from Codebook 2, for the target country, chapters, themes and time window set in the run record.
2. Cover all five families. For each line, state the issuing institution, years, chapters or theme codes, core or supporting, and search hints (official website and likely title, including the original-language title if relevant).
3. Group repeating documents into one line (for example one line for all Commission annual reports in the time window).
4. Start from the source requirement hints in the run record. Typical lines include:
   - EU: Commission annual reports on the target country; screening reports for the in-scope chapters if public; opening, interim or closing benchmarks where negotiations have reached that point; Council conclusions and EU common positions where public; Reform Agenda and Growth Plan documents that cover the scope. For a cross-cutting theme, the whole annual report is a source, not only the in-scope chapter sections.
   - GOV: the laws, strategies, action plans and implementation reports that govern the in-scope chapters and theme areas; annual reports of the responsible institutions; audit reports; the national programme for adopting the acquis.
   - IO: monitoring reports and assessments by international organisations with a mandate for the chapters or theme areas.
   - RES: evaluations and academic or think tank analyses of reform in the target country in the scope.
   - CSO: monitoring reports by watchdogs and civil society coalitions working in the scope.
5. These are hints, not facts. Mark a line `not_public` or `not_found` only after searching.

**G1 decision (analyst):** add, remove or edit lines. Record the decision ID in `approved_at` for each line.

## Stage 2: Acquisition

**Goal:** bring every available document into the project in a usable form.

For each requirement line:

1. Search for the document, preferring the issuing institution's own website over copies hosted elsewhere.
2. Download the original to a temporary location and compute its SHA-256 fingerprint.
3. Compare the fingerprint with `content_hash` in the register:
   - same fingerprint as an existing source: register it as `duplicate` of that source (tier 1) and do not file it again;
   - same document title and institution but a different fingerprint: treat it as a possible new version and flag it for G2.
4. Assign the next source ID (`<country code>-<family>-<publication year>-<sequence>`) and file the original as `sources/<country code>/<family>/originals/<source_id>_<short-label>.<ext>`. The short label uses hyphens, no spaces, for example `CCC-EU-2025-001_EC_Country-Report-2025.pdf`, where `CCC` is the country code. The run record gives the code and an example for the run.
5. Convert it to text at `sources/<country code>/<family>/text/<source_id>.txt`, with a marker line `=== PAGE n ===` before each page. For webpages, save the HTML snapshot as the original and the readable text as the text file, with section headings kept.
6. If the text is unreadable or the PDF is scanned, run text recognition in the languages listed in the run record and note `ocr` in the register notes.
7. Record the language of the document. If it is not English, note in the register why no suitable English version was used. Then add a register row with all fields, `status` `available` and `added_in_run` `RUN-2026-01`.

When a document cannot be obtained:

- add a register row with `status` `inaccessible`, the URL tried, and the reason (for example "not published", "broken link", "behind login");
- never get around a paywall or login;
- update the requirement line status.

Manual drop-in: documents the analyst adds to `sources/_inbox/` are registered in the same way. Ask the analyst for the URL and requirement if they are not obvious, and move the file out of the inbox once it is registered.

Clear-cut exclusions (outside the time window, outside the country scope, outside the in-scope chapters and themes) are tier 2: the agent records them with the reason and they are listed for review at G2.

## Stage 3: Register and organise

1. Check the register for completeness and for possible versions (step 3 above).
2. Propose source quality ratings for each in-scope chapter or theme the source covers in `judgements/source_quality.csv`, following the judgement rules (tier 2).
3. Update the status of every requirement line.
4. Export the G2 package to `review/RUN-2026-01/G2_source_review.xlsx` with these sheets:
   - the source register;
   - requirements with their status, with gaps first;
   - exclusions and inaccessible documents;
   - source quality ratings, with Low ratings, specialist sources and uncertain ratings first;
   - a short coverage note: counts by family, year, chapter and theme, the number of sources not in English, and the main gaps.

## Stage 4: Source review (gate G2)

**G2 decision (analyst):** confirm the source set. The analyst may add documents (through the inbox), remove documents, confirm exclusions, override quality ratings and add limits. The agent then:

- updates the register, the quality ratings (`overridden`, with the reason in `override_reason`) and the limits log;
- records the gate decision, including any conditions.

No parsing may start before G2 passes.
