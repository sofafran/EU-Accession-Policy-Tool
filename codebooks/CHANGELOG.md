# Codebook change log

## Data dictionary 1.6 and evidence schema 1.3, 3 November 2026

Approved by Sofia at G0 of RUN-2026-02 (G0-D02, decision E21). A source can hold the extractions of several runs: the earlier run's records move unchanged to `earlier_extractions`, each traceable to its run, the run's country and the source's role, with the items it created. Items belong to one run only. The register `role` may list one role per run. No codebook or rules version changes; RUN-2026-01's records and items are unchanged. Tools: `start_extraction.py` 1.0.0 (new), `validate_data.py` 1.5.0, `build_review_page.py` 1.5.0, `export_review.py` 1.13.1.

## Version 1.3 (Codebooks 1 to 6) and 1.2 (Codebook 7), 2 November 2026

The changes PC-01 to PC-17, approved by Sofia at G8 of RUN-2026-01 (GATE-0013), applied as new shared-core versions before RUN-2026-02, together with the multi-country rollout (decision E19, `runs/rollout_plan.md`). Full wording and reasons: `runs/RUN-2026-01/run_review.md`, section 5, and `review/RUN-2026-01/G8_proposed_changes.csv`. RUN-2026-01 keeps the versions recorded in its run record and evidence files; none of its evidence, judgements or outputs changed.

- **Codebook 1:** later runs apply the method country by country; North Macedonia is the methodological baseline, not a substantive template; one shared taxonomy for comparison (E19).
- **Codebook 2:** manual retrieval route for publishers that block automated download, and a near-duplicate check at acquisition (PC-03).
- **Codebook 3:** one target country per run, following the rollout plan; a cross-cutting theme makes every annual and screening report relevant, and time and volume plans must allow for it (PC-04).
- **Codebook 4:** no change in substance; version aligned.
- **Codebook 5:** the taxonomy is shared and never stretched to fit a new country; route for problems raised only by national or independent sources (PC-12); evidence of a closed run keeps its taxonomy version.
- **Codebook 6:** transferability may attach to a comparator case, with the case's lesson labelled agent synthesis (PC-01).
- **Codebook 7:** reviewers named in the run record; agent synthesis labelled in every output; warnings alongside options (PC-02); outputs of each run, and the country and regional pages.
- **Extraction rules 0.5:** standard second-pass check by a different agent, with its yield reported by source family (PC-05).
- **Classification rules 0.4:** country statements in screening reports are country responses, and a same-sentence check before G5 (PC-06); overlap check after parallel taxonomy drafting (PC-07); route for problems not raised in EU material (PC-12); the taxonomy is shared.
- **Judgement rules 0.5:** final wording of reasons and a reason-value check (PC-08); searches behind claims of absence and no truncated inputs (PC-09); helper briefs checked against the rules (PC-10); each country judged on its own evidence.
- **Taxonomy:** stays at 1.1. PC-12 is applied through Codebook 5 and the classification rules. PC-11 (consider MEC-04 for RI-TEC-028) is carried to RUN-2026-02's G4 as a proposal, because changing the shared row now would change how a validated North Macedonia issue is shown.
- **Data dictionary 1.5:** `reform_issue_ids` on interventions (PC-13); the case fields on comparator cases, filled for the nine alpha cases by copying the text validated at G6b word for word (PC-14); the learning log is `learning_log.csv` from RUN-2026-02; country code list.
- **Procedures:** `<run_id>` in place of the alpha's run ID; country checks at stage 0; shared-taxonomy route at stage 7; the checks above before G3, G5 and G6; stage 12 method and output writing as a review step (PC-15); limits check under a standing instruction (PC-16); comparators first from countries already in the project.
- **Tools:** tests for `build_outputs.py`, a text-density check in `convert_to_text.py`, a near-duplicate check, a check that every theme issue has a recommendation, and a tested acquisition tool (PC-17). The tools now read the run's country from its run record, and the pages are split into a regional page and one page per country (E19).

## Version 1.2 (Codebooks 1 to 6) and 1.1 (Codebook 7), 29 October 2026

Pre-G0 reconfiguration of the pilot from Serbia, Chapter 5 (Public procurement) to North Macedonia, Chapter 2 plus a technology and AI theme. Run-specific settings moved to the run record, CLAUDE.md and the limits log; the codebooks were made country-neutral. Decision IDs refer to `decisions/decision_log.md`.

- **Codebook 1:** first-run scope described as one pilot country with one chapter and one cross-cutting theme, set in the run record (A5, A6); first run defined as an alpha product and methodology test (E6); country-neutral examples (F2).
- **Codebook 2:** country-neutral wording (F2); language rule covers the target country's official languages, each non-English source recorded in the register, and the machine translation cap applies unless a reviewer who reads the language is named (A8); themes added to the register fields (D6).
- **Codebook 3:** country-neutral scope (A5, F2); cross-cutting themes, materiality, full chain and the out-of-scope rule; no deferred-chapter list (A6, A9, D6); time window start set in the run record (A7); language limit generalised (A8); new exclusion category "outside current thematic scope"; learning recorded throughout the run in a working diary and a curated learning log, feeding a run review with readiness for scaling (E8).
- **Codebook 4:** country-neutral ID examples (F2); scope basis and theme tags recorded in the first pass (D6); sample requires a non-English document only where such documents are approved.
- **Codebook 5:** cross-cutting themes brought forward through a controlled theme list, and theme added to the matching fields (D6); country-neutral examples (F2).
- **Codebook 6:** country-neutral wording (F2); source quality per chapter or theme.
- **Codebook 7:** scope overview replaces the Serbia Chapter 5 overview and covers chapters and themes; country-neutral wording for policy options (A6, F2); single static review page with five status labels, not a gate-decision mechanism (E7); run review adds readiness for scaling (E8).

## Version 1.1 (Codebooks 1 to 6) and 1.0 (Codebook 7), 23 October 2026

Revised after the architecture review. Decision IDs refer to `decisions/decision_log.md`.

- **Codebook 1:** ten-link analytical chain replacing the eight-link chain (B1); finding versus judgement vocabulary (B1); first run limited to Serbia and Chapter 5, split into runs 1a and 1b (A1, A2); human review principle; list of seven codebooks (E4).
- **Codebook 2:** fifth source family for civil society and independent monitoring (C5); "evidence weight" renamed "default guidance" (C4); register fields separated from evidence item fields (B2, C2); High, Medium, Low ratings never merged (C4); source requirements list (C1); language rule (A4); SIGMA added to the international organisations list.
- **Codebook 3:** Chapter 5 scope and deferred chapters (A2); comparator pilot exception (A1); time and language limits (A3, A4); roles of the source register and limits log (C2); future-run logic (E3); no automatic expansion (E3).
- **Codebook 4:** evidence item defined (B2); seven claim types and four details on every item (B2); three dates and speaker versus subject (B2); IDs (D2); CSV and JSON formats (D1); record layers (B2); two passes (D3); sample design and EU-first sequence (E1); folders and naming (C3).
- **Codebook 5:** theme lookup through clusters and chapters (D5); two-level taxonomy and its governance (D4); controlled matching fields with no free-text keywords (D5); chain updated to ten links (B1); corroborate and contradict links (B2).
- **Codebook 6:** judgement vocabulary (B1); object and scale for each judgement (B3); relevance and unresolved gap added (B3); six source quality factors (C4); confidence and relevance criteria (C4); judgement records and protection of validated judgements (B3, E3); authority tiers (E2).
- **Codebook 7 (new):** output principles, run 1 products, rules for policy options and format (E4).

## Version 1.0, 20 October 2026

Original Codebooks 1 to 6.
