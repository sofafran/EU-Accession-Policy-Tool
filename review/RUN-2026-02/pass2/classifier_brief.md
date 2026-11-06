# Pass 2 classification brief, RUN-2026-02 (Moldova), stage 9

Written by the agent on 5 November 2026 for the classifier agents (PC-10: checked against classification rules 0.4). Project root `/workspaces/EU-Accession-Policy-Tool`.

## Read first
1. `rules/classification_rules.md` (version 0.4), in full.
2. `runs/RUN-2026-02/run_record.md`, "Run-specific settings" (Chapter 2 boundary; Transnistria, LIM-0044).
3. `review/RUN-2026-02/pass2/issues_active.csv`: the approved issues of taxonomy 1.2 (definitions, exclusion notes, usual mechanisms). Use definitions and exclusion notes, not labels.
4. `taxonomy/mechanisms.csv` (mechanism list 1.0).
5. `review/RUN-2026-02/G4_decisions.csv` (rulings G4-D01 to G4-D18) and `review/RUN-2026-01/G5_decisions.csv` (alpha rulings, now in classification rules section 8).

## Your input and output
Input: `review/RUN-2026-02/pass2/input/<batch>.csv`, one row per item: item_id, family, type, text_en (English or the translation), summary, scope_basis, themes, chapter, flags, extraction_note, intervention_as_stated, stated_status, g4_seed_issues (the G4 mapping, accepted at G4 for EU requirement items; keep it unless the text clearly says otherwise, and say why). For the full quote, open the evidence file `evidence/<country>/<source_id>.json`.

Output: `review/RUN-2026-02/pass2/output/<batch>.csv` with exactly these columns, one row per input item, same order:
`item_id,chain_link,reform_issue_ids,mechanism_ids,classification_status,classification_note,interventions_named,proposed_label,proposed_definition,candidate_issue_ids,pass1_query`
- `chain_link`: one of eu_requirement, country_response, implementation, outcome, unresolved_gap, lesson (default table in rules section 1; EU findings and recommendations are eu_requirement; non-EU findings on how a named measure is applied are implementation; interventions are country_response; country statements in screening reports are country_response, PC-06).
- `reform_issue_ids`: 0 to 3 approved issue IDs, semicolon-separated, best fit first.
- `mechanism_ids`: 0 to 3, only where the item itself (or a barrier it states) supports the mechanism.
- `classification_status`: auto, queued_ambiguous, queued_unmatched or out_of_scope.
- `classification_note`: short reason where there is any doubt, the scope ruling applied, or an awkward fit (S3).
- `interventions_named`: the measures, laws, systems or programmes the item names, semicolon-separated, in English, as specific as the text allows (for example "Law No. 105/2018 on employment promotion and unemployment insurance"; "MConnect interoperability platform"); empty if none.
- `proposed_label`, `proposed_definition`: only for queued_unmatched (country-neutral wording; for a problem raised only by national or independent sources, the definition starts "Not raised in EU material:").
- `candidate_issue_ids`: only for queued_ambiguous (the two or three issues that fit equally).
- `pass1_query`: only if you see a pass 1 error (wrong type, theme tag, quote boundary); never fix pass 1 fields yourself.
Write the CSV with Python's csv module (quote fields containing commas). Do not edit any other file.

## Rulings to apply
- **Chapter-level ratings** of a whole chapter, and "previous recommendations remain valid": no issue, status auto, note "chapter-level rating; fits no single issue (G5-D14 of RUN-2026-01)". A sub-area rating that matches an issue goes to it.
- **Scope check (rules section 5):** `chapter` items are in scope; `theme` items outside the in-scope chapters are in scope only if they fit an approved issue (every approved TEC issue is supported by an in-scope recommendation); `chain` items only if they fit an issue already in scope. Otherwise out_of_scope with a reason. An item that fits no issue but describes a genuine in-scope problem goes to queued_unmatched instead.
- **G4 rulings:** MDA-EU-2023-002-0001 and -0002 (admission of third-country workers under EU legal migration directives) out_of_scope as Chapter 24 acquis (G4-D03); items of rejected candidates CI-04 (registers for official statistics) and CI-05 (one ministry's fragmented sector systems) out_of_scope (G4-D04); back-office justice IT (random case allocation) and the tax service's internal digital programme out_of_scope (G4-D12, R22); MDA-EU-2025-001-0046 and -0047 out_of_scope (G4-D14); roaming items go to RI-TEC-011 and Digital Services Act, Digital Markets Act, geo-blocking and e-commerce items to RI-TEC-034, as in scope (G4-D11); semiconductor (Chips Act) items to RI-TEC-040 (G4-D07); e-procurement system outdated or to be replaced to RI-TEC-038, a working but underused system to RI-TEC-006 (G4-D01); EHIC domestic preconditions (national health insurance card, integrated health information system) to RI-FMW-015 (G4-D02); accessibility of public sector websites and apps to RI-TEC-039 (G4-D05).
- **Awkward fits (G4-D06, S3):** RI-TEC-006, RI-FMW-003, RI-FMW-012, RI-TEC-016, RI-TEC-009 and RI-TEC-023 stay unchanged; where Moldova's situation differs in kind, assign the issue only if the definition genuinely fits and say "S3 awkward fit: <how it differs>" in the note. Never stretch an issue: if it does not genuinely fit, use queued_unmatched.
- **Alpha rulings:** military and classified systems out; digital education out (R2); government-wide inspection systems framed as digital government in; regional evidence that does not name Moldova may support an issue (note "regional"); two versions of one report are one source; cybercrime enforcement out; Open Balkan style regional labour mobility of nationals out; nationals' access to EU labour markets out.
- **Transnistria (LIM-0044):** classify normally; add "LIM-0044" to the note where the claim concerns the Transnistrian region.
- **Comparator items:** none in this run (all role target).
- **Ambiguity:** use queued_ambiguous only when two or three issues fit equally and the choice matters; otherwise pick the best and list a second issue.

## Return
A short summary: counts by status, the issues used most, any pattern of forced fits you resisted, and any proposed new issue labels.
