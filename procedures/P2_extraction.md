# Procedure P2: Extraction and taxonomy (stages 5 to 8)

Read this file and `rules/extraction_rules.md` before starting any of stages 5 to 8. Gates G3 and G4 sit in this procedure.

## Stage 5: Sample extraction

**Goal:** test the extraction rules on a small, varied sample before committing to the full evidence base.

1. Propose a sample of about 10 to 12 approved sources, all on Chapter 5:
   - EU: three Commission annual reports (one from around 2015, one from around 2020, the latest) and one other EU document (benchmarks, Council conclusions or screening report);
   - GOV: one law or strategy and one implementation report, at least one of them in Serbian;
   - IO: one SIGMA monitoring report and one other IO assessment if available;
   - RES: one source;
   - CSO: one source;
   - at least one difficult format (scanned PDF, very long document or webpage), which may overlap with the above.
2. The analyst confirms the sample.
3. **Hand-coding first.** Prepare `review/RUN-2026-01/G3_handcoding.xlsx` containing three short passages chosen with the analyst (for example the Chapter 5 section of one Commission report, one page of a SIGMA report, one page of a government report) with empty item rows. Wait until the analyst has filled it in before showing any agent output for those passages.
4. Extract the sample following the extraction rules. Set the evidence file `extraction.status` to `sample`.
5. Run quote verification and fix or remove every failure.

## Stage 6: Extraction review (gate G3)

1. Export `review/RUN-2026-01/G3_sample_review.xlsx` with:
   - every sample item, one row each, with empty columns for the reviewer's verdict (`correct`, `wrong_type`, `unsupported_interpretation`, `wrong_reference`, `wrong_date_or_actor`, `should_not_extract`) and comment;
   - a sheet for items the reviewer thinks were missed;
   - a comparison of the hand-coded passages with the agent's items (matched, missed by the agent, extra in the agent's output, type disagreements);
   - quote verification results.
2. The analyst reviews against this checklist:
   - findings separated from recommendations;
   - actions separated from outcomes;
   - stated status recorded without interpretation;
   - the three dates kept apart, with no inferred event dates;
   - speaker and subject actors right;
   - barriers and lessons captured where the source states them;
   - exact references correct;
   - no interpretation beyond the text;
   - all pass 1 fields filled in.
3. Summarise the results: type accuracy, number of missed items, reference errors, and the main error patterns.
4. Propose specific changes to the extraction rules, each with the error it fixes and an example. The analyst approves or edits them, and the rules become version 0.2.
5. Re-run the sample with the new rules and recheck only the areas that changed.
6. If the sample still fails after two refinement loops, stop and present the problem to the analyst rather than patching further.

**G3 decision (analyst):** the rules are good enough for full extraction. Suggested threshold: no unresolved reference errors, type accuracy of roughly nine in ten, and no systematic misses. The analyst makes the final call. Record the rules version approved.

## Stage 7: EU extraction and taxonomy (gate G4)

1. Extract all approved EU-family sources with the approved rules and verify quotes. EU sources already extracted in the sample are re-extracted with the approved rules, and their evidence files are replaced (their status changes from `sample` to `complete`).
2. Draft the reform-issue taxonomy in `taxonomy/reform_issues.csv` from the EU requirement items (findings and recommendations):
   - group items that describe the same underlying problem;
   - give each issue a label, a definition, the cluster and chapter, two or three example items and exclusion notes;
   - apply the granularity test: specific enough that one EU requirement maps clearly to it, general enough that another country could plausibly have the same issue;
   - use the `PP` area code and country-neutral wording;
   - set every new issue to `draft`.
3. Review the draft mechanism list in `taxonomy/mechanisms.csv` against the EU items and propose changes.
4. Export `review/RUN-2026-01/G4_taxonomy.xlsx`: issues with definitions and item counts, items that fit no issue, the mechanism list, and a sample of items under each issue.

**G4 decision (analyst):** edit, merge, split and approve the issues and mechanisms. Set approved rows to `approved` and record the taxonomy version (1.0).

## Stage 8: Full extraction

1. Extract all remaining approved sources with the approved rules, including the non-EU sample sources, which are re-extracted in the same way.
2. Verify quotes for every source.
3. Prepare a spot-check sheet for G5: a random 5 per cent of items plus every flagged item.
