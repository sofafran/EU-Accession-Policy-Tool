# RUN-2026-02: steps once the 2026 Moldova report is published

The run is paused at stage 7 (EU extraction and taxonomy), waiting for the Commission's 2026 report on Moldova, due in the 2026 Enlargement Package on 4 November 2026. The evidence freeze date is 6 November 2026, or earlier once the report is out (G0-D01).

Sofia only needs to say that the report is published, ideally with its link. Everything below then follows in order.

1. **Register the report.** Download it from enlargement.ec.europa.eu with `tools/acquire.py` as the next `MDA-EU-2026-0NN` ID, convert it, match it to REQ-073 and propose its quality rating. Also register the 2026 enlargement communication if it covers Moldova (REQ-076).
2. **Freeze the evidence.** Set the evidence freeze date in the run record to the report's publication date, if earlier than 6 November 2026.
3. **Extract it** with extraction rules 0.5, as approved at G3 (GATE-0017): the Chapter 2 section in full and every section for technology and AI recommendations. Then run the quote check and an independent second pass.
4. **Map its requirement items** to the shared taxonomy, in the same way as the rest of the EU evidence (`review/RUN-2026-02/G4_issue_mapping.csv`). New candidate issues go through `taxonomy/unmatched_queue.csv`.
5. **Prepare G4**, the first gate since G0 that needs Sofia's own decisions. The package `review/RUN-2026-02/G4_taxonomy.xlsx` will set out:
   - any new shared issues proposed from Moldova's evidence;
   - PC-11 (MEC-04 for RI-TEC-028);
   - the theme-list question M4 (digital market rules and roaming);
   - the rule clarifications M1 to M3;
   - confirmation of the gates passed under the standing instruction (G1, G2 and G3).
6. After G4: full extraction of the national, international, research and civil-society sources (stage 8), then classification and assessment (stages 9 to 11).

What is already done without the report: setup and G0; sources and G1 and G2; the extraction sample and G3; extraction of all other available EU sources, with second passes; and a draft mapping of the EU items to the shared taxonomy.
