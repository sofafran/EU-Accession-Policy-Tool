# Procedure P5: Outputs, closing a run, and starting the next one (stages 12 to 14)

Read this file and Codebook 7 before starting any of stages 12 to 14. Gates G7 and G8 sit in this procedure.

## Stage 12: Outputs (gate G7)

1. Write the outputs listed in Codebook 7 to `outputs/RUN-2026-01/`:
   - `serbia_ch05_overview.md`;
   - one `issue_brief_<issue_id>.md` per reform issue;
   - `coverage_and_limits_report.md`;
   - for run 1b only: one `comparator_brief_<issue_id>.md` per selected issue, each ending with draft policy options.
2. Use only validated judgements. Label anything else as a proposal.
3. Follow the Codebook 7 principles and the policy option rules. Cite evidence item IDs in an annex at the end of each file, not in the running text.
4. Write in plain British English, in full sentences, without em dashes.

**G7 decision (both reviewers):** sign off each output. Policy options remain labelled as internal drafts even after sign-off, until a separate decision is taken to adapt them for an external audience.

## Stage 13: Close the run (gate G8)

1. Write `runs/RUN-2026-01/run_review.md`:
   - what happened at each gate, with the decisions and conditions;
   - error patterns found in extraction, classification and judgement, and how often they occurred;
   - gaps in the evidence and their effect on the analysis;
   - proposed changes to the codebooks, rules, taxonomy and data dictionary, each with its reason;
   - proposed scope for the next run.
2. Update the limits log: mark limits as lifted or still active, and add methodological limitations found during the run.

**G8 decision (analyst):** approve, edit or reject each proposed change. Approved changes are applied as new versions (codebooks 1.2, rules 1.0 and so on), listed in `codebooks/CHANGELOG.md`, and the run record is closed.

## Stage 14: Starting a new run

A new run only starts when the analyst asks for it. The agent never starts one itself.

1. Create `runs/RUN-YYYY-NN/run_record.md` from the previous one, with the new scope, freeze date, reviewers and current versions. Go through G0.
2. Extend or update the source requirements list (G1).
3. Search for documents. For each one found:
   - same fingerprint as a registered source: reuse it, no processing;
   - a new document (for example the next annual report): register and process it;
   - a new version of a registered document: register it as a new source with `version_of`, and mark the old one `superseded` but keep it and its items.
4. If the extraction rules changed since the evidence was extracted, list the affected sources and ask the analyst whether to re-extract them.
5. If the taxonomy changed, re-run pass 2 on the affected items.
6. If the judgement rules changed, re-run first-cut judgements, but never overwrite validated or overridden judgements. Flag them for re-review at G6 instead.
7. Carry on from the earliest stage affected, following the normal gates.
