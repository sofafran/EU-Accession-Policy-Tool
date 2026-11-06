# Problems in validated material found while writing (for G7, not fixed)

## W3
- RI-TEC-024: INT-MDA-0232 (draft Government Decision on 5G network cybersecurity) proposed, while MDA-EU-2026-012-0125 and INT-MDA-0568 (adopted) record 5G security secondary legislation adopted in 2026; possibly the same act (duplicate entity or out-of-date status).
- RI-TEC-002: the validated gap reason attributes "53 and 37 of its 68 actions" to the Government; the cited MDA-GOV-2025-003-0281 is a comment by STISC, a consulted body.
- RI-TEC-014: relies on MKD-EU-2023-002-0045, a horizontal Communication passage filed under the MKD prefix (scaling note S8, known).
- RI-TEC-002: the 2026 report names the strategy "2025-2027" (source wording, MDA-EU-2026-012-0104).

## W4
- Tool: the annex entry for MKD-EU-2023-002-0054 (RI-TEC-036) has no institution or title; build_outputs' run-scoped register omits horizontal sources filed under MKD but used by this run (to fix, tier 1).
- RI-TEC-036: relevance JDG-018540 says "It concerns the same country" for a horizontal enlargement-wide item (the written rule did not distinguish horizontal passages).
- RI-TEC-004: gap reason says 16 of 31 institutions used the permits system "at the 2024 audit"; MDA-GOV-2024-001-0054 says 2020 audit.
- RI-TEC-015: MDA-CSO-2026-001-0012 (March 2026, register not yet operational) against MDA-EU-2026-004-0003 (launched 29 December 2025); no contradicts link.
- RI-TEC-015: Law No. 71/2017 printed in MDA-IO-2024-002-0061 (source misprint; INT-MDA-0452 is Law 71/2007).
- RI-TEC-020: MDA-GOV-2026-009-0006 gives 347 decisions split as 266 plus 173 (source arithmetic).
- Status label "reversed" used for laws repealed and replaced (INT-MDA-0424, INT-MDA-0428); the scale has no "replaced" value.
- Search scopes stated differently: "1,451 Moldova items" (EU, IO, CSO and RES only, for success) against "3,631 items held in the Moldova evidence files" (issue judgements).

## W2
- RI-TEC-039: INT-MDA-0041 status reason says the WCAG 2.2 order "had not started in 2025"; the source item MDA-GOV-2026-002-0046 is April 2026 and the gap reason says 2026.
- RI-TEC-018: the shared definition includes "can be left without a director", which the Moldova evidence does not show (definition drafted from North Macedonia).
- RI-TEC-001 and RI-TEC-018 rely on horizontal Communication items filed under MKD IDs (MKD-EU-2026-009-0022, MKD-EU-2025-002-0020); they resolve correctly (scaling note S8).
- RI-TEC-007: the priority reason states that the link to the technology theme is uncertain.

## Tool fix
- build_outputs.py 1.3.2: sources registered by another run but extracted by this run (horizontal passages under MKD, held comparator reports) now appear in the annex with the role from this run's extraction record; RUN-2026-01 outputs rebuild unchanged.

## W5
- (Tool annex metadata for MKD-filed horizontal items: fixed in build_outputs 1.3.2.)
- RI-TEC-016: Law No. 109/2025 dated May 2025 by the Government and civil society, while the Commission dates a partly harmonising law to July 2026 (MDA-EU-2026-012-0118); no contradicts link; the direction reason reads them as the same law.
- RI-TEC-011: the regulator says "fully aligned" (MDA-GOV-2026-014-0076), civil society "only partially compatible" (MDA-CSO-2026-001-0056); no contradicts link.
- RI-TEC-026: conflicts on EVOSign (INT-MDA-0009) and the eIDAS draft law (INT-MDA-0248, INT-MDA-0069) are stated in validated statuses but have no contradicts link.
- RI-TEC-026: an outcome link from INT-MDA-0398 (integrated health information system, proposed; the Commission says not in place) to MDA-GOV-2025-003-0032 ("when the Integrated Health Information System was implemented") is inconsistent with RI-FMW-015.
- RI-TEC-021: the shared definition mentions biometric data and the data protection authority not consulted; the only Moldova item concerns campaign databases.

## W1
- RI-TEC-022: the tractability reason says lack of staff "limited supervision in 2025", citing MDA-GOV-2026-010-0036, which concerns notifying users of network access restrictions.
- RI-TEC-038: the gap reason dates the specifications and call for bids to 2025; the items give only day and month (year inferred from MDA-GOV-2026-011-0014).
- RI-FMW-001: MDA-GOV-2025-002-0006 (EU citizens need a temporary residence permit for work) beside MDA-EU-2024-001-0052 (no work permit since January 2024); this pair was proposed as contradicts and rejected at G5 as an apparent difference (permit types differ); the brief states both facts.
- RI-TEC-017: INT-MDA-0608's validated status reason addresses the analyst ("should decide whether the two entities should be merged"), not final wording (PC-08).
