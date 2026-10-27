# Procedure P1: Run setup and sources (stages 0 to 4)

Read this file before starting any of stages 0 to 4. Gates G0, G1 and G2 sit in this procedure. Do not start a stage until the gate before it has a `pass` or `pass_with_conditions` entry in `registers/gate_log.csv`.

## Stage 0: Run setup (gate G0)

**Goal:** fix what this run covers before any work starts.

1. Read `runs/RUN-2026-01/run_record.md`.
2. Check that the helper tools listed in `tools/README.md` exist and work. If they do not exist yet, build them first, test each on a small sample file, and record their versions in the run record.
3. Check that all CSV templates exist with the headers defined in `schemas/data_dictionary.md`.
4. Ask the analyst to set the evidence freeze date. Until it is set, the run record shows `TBC` and G0 cannot pass.
5. Present the G0 package: the completed run record, the active entries in the limits log, and the versions of the codebooks and rules.

**G0 decision (analyst):** approve the scope, freeze date, reviewers and versions. Record it in the gate log.

## Stage 1: Source requirements list (gate G1)

**Goal:** list every type of document the analysis expects to exist, before searching.

1. Draft `registers/source_requirements.csv` from Codebook 2, for Serbia, Chapter 5, from 2014 to the freeze date.
2. Cover all five families. For each line, state the issuing institution, years, core or supporting, and search hints (official website and likely title, including the Serbian title if relevant).
3. Group repeating documents into one line (for example one line for all Commission annual reports from 2014 onward).
4. Typical lines for Chapter 5 include:
   - EU: Commission annual reports on Serbia; screening report for Chapter 5 if public; opening, interim or closing benchmarks; Council conclusions and EU common positions where public; Reform Agenda and Growth Plan documents that mention public procurement.
   - GOV: the public procurement law and its amendments; the law on public-private partnerships and concessions; public procurement development strategies or programmes and their action plans; annual reports of the national public procurement authority; annual reports of the body that reviews procurement complaints; State Audit Institution reports on procurement; the National Programme for the Adoption of the Acquis.
   - IO: SIGMA monitoring reports; World Bank, EBRD or OECD procurement assessments where they exist.
   - RES: evaluations and academic or think tank analyses of Serbian procurement reform.
   - CSO: monitoring reports by procurement or anti-corruption watchdogs.
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
4. Assign the next source ID (`SRB-<family>-<publication year>-<sequence>`) and file the original as `sources/SRB/<family>/originals/<source_id>_<short-label>.<ext>`. The short label uses hyphens, no spaces, for example `SRB-EU-2025-001_EC_Serbia-Report-2025.pdf`.
5. Convert it to text at `sources/SRB/<family>/text/<source_id>.txt`, with a marker line `=== PAGE n ===` before each page. For webpages, save the HTML snapshot as the original and the readable text as the text file, with section headings kept.
6. If the text is unreadable or the PDF is scanned, run text recognition and note `ocr` in the register notes.
7. Add a register row with all fields, `status` `available` and `added_in_run` `RUN-2026-01`.

When a document cannot be obtained:

- add a register row with `status` `inaccessible`, the URL tried, and the reason (for example "not published", "broken link", "behind login");
- never get around a paywall or login;
- update the requirement line status.

Manual drop-in: documents the analyst adds to `sources/_inbox/` are registered in the same way. Ask the analyst for the URL and requirement if they are not obvious, and move the file out of the inbox once it is registered.

Clear-cut exclusions (outside the time window, outside the country scope) are tier 2: the agent records them with the reason and they are listed for review at G2.

## Stage 3: Register and organise

1. Check the register for completeness and for possible versions (step 3 above).
2. Propose source quality ratings for Chapter 5 in `judgements/source_quality.csv`, following the judgement rules (tier 2).
3. Update the status of every requirement line.
4. Export the G2 package to `review/RUN-2026-01/G2_source_review.xlsx` with these sheets:
   - the source register;
   - requirements with their status, with gaps first;
   - exclusions and inaccessible documents;
   - source quality ratings, with Low ratings, specialist sources and uncertain ratings first;
   - a short coverage note: counts by family and year, and the main gaps.

## Stage 4: Source review (gate G2)

**G2 decision (analyst):** confirm the source set. The analyst may add documents (through the inbox), remove documents, confirm exclusions, override quality ratings and add limits. The agent then:

- updates the register, the quality ratings (`overridden`, with the reason in `override_reason`) and the limits log;
- records the gate decision, including any conditions.

No parsing may start before G2 passes.
