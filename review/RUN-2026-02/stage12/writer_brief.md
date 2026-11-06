# Stage 12 writer brief, RUN-2026-02 (Moldova)

Written by the lead agent on 6 November 2026 (PC-10: checked against Codebook 7 and judgement rules 0.5).

Read first: `codebooks/CB7_outputs.md` (principles, rules for policy options, agent synthesis labelled), `procedures/P5_outputs_and_close.md` stage 12, `CLAUDE.md` "Writing". For structure and tone read the North Macedonia narratives in `review/RUN-2026-01/stage12/narrative/` (same file names and headings) and one built brief, e.g. `outputs/RUN-2026-01/issue_brief_RI-FMW-001.md`.

Input: the fact pack per issue `review/RUN-2026-02/stage12/factpacks/<issue>.md` (validated judgements, items, interventions, links). Write from the fact pack only. Every factual sentence cites evidence item IDs in parentheses, e.g. (MDA-EU-2026-012-0078); the tool moves them to an annex. Use only IDs that appear in the fact pack (or, for comparator and overview files, in the validated records you are told to read).

Output: `review/RUN-2026-02/stage12/narrative/<issue>.md` with exactly these sections:
- `## In brief`: one paragraph: the EU requirement, what Moldova has done, what is shown to have happened, what remains, then the validated values: "The unresolved gap is <value> and the direction of travel is <value>. Priority is <value> and tractability is <value>." Say "legal only" where the direction reason says so.
- `## How the EU requirement has changed`: how the Commission's wording moved from the 2022 Opinion and 2023 report to the 2026 report (with the Reform Agenda conditions where they apply). For an issue not raised in EU material, say so plainly.
- `## Open questions`: three or four bullets, each stating what evidence would settle it.
Rules: stated and assessed kept apart; adoption is never success; conflicts stated both ways only where the fact pack records them; no new judgement; no mention of stages, gates, proposals or review statuses, and no "validated"; final third-person wording; plain British English; no em dashes; about 350 to 550 words. Moldova's Transnistrian region is not covered by most evidence (LIM-0044); mention it only where the fact pack does.

After writing all your files, run `python3 tools/build_outputs.py --run RUN-2026-02 --issues <comma-separated issues>` and check each built brief reads correctly and every cited ID resolved. Edit no other file. Return one line per issue and any problem found in validated material (record, do not fix).
