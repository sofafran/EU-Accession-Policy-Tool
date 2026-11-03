# Scaling note: from one country to two

RUN-2026-02 (Moldova), started 3 November 2026 under decision E20. This note lists problems that arise because the project now has two countries rather than one. It is kept short and updated through the Moldova run; Sofia reviews it before Montenegro (RUN-2026-03) starts. Problems that would arise in any run are recorded in `run_notes.md`, not here.

No change to the method is proposed unless a problem below says so. Each point says what was found, what has been done, and what, if anything, needs a decision.

## Status at stage 0

| ID | Problem | Kind | Status |
|---|---|---|---|
| S1 | Tools and tests assumed one run | Tooling | Fixed at stage 0, no method change |
| S2 | A source can hold only one run's extraction | Data model | Decision at G0 (G0-D02) |
| S3 | Shared issues were all built from North Macedonia evidence | Taxonomy | Watch at G4 and G5; check proposed |
| S4 | Changes to a shared issue can alter how a closed run is shown | Taxonomy and pages | Rule proposed for G4 |
| S5 | Earlier unmatched Moldova items were raised against North Macedonia issues | Taxonomy | Re-examined at G4 |
| S6 | The method has no rule on territorial coverage | Scope | Run deviation at G0 (G0-D03) |
| S7 | Countries compared on different rule versions and within-country scales | Regional page | Check at Moldova's G6 |
| S8 | Horizontal EU documents are registered under the first country that used them | Register | Reused by ID; change proposed for the Moldova review |
| S9 | Restricted documents and a public repository | Sources | Kept out of git (LIM-0045); tool change proposed |

## S1. Tools and tests assumed one run

**Found:** adding a second run record changed the default run of every tool. Three tests failed because they assumed RUN-2026-01 was active; the review page kept alpha wording; the North Macedonia country page linked to `index.html`, which now shows Moldova.

**Done:** tests name their run; `build_review_page.py` 1.5.0 labels pages by run, links each country page to its own run's review page and links the active page to earlier runs. 91 of 91 tests pass. North Macedonia content is unchanged.

**Remaining:** add a test with two runs before RUN-2026-03 (ALN-0035).

## S2. A source can hold only one run's extraction

**Found:** 11 Moldova evidence files were extracted in the alpha's comparator step for three North Macedonia issues only. An evidence file holds one extraction record, so this run cannot add its own extraction without overwriting the alpha's, which the closed-run rule and rule 6 forbid.

**Needs a decision (G0-D02):** this is a genuine scaling problem and the only one so far that needs a data-model change. The recommended fix is small: an optional `earlier_extractions` list in the evidence file (evidence schema 1.3). Existing items keep their IDs. It applies to every country with comparator sources from earlier runs (ALN-0036).

## S3. Shared issues were all built from North Macedonia evidence

**Found:** the 48 approved shared reform issues were drafted from North Macedonia's EU requirements. Many will fit Moldova, because the Commission uses similar wording across reports. The risk is anchoring: a Moldova item is classified under the nearest North Macedonia issue when its substance differs (for example a different legal instrument or a different stage of alignment).

**Proposed, no method change:** the existing rule (classify only where the issue genuinely fits; otherwise the unmatched queue) is enough if it is checked. At G5, report for Moldova the share of items matched to existing issues and the share sent to the unmatched queue, and have the second-pass agent check a sample of matched items for forced fits. If the check finds forced fits, raise a rule change then.

## S4. Changes to a shared issue can alter how a closed run is shown

**Found:** the regional page reads the current `taxonomy/reform_issues.csv`, and the country pages read the current mechanism and theme lists. If Moldova leads to rewording, merging or retiring an issue that North Macedonia's validated judgements cite, the North Macedonia pages would show the new wording against judgements made under taxonomy 1.1. PC-11 (adding MEC-04 to RI-TEC-028) is the first case.

**Proposed for G4, no redesign:** during this run, change the shared taxonomy additively only (new issues, new mechanisms). Any change to an issue that a closed run's validated judgements cite is put to the gate with a note of its effect on that run, and the closed run keeps its taxonomy version on its judgements. Whether the pages should show each run's issues as at its own version is a question for the Moldova review.

## S5. Earlier unmatched Moldova items were raised against North Macedonia issues

**Found:** 11 Moldova rows in `taxonomy/unmatched_queue.csv` come from the comparator step, where the question was whether they fitted three North Macedonia issues. "Unmatched" there does not mean unmatched for a full Moldova run.

**Done:** recorded in the run record; they are re-examined at this run's G4 alongside new items. Their rows are not changed or deleted.

## S6. The method has no rule on territorial coverage

**Found:** North Macedonia raised no question about which territory a finding covers. Moldova does: the constitutional authorities do not control the Transnistrian region. Ukraine, Georgia and Kosovo will raise similar questions.

**Needs a decision (G0-D03):** handled for Moldova as a run deviation. If it recurs in Montenegro or later, a short general rule in Codebook 3 may be proposed after the Moldova review, not now.

## S7. Countries compared on different rule versions and within-country scales

**Found:** North Macedonia's judgements were made under judgement rules 0.2 to 0.4 and taxonomy 1.1; Moldova's will use judgement rules 0.5. Priority and tractability are judged within a country, not across countries. The regional page will compare the two once Moldova passes G6.

**Proposed:** at Moldova's G6, check that the regional page shows each country's rule versions and states that priority is a within-country judgement, so the comparison is not read as a ranking of countries. No change before then, because there is nothing to compare yet.

## S8. Horizontal EU documents are registered under the first country that used them

**Found at stage 2:** the enlargement communications for 2023 to 2025 and the December Council conclusions cover every candidate country. They were registered in the alpha as `MKD-EU-...` with `country` MKD. Moldova downloads were byte-identical, so they are matched to Moldova's requirement lines by their MKD IDs and not registered again (IDs are permanent).

**Effect:** filters by country, the source counts on country pages, and quality ratings per country treat these documents as North Macedonia documents. This will recur in every country.

**Proposed for the Moldova review, no change now:** allow `country` to read `multi` (or a semicolon list) for horizontal EU documents, keeping the existing IDs. Items extracted from them already carry their own `country`, so evidence is not affected.

## S9. Restricted documents and a public repository

**Found at stage 2:** two Council documents marked LIMITE were publicly downloadable and were downloaded before the marking was seen. The repository and its pages are public (E10), so anything filed under `sources/` would be published on the next push.

**Done:** both files are listed in `.gitignore`, registered `excluded`, and not used (LIM-0045).

**Proposed:** `acquire.py` should check the first pages for "LIMITE" or similar markings and refuse to file the document. This is a small tool change, not a method change.
