# Implementation status brief, RUN-2026-02 (Moldova), stage 10

Written by the lead agent on 6 November 2026; checked against judgement rules 0.5 (PC-10: no stricter test than the rules).

Read first: `rules/judgement_rules.md` (0.5, in full), `codebooks/CB6_assessment.md` (implementation status scale and "adoption is never success"), and for style the validated RUN-2026-01 outputs in `review/RUN-2026-01/stage10/impl_output_1.csv`.

Input: `review/RUN-2026-02/stage10/impl_input_<N>.csv`, one row per item naming an intervention (all items, never truncated, PC-09): intervention_id, name, type, item_id, year, family, item_type, stated_status, chain_link, flags, confidence, text_en. For full context open `evidence/<country>/<source_id>.json`; intervention records are in `entities/interventions.csv`; confirmed conflicts are the `contradicts` links with review_status `validated` in `links/links.csv` (run RUN-2026-02).

Output: `review/RUN-2026-02/stage10/impl_output_<N>.csv`, columns `intervention_id,context_date,value,sources_agree,reason,evidence_item_ids`, at least one row per intervention in the input: the status at the freeze date (context_date 2026-11-06). Add an earlier dated row only where the evidence clearly shows a different earlier status worth recording (for example a law adopted in 2024 that was a draft in 2023).

Scale: proposed, adopted, implemented, in_practice, reversed, unclear, or insufficient_evidence. Adopted means formally approved; implemented means put into effect (system launched, body set up and working, measures carried out); in_practice means evidence of actual use or application at scale, not only launch. Government statements of its own delivery support implemented at most unless corroborated by an independent or Commission item. A draft law stays proposed. When sources conflict, set sources_agree to `no`, cite both sides and say so (this makes the status tier 3 for the analyst). Use insufficient_evidence rather than force a value.

Reason: one to three sentences in final third-person wording, checkable against the cited items; never mention stages, proposals or review statuses; plain British English, no em dashes. Cite every item relied on in evidence_item_ids (semicolon-separated). Machine-translated items are capped at Medium confidence; say so where the status rests on them alone.

Write with Python's csv module. Do not edit any other file. Verify every input intervention has a row and every cited ID is in the input or an evidence file. Return counts by value, the rows with sources_agree no, and any doubts.
