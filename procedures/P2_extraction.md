# Procedure P2: Extraction and taxonomy (stages 5 to 8)

Read this file and `rules/extraction_rules.md` before starting any of stages 5 to 8. Gates G3 and G4 sit in this procedure. Follow "Around every gate" in procedure P1 for the learning log and the review page.

## Stage 5: Sample extraction

**Goal:** test the extraction rules on a small, varied sample before committing to the full evidence base.

1. Propose a sample of about 10 to 12 approved sources, all within the run scope, covering both the in-scope chapters and the cross-cutting themes where the run has both:
   - EU: three Commission annual reports (one from early in the time window, one from the middle, the latest) and one other EU document (benchmarks, Council conclusions, screening report or Reform Agenda document);
   - GOV: one law or strategy and one implementation report, at least one of them not in English if such sources are approved;
   - IO: two IO monitoring reports or assessments if available;
   - RES: one source;
   - CSO: one source;
   - at least one difficult format (scanned PDF, very long document or webpage), which may overlap with the above.
2. The analyst confirms the sample.
3. **Hand-coding first.** Prepare `review/<run_id>/G3_handcoding.xlsx` containing three short passages chosen with the analyst (for example an in-scope chapter section of one Commission report, one section of the same or another report that contains theme recommendations, and one page of a government report) with empty item rows. Wait until the analyst has filled it in before showing any agent output for those passages.
4. Extract the sample following the extraction rules, screening the whole text of a long source and listing its pages before extraction (extraction rules, PC-24). Set the evidence file `extraction.status` to `sample`.
5. Run quote verification and fix or remove every failure.
6. Run the second-pass check on each sample source (extraction rules, section 8), and report its yield by source family in the G3 package.

## Stage 6: Extraction review (gate G3)

1. Export `review/<run_id>/G3_sample_review.xlsx` with:
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
   - scope basis and theme tags correct, with incidental references to technology left out and doubtful cases flagged;
   - all pass 1 fields filled in.
3. Summarise the results: type accuracy, number of missed items, reference errors, and the main error patterns.
4. Propose specific changes to the extraction rules, each with the error it fixes and an example. The analyst approves or edits them, and the rules become version 0.2.
5. Re-run the sample with the new rules and recheck only the areas that changed.
6. If the sample still fails after two refinement loops, stop and present the problem to the analyst rather than patching further.

**G3 decision (analyst):** the rules are good enough for full extraction. Suggested threshold: no unresolved reference errors, type accuracy of roughly nine in ten, and no systematic misses. The analyst makes the final call. Record the rules version approved.

## Stage 7: EU extraction and taxonomy (gate G4)

1. Extract all approved EU-family sources with the approved rules and verify quotes. EU sources already extracted in the sample are re-extracted with the approved rules, and their evidence files are replaced (their status changes from `sample` to `complete`).
2. **Runs after the alpha:** the taxonomy is shared and already approved. Classify the EU requirement items against the existing issues first, using the definitions and exclusion notes. Draft a new issue only for requirement items that genuinely fit none, following the steps below, and propose it at G4 as an addition to the shared taxonomy. Never redefine an existing issue to fit the new country; propose a change to it at G4 instead, with the effect on earlier runs stated.
3. Draft the reform-issue taxonomy in `taxonomy/reform_issues.csv` from the EU requirement items (findings and recommendations), or, in later runs, only the new issues:
   - group items that describe the same underlying problem;
   - give each issue a label, a definition, the cluster and chapter, two or three example items and exclusion notes;
   - apply the granularity test: specific enough that one EU requirement maps clearly to it, general enough that another country could plausibly have the same issue;
   - use the area codes proposed in the run record and country-neutral wording;
   - record the chapters and theme codes of each issue; an issue from a cross-cutting theme must be supported by at least one in-scope recommendation that meets the materiality test;
   - set every new issue to `draft`.
4. If more than one agent drafted the taxonomy, list items mapped to issues in more than one draft and resolve each overlap (classification rules, PC-07).
5. **Runs after the alpha:** for every shared issue the run uses, list the elements of its definition that the new country's evidence does not show, with the items checked (classification rules, section 9, PC-25). Shared taxonomy changes are additive; a change to an issue that a closed run cites is proposed separately, with its effect on that run stated.
6. Review the draft mechanism list in `taxonomy/mechanisms.csv` against the EU items and propose changes.
7. Export `review/<run_id>/G4_taxonomy.xlsx`: issues with definitions and item counts, items that fit no issue, the mechanism list, a sample of items under each issue, every item flagged `theme_doubtful`, and the list of definition elements from step 5.

**G4 decision (analyst):** edit, merge, split and approve the issues and mechanisms. Set approved rows to `approved` and record the taxonomy version (1.0 in the alpha; the next minor version when a later run adds or changes issues).

## Stage 8: Full extraction

1. Extract all remaining approved sources with the approved rules, including the non-EU sample sources, which are re-extracted in the same way. Screen the whole text of each long source and list its pages before extraction (extraction rules, PC-24), and screen horizontal EU documents for horizontal passages as well as passages on the target country (PC-26).
2. Verify quotes for every source, and run the second-pass check, reporting its yield by source family; resample any family whose yield is well below the others (PC-05).
3. Prepare a spot-check sheet for G5: a random 5 per cent of items plus every flagged item.
