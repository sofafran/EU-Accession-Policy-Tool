# Refresh plan: RUN-2026-01 with the 2026 Enlargement Package

Decision E18 (2 November 2026). This is a refresh of the closed North Macedonia alpha, not a new run. It applies the existing procedures unchanged to a small set of new sources. Limits LIM-0036 and LIM-0037 apply.

## Position on 2 November 2026

- The Commission's 2026 Enlargement Package was not published. The North Macedonia country page and the strategy and reports page still list the 2025 report (4 November 2025) and the 2025 factsheet as the latest. The package is due on 4 November 2026.
- The 2026 Rule of Law country chapter (MKD-EU-2026-006, 17 July 2026), the 2026 to 2028 economic reform programme assessment (MKD-EU-2026-003), the May 2026 joint conclusions (MKD-EU-2026-004), the third Reform Agenda payment assessment (MKD-EU-2026-002) and the 21st subcommittee (MKD-EU-2026-005) were registered, extracted and judged in the alpha. They stay as they are, and they do not substitute for the package.
- No other official EU material in scope was published after the 29 October freeze. The 6 October communication "Preparing for a wider Union" and its staff working document were excluded on country scope (LIM-0037).
- **Second check, 2 November 2026 (later the same day).** The North Macedonia country page, the strategy and reports page, the enlargement news page and the Reform and Growth Facility page were checked again. The position is unchanged: no 2026 country report, factsheet or package communication; the latest report and factsheet are dated 4 November 2025, and the latest Reform and Growth Facility decision is the third release of 20 May 2026 (MKD-EU-2026-001 and -002, already held). The press reports Commissioner Kos presenting the package on 4 November 2026; an earlier expected date of 28 October passed without publication. Nothing official and in scope was published after the 29 October freeze. The 13 October 2026 press release on the European Centre for Democratic Resilience falls outside Chapter 2 and the theme list.
- **Point for the refresh G6 (LIM-0037).** "Preparing for a wider Union" (COM(2026) 705, 6 October 2026) names North Macedonia only in lists (the preventive rule-of-law cycle and SEPA payments). It also states that the Council authorised negotiations in June 2026 to extend Roam Like at Home to the Western Balkans. This is regional and EU-side, and changes no judgement on RI-TEC-011. The 2025 communication's regional roaming items were extracted (MKD-EU-2025-002), however, so when the 2026 package communication is registered, check whether it repeats this point. If it does, extract it there and link it to RI-TEC-011 for consistency.
- The North Macedonia page (`analysis/MKD.html` since E19; formerly `analysis.html`) shows a 2025 to 2026 comparison on every issue card. Until a 2026 country report is registered, its 2026 update is "Awaiting 2026 Enlargement Package".

## Steps once the package is published

Follow the procedure named for each step, with the run's current rule versions (extraction 0.4, classification 0.3, judgement 0.4, taxonomy 1.1, theme list 1.3, mechanisms 1.0). PC-01 to PC-17 are not applied: they belong to the next run.

1. **Start (P1, "Around every gate").** Set `current_stage` in the run record to `Refresh R1 sources`. Record the refresh evidence freeze date (the day the package documents are retrieved) in the run record, in a note under the existing freeze date. Do not overwrite the existing freeze date.
2. **Find and acquire (P1 stage 2).** Check the North Macedonia country page, the strategy and reports page and the Commission's press corner. Look for:
   - the North Macedonia 2026 report (staff working document);
   - the North Macedonia 2026 factsheet;
   - the 2026 communication on enlargement policy, and its annexes if they exist;
   - any other official EU material published after 29 October 2026 that bears on Chapter 2 or the technology and AI theme, for example a fourth Reform Agenda payment decision.

   Record each document's exact title, date, reference and type. Never assume that a document exists.
3. **Register (P1 stage 3).**
   - Use the next source IDs (`tools/next_id.py source --country MKD --family EU --year 2026`), the existing requirements (REQ-001 annual report, REQ-002 communication) and `document_type` as already used (`annual report`, `communication`). For the factsheet, use a new requirement only if none fits, and propose it at G6.
   - Hash the originals and keep them read-only.
   - The page treats a registered, available `annual report` published in 2026 as the 2026 update. No change to the page is needed.
4. **Source quality (P1 stage 4).** Propose ratings as in the alpha. G2 may pass under Sofia's standing instruction (E18), with a gate log row noting that she confirms it at G6.
5. **Extract (P2 stage 8).**
   - Run pass 1 on the new sources only, with Chapter 2 and technology and AI material only and exact quotes.
   - Run `tools/verify_quotes.py` and then `tools/validate_data.py`.
   - Nothing existing is edited or removed.
6. **Classify and link (P3 stage 9).**
   - Classify the new items against the existing taxonomy. Items that match no issue go to `taxonomy/unmatched_queue.csv` as candidate new issues.
   - Run `python3 tools/refresh_delta.py --sources <new source IDs>`. It writes `review/RUN-2026-01/refresh/refresh_delta.csv`, with each new item, its issue, the earlier items on the same issue and link type, and the current judgements.
   - For each new item, propose one link to an earlier item, recorded in `links/links.csv`:
     - `same_as_earlier`: repeats the 2025 text;
     - `corroborates`: confirms an existing finding;
     - `contradicts`: conflicts with an existing finding, which is then reported and not resolved silently;
     - `replaces` or `amends`: updates a requirement.

     An item with no link is genuinely new.
   - G5 may pass under the standing instruction, to be confirmed at G6.
7. **Re-judge only affected issues (P3 stages 10 and 11).**
   - An issue is affected only if a new item touches it.
   - For each affected issue, review the direction of travel, unresolved gap, priority and tractability. Where the value or the reasoning changes, add a new judgement row with `supersedes` set and `review_status` `proposed`. Never edit a validated row; set its `rereview_flag`.
   - Where the 2026 item only confirms the finding, keep the judgement, and record the confirmation through the `corroborates` link.
   - Unaffected issues are not touched.
8. **Refresh gate (G6).** Build `review/RUN-2026-01/G6_refresh.xlsx` with `tools/export_review.py` (add a refresh option to it if the existing G6 export does not fit, as a tier 1 tool change). Its contents:
   - the new sources;
   - the links that say what is new, confirmed or contradicted;
   - changes in direction and priority;
   - candidate new issues;
   - LIM-0036 and LIM-0037.

   Summarise it in chat for Sofia; she may answer "accept all". Record the gate in `registers/gate_log.csv` with gate `G6` and a new gate decision ID.
9. **Outputs (P5 stage 12, G7).**
   - Rebuild the issue briefs of affected issues only with `tools/build_outputs.py`, and update the coverage and limits report.
   - Comparator briefs and draft policy options change only if an affected issue is one of RI-FMW-001, RI-TEC-028 or RI-TEC-036. If it is, flag them for review rather than rewriting them.
   - Record G7 with a new gate decision ID.
10. **Pages.**
    - Run `python3 tools/build_review_page.py --run RUN-2026-01`, then check `analysis/MKD.html` with `tools/tests/analysis_page_test.js` and `analysis.html` with `tools/tests/regional_page_test.js`. Expected counts (for example the "evidence held" filter) may need updating.
    - Update `alpha_summary.html` by hand from the refreshed records (decision E16): the findings, the counts and the refresh note in section 2.
11. **Close.** Add a line to `run_notes.md` and propose alpha learning log rows if the refresh taught something material. Commit with a message such as `RUN-2026-01 refresh G6 pass: 2026 Enlargement Package`, then push.
