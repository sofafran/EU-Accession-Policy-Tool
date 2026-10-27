# Procedure P3: Classification and assessment (stages 9 to 11)

Read this file, `rules/classification_rules.md` and `rules/judgement_rules.md` before starting any of stages 9 to 11. Gates G5 and G6 sit in this procedure.

## Stage 9: Classify and link (gate G5)

1. Run pass 2 on every evidence item against the approved taxonomy and mechanism list versions: chain link, reform issues, mechanisms, interventions and actors.
2. Build or update `entities/interventions.csv` and `entities/actors.csv`.
3. Create links in `links/links.csv` following the classification rules.
4. Export `review/RUN-2026-01/G5_classification.xlsx` with:
   - the ambiguous queue (`taxonomy/ambiguous_queue.csv`);
   - the unmatched queue with proposed new issues;
   - a random 10 per cent of automatically classified items;
   - the spot-check sheet from stage 8;
   - the intervention and actor lists, sorted so possible duplicates sit together;
   - all `contradicts` links.

**G5 decision (analyst):** resolve the queues, approve or reject proposed issues, and confirm entity merges. If the taxonomy changes, create a new taxonomy version and re-run pass 2 on the affected items only.

## Stage 10: First-cut assessment

Make judgements in this order, citing evidence items for each:

1. evidence confidence for every item (tier 2);
2. relevance of each item to each reform issue it is tagged with (tier 2);
3. implementation status for each intervention, at the freeze date and at earlier dates where the evidence allows;
4. for each reform issue in Serbia: direction of travel, unresolved gap, priority and tractability (tier 3, proposals only);
5. success and attribution for each `leads_to` link (tier 3, proposals only).

## Stage 11: Analytical validation (gate G6)

1. Export one dossier per reform issue in `review/RUN-2026-01/G6_issue_dossiers.xlsx`. Each dossier lays out the chain (EU requirement over the years, country response, implementation, outcomes, gap), the proposed judgements with their reasons and evidence, conflicting evidence, and the confidence and relevance of the key items.
2. Add a sheet listing all tier 3 judgements with columns for the reviewers' decision (`validate`, `override` with a new value and reason).
3. Add a sheet of tier 2 judgements for review by exception: all Low evidence confidence ratings, all machine-translated items, all implementation statuses, every item with a `contradicts` link, and a random 5 per cent of the rest. Reviewers may validate them in bulk and override individual rows.
4. Propose two or three reform issues for the comparator pilot (run 1b), with a short reason for each: importance for accession, a clear unresolved gap, and a likelihood that comparator evidence exists.

**G6 decision (both reviewers named in the run record):** validate or override each tier 3 judgement and choose the issues for run 1b. Record overrides in `judgements/judgements.csv` with the reviewer and reason. Record the gate decision with both reviewers.
