# Comparator case brief, RUN-2026-02 (Moldova), P4 step 5

Written by the lead agent on 6 November 2026 (PC-10: checked against judgement rules 0.5, which include the G6b rule 0.4 on case transferability).

Read first: `procedures/P4_comparator_pilot.md`; `rules/judgement_rules.md` (0.5: comparator relevance, transferability, success and attribution, implementation status, PC-08 to PC-10, "Several countries"); `codebooks/CB6_assessment.md`; the alpha's validated cases and judgements in `review/RUN-2026-01/run1b/cases/` (cases_*.csv, judgements_*.csv, links_*.csv) and `entities/comparator_cases.csv` (CMP-0001 to CMP-0009) for structure and style; the Moldova issue definitions in `taxonomy/reform_issues.csv` and Moldova's validated judgements for your issue in `judgements/judgements.csv` (object_id `<issue>@MDA`, run RUN-2026-02) so you know Moldova's gap.

Evidence: comparator items of run RUN-2026-02 in `evidence/HRV`, `evidence/SRB`, `evidence/MNE`, `evidence/ALB` (use `run_items(d, 'RUN-2026-02')` from `tools/common.py`); for North Macedonia, the validated RUN-2026-01 items and judgements already held (reused, not collected again, E19); for the reused cases CMP-0008 (Albania) and CMP-0009 (Montenegro), the validated case records and their items. North Macedonia's and other countries' judgements are context, never evidence about Moldova. Moldova's own items are the target side.

Output in `review/RUN-2026-02/run1b/cases/` (your issue only):
1. `cases_<issue>.csv`: one row per new case, columns as `entities/comparator_cases.csv` (case_id blank; the lead agent assigns IDs; country; reform_issue_id; intervention_ids; description; problem_addressed; reform_or_mechanism; how_implemented; evidence_of_results; limitations_of_evidence; practical_lesson (for Moldova, labelled agent synthesis); transferable; not_transferable; selected_at GATE-0025; notes). Keep reform, implementation, outcome and attribution apart; cite item IDs in parentheses.
2. `judgements_<issue>.csv` with columns judgement_type,object_type,object_id,context_id,value,reason,evidence_item_ids, using a placeholder object_id `NEW-<country>` for new cases and the CMP ID for reused ones:
   - comparator_relevance (object_type issue_comparator, context_id `<issue>@MDA`), High, Medium or Low: how closely the case matches Moldova's issue and mechanisms and how the context differs;
   - transferability (object_type issue_comparator, context_id `MDA`), likely, conditional or unlikely, labelled "Agent synthesis, not stated by a source:" in the reason;
   - implementation_status (object_type intervention, context_id the date, 2026-11-06 unless the evidence is dated earlier) for each comparator intervention of the new cases that has no validated status yet;
   - success and attribution (object_type link, object_id `NEW-LINK-<n>`) for each leads_to link you propose; never success from government reporting alone; adoption is never success.
3. `links_<issue>.csv` (from_id,to_id,link_type,basis): leads_to from comparator interventions to outcome items, numbered in order as NEW-LINK-1, NEW-LINK-2 in a first column `ref`.
Reasons: one to three sentences, final third-person wording, no process language, plain British English, no em dashes; claims of absence state the search. Edit no other file. Return a short summary of each case, the values, and any doubt.
