# Procedure P3: Classification and assessment (stages 9 to 11)

Read this file, `rules/classification_rules.md` and `rules/judgement_rules.md` before starting any of stages 9 to 11. Gates G5 and G6 sit in this procedure. Follow "Around every gate" in procedure P1 for the learning log and the review page.

## Stage 9: Classify and link (gate G5)

1. Run pass 2 on every evidence item against the approved taxonomy and mechanism list versions: chain link, reform issues, mechanisms, interventions and actors, and the scope check in the classification rules.
2. Build or update `entities/interventions.csv` and `entities/actors.csv`.
3. Create links in `links/links.csv` following the classification rules. Propose `contradicts` only for the same measure, basis and reference date; record other differences in `review/<run_id>/stage9/noted_differences.csv` and differences within one source in `review/<run_id>/stage9/internal_inconsistencies.csv` (classification rules, PC-18).
4. Before the export, run the same-sentence check, leaving out sentences split at pass 1 (PC-18), and check that country statements in screening reports are classified as country responses (classification rules, PC-06).
5. Export `review/<run_id>/G5_classification.xlsx` with:
   - the ambiguous queue (`taxonomy/ambiguous_queue.csv`);
   - the unmatched queue with proposed new issues;
   - a random 10 per cent of automatically classified items;
   - the spot-check sheet from stage 8;
   - the intervention and actor lists, sorted so possible duplicates sit together;
   - all `contradicts` links, the noted differences and the internal inconsistencies;
   - all items marked `out_of_scope`, and any items still flagged `theme_doubtful`.

**G5 decision (analyst):** resolve the queues, approve or reject proposed issues, and confirm entity merges. If the taxonomy changes, create a new taxonomy version and re-run pass 2 on the affected items only.

## Stage 10: First-cut assessment

Before starting, compute the run's standard search scope for claims of absence with the run-scoped tools, and state it in the same words in every reason (judgement rules, PC-20). If the stage is split across parallel batches, merge the `responds_to` and `leads_to` links from all batches and resolve duplicates before step 5, so that success and attribution are judged once per link (judgement rules, PC-19).

Make judgements in this order, citing evidence items for each:

1. evidence confidence for every item (tier 2);
2. relevance of each item to each reform issue it is tagged with (tier 2);
3. implementation status for each intervention, at the freeze date and at earlier dates where the evidence allows, using `replaced` for a measure replaced by a named successor and `reversed` only where there is none (judgement rules, PC-22);
4. for each reform issue in the target country: direction of travel, unresolved gap, priority and tractability (tier 3, proposals only);
5. success and attribution for each `leads_to` link (tier 3, proposals only).

## Stage 11: Analytical validation (gate G6)

1. Before the export, check each tier 3 reason against its value and cited items, its wording, any claim of absence and any statement of conflict (judgement rules, PC-08, PC-09 and PC-20).
2. Resolve possible duplicate interventions that a tier 3 judgement or an implementation status relies on, since the outputs will rely on them too: for each pair, propose either a `successor_id` with a superseding note on the duplicate, or keeping both with a note on why they differ, and list the proposals in the G6 package for the reviewers (data dictionary 1.7, PC-28).
3. Export one dossier per reform issue in `review/<run_id>/G6_issue_dossiers.xlsx`. Each dossier lays out the chain (EU requirement over the years, country response, implementation, outcomes, gap), the proposed judgements with their reasons and evidence, conflicting evidence, and the confidence and relevance of the key items.
4. Add a sheet listing all tier 3 judgements with columns for the reviewers' decision (`validate`, `override` with a new value and reason).
5. Add a sheet of tier 2 judgements for review by exception: all Low evidence confidence ratings, all machine-translated items, all implementation statuses, every item with a `contradicts` link, and a random 5 per cent of the rest. Reviewers may validate them in bulk and override individual rows.
6. Propose two or three reform issues for the comparator step (procedure P4), with a short reason for each: importance for accession, a clear unresolved gap, and a likelihood that comparator evidence exists.

**G6 decision (the reviewers named in the run record):** validate or override each tier 3 judgement, decide the proposed duplicate interventions, and choose the issues for the comparator step. Record overrides in `judgements/judgements.csv` with the reviewer and reason. Record the gate decision with the reviewers. Once G6 passes, the run's validated judgements appear in the comparisons on the regional page.
