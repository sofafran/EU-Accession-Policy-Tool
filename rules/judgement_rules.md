# Judgement rules

Version 0.6, 6 November 2026. Status: approved at G8 of RUN-2026-02 (GATE-0030) as part of PC-18 to PC-32, applied on 6 November 2026 before RUN-2026-03. Changes create a new version and are listed in the change log at the end of this file. Version 0.5 was approved at G8 of RUN-2026-01 (GATE-0013) as part of PC-01 to PC-17 and applied before RUN-2026-02 (decision E19). Version 0.4 was approved at G6b of RUN-2026-01 (GATE-0011).

These rules tell the agent how to make first-cut judgements. The questions, scales and criteria are defined in Codebook 6, which takes precedence if the two ever differ. This file adds the operational detail.

## 1. Every judgement record

Each judgement is one row in `judgements/judgements.csv` (or `judgements/source_quality.csv` for source quality) and must contain:

- the judgement type and the object it attaches to (see the table below);
- the value, taken from the allowed scale;
- a reason of one to three sentences, written so that a reviewer can check it;
- the evidence item IDs it relies on (at least one, except for source quality);
- `made_by` (`agent` or the reviewer's name), `review_status` (`proposed`, `validated` or `overridden`), `rereview_flag` where it applies, and the codebook, rules and taxonomy versions used.

## 2. What each judgement attaches to, and who decides

| Judgement | `object_type` | Scale | Authority tier |
|---|---|---|---|
| Source quality | `source` (per chapter or theme, in `source_quality.csv`) | High / Medium / Low | 2: agent decides, analyst reviews by exception at G2 |
| Evidence confidence | `item` | High / Medium / Low | 2: spot checks |
| Relevance | `item` for a reform issue (`context_id`) | High / Medium / Low | 2: spot checks |
| Implementation status | `intervention` at a date | proposed / adopted / implemented / in_practice / replaced / reversed / unclear | 2 if sources agree; 3 if they conflict |
| Direction of travel | `issue_country` | new / worsening / persistent / improving / largely_resolved | 3: analyst decides at G6 |
| Unresolved gap | `issue_country` | open / partly_addressed / largely_closed | 3 |
| Success or result | `link` (intervention to outcome) | worked / failed / mixed / too_early | 3 |
| Attribution | `link` (intervention to outcome) | High / Medium / Low | 3 |
| Comparator relevance | `issue_comparator` (object ID is the comparator case) | High / Medium / Low | 3 |
| Transferability | `item` (lesson stated by a source) or `issue_comparator` (the case's lesson, which is agent synthesis and labelled so in the reason and in every output), for the target country | likely / conditional / unlikely | 3 |
| Priority | `issue_country` | High / Medium / Low | 3 |
| Tractability | `issue_country` | High / Medium / Low | 3 |

Every scale also allows `insufficient_evidence`. Use it rather than force a value.

## 3. Operational rules

- **Source quality:** fill in the six factor columns first (yes, partly, no or not applicable; primary or secondary), then the overall value. A source can have different ratings for different chapters or themes.
- **Relevance (PC-23):** a horizontal passage addressed to all enlargement countries, or to a group of them, without naming the target country, does not concern "the same country" in the Codebook 6 criteria. Rate it at most Medium for an issue, and say in the reason that the passage is horizontal. Only a statement about the target country itself can be High.
- **Evidence confidence:** apply the Codebook 6 criteria. Cap at Medium if `machine_translated` is true. Lower by one level if the item is flagged `hedged` or `ocr`, unless the claim is corroborated.
- **Implementation status, replaced or reversed (PC-22):** use `replaced` for a measure repealed and replaced by a named successor. It needs a `replaces` link from the successor to the measure, and the reason names the successor; the successor's own status is judged separately. Keep `reversed` for a measure withdrawn, suspended or repealed without a successor. A replaced measure is not described as backsliding. Pass 1 stated status is unchanged: a source that says a law was repealed still gives `reversed` there, and this judgement decides between the two.
- **Direction of travel:** base it on the sequence of EU standard-scale wording across years (`preparation_level`, `progress_level`) first, then on independent evidence. Cite the items for each year used. If the Commission wording is unchanged for three or more reports, the default is `persistent`. Use only wording with `eu_scale.applies_to` `chapter` for a chapter-wide issue; use `sub_area` wording only for an issue that matches that sub-area, and say so in the reason. The standard scale rates a whole chapter. For an issue that comes from a cross-cutting theme, or that is only part of a chapter, use the chapter's scale as context only: base the judgement on the issue's own items (repeated or changed recommendations and findings) and say in the reason that the scale was not decisive.
- **Unresolved gap:** compare the latest EU requirement items for the issue with the implementation status of the interventions that respond to them. At stage 10 these statuses are still proposals; the reviewers check both together at G6. Do not mention their proposal status in the reason (see wording of reasons). Describe in one sentence what remains.
- **Success and attribution:** only judge an outcome that has a `leads_to` link. Never judge success from government reporting alone (Codebook 2).
- **Parallel batches (PC-19):** when stage 10 is split across parallel batches, first merge the `responds_to` and `leads_to` links that all batches propose, and resolve duplicates so that each intervention and outcome pair has one link (a duplicate is marked `rejected`, never deleted). Then judge success and attribution once per link, so that no link receives two pairs.
- **Priority:** consider whether the issue appears in EU benchmarks or repeated key recommendations, and how central it is to the chapter or theme. **Tractability:** consider the mechanisms involved, the actors needed and evidence of past progress.
- **Priority test (G6-D02 of RUN-2026-01):** High usually means the issue is named in a benchmark, Reform Agenda payment condition or key recommendation repeated across three or more reports, and is central to the chapter or theme. A core acquis requirement repeated across three or more reports, with no progress recorded in the main findings, can also be High; say why. Evidence volume, and national or audit material, never raise priority. Calibrate priority across all issues before a gate.
- **Fulfilled conditions (PC-21, from G6-D01 of RUN-2026-02):** a Reform Agenda payment condition that the evidence records as fulfilled, and that the latest Commission report does not repeat as a recommendation, does not alone make an issue High.
- **Countries with fewer than three standard reports (PC-21):** the three-report tests for priority and for a `persistent` direction count the Commission's standard annual reports on the country within the time window. Where fewer than three such reports exist, the tests apply to all of them: a key recommendation or core acquis requirement repeated in every available report, and in at least two, meets the repetition part of the priority test; unchanged standard-scale wording in every available report, and in at least two, may support `persistent` but is not the default. With one report only, no repetition test is met: direction is `new` or `insufficient_evidence`, and priority rests on benchmarks, open Reform Agenda payment conditions and how central the issue is. The reason states how many standard reports were available and how the test was applied.
- **Legal progress (G6-D05):** a law reviewed by the Commission may count as `improving`, with the gap as `partly_addressed`, but the reason and the outputs must say the improvement is legal only. Adoption alone is not improvement.
- **Regional evidence:** a claim that does not name the target country may support an issue but cannot alone support a finding about the country.
- **Versions of one report:** count once.
- **Conflicting evidence:** when items contradict each other, say so in the reason and cite both sides. Do not resolve a conflict by choosing the higher-quality source without saying so.
- **Wording of reasons (PC-08):** write each reason in final, third-person wording, as it will appear in the outputs. Never refer to the stage, to proposals or to review statuses. A reason that says sources conflict must cite a `contradicts` link, or be reworded. Before G6, check each reason against its value and the items it cites.
- **Claims of absence (PC-09, refined by PC-20):** a reason that says something is absent (no item, no evidence, not mentioned) states the search behind it. Every such claim in a run uses one standard search scope: the items this run created for the target country, including its items from horizontal documents. Items created by earlier runs, including their comparator items, are outside it. The scope is computed once per stage with the run-scoped tools, not counted by hand, and every reason states it in the same words. Inputs to an agent making a judgement are never truncated by count.
- **Helper agents (PC-10):** briefs to helper agents are checked against these rules before use. A brief never applies a stricter test than these rules; any stricter test is logged as a proposed rule change instead.
- **Several countries:** judgements are made for one country on its own evidence. Another country's judgement on the same issue is never evidence for this country, except through the comparator step.

## 4. Re-runs

- Never change the value, reason or `review_status` of a judgement that is `validated` or `overridden`.
- If new evidence or a new rules version would change such a judgement, add a new proposed row whose `supersedes` field names the old judgement, set `rereview_flag` to `yes` on the old row (the only field that may be touched), and list both in the gate package for the next G6. The old judgement stays validated and in use until the analyst decides.

## Change log

- 0.6 (6 Nov 2026): PC-19 to PC-23 approved at G8 of RUN-2026-02 (GATE-0030, G8-D01), applied before RUN-2026-03. Links from parallel batches merged before success and attribution are judged once per link (PC-19); one standard search scope for every claim of absence, computed by a tool (PC-20); priority test: a fulfilled Reform Agenda condition not repeated in the latest report does not alone make an issue High, and how the three-report tests apply with fewer than three standard reports (PC-21); implementation status `replaced`, with `reversed` kept for a measure withdrawn or repealed without a successor (PC-22); relevance of horizontal passages (PC-23).

- 0.5 (2 Nov 2026): PC-08 to PC-10 (GATE-0013), applied before RUN-2026-02 (E19). Final wording of reasons and a reason-value check before G6; searches behind claims of absence and no truncated inputs; helper briefs checked against the rules; each country judged on its own evidence.

- 0.4 (2 Nov 2026): approved at G6b (GATE-0011, G6b-D05 Option A). Transferability may also attach to a comparator case, one judgement per case, using the case's transferable and not-transferable statements as its conditions, labelled agent synthesis.
- 0.3 (30 Oct 2026): approved at G6 (GATE-0007). Priority test, legal progress, regional evidence and versions of one report added.
- 0.2 (29 Oct 2026): direction of travel distinguishes chapter-level from sub-area progress wording (rule issue R3, approved by the analyst).
- 0.1b (29 Oct 2026): pre-G0 reconfiguration of the pilot (decisions A5 to A9 and D6). Country-neutral wording; source quality per chapter or theme; direction of travel and priority for issues from cross-cutting themes.
- 0.1 (23 Oct 2026): first draft from the approved architecture.
