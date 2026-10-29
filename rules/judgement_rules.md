# Judgement rules

Version 0.2, 29 October 2026. Status: draft, to be refined at gate G6. Changes create a new version and are listed in the change log at the end of this file.

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
| Implementation status | `intervention` at a date | proposed / adopted / implemented / in_practice / reversed / unclear | 2 if sources agree; 3 if they conflict |
| Direction of travel | `issue_country` | new / worsening / persistent / improving / largely_resolved | 3: analyst decides at G6 |
| Unresolved gap | `issue_country` | open / partly_addressed / largely_closed | 3 |
| Success or result | `link` (intervention to outcome) | worked / failed / mixed / too_early | 3 |
| Attribution | `link` (intervention to outcome) | High / Medium / Low | 3 |
| Comparator relevance | `issue_comparator` (object ID is the comparator case) | High / Medium / Low | 3 |
| Transferability | `item` (lesson) for the target country | likely / conditional / unlikely | 3 |
| Priority | `issue_country` | High / Medium / Low | 3 |
| Tractability | `issue_country` | High / Medium / Low | 3 |

Every scale also allows `insufficient_evidence`. Use it rather than force a value.

## 3. Operational rules

- **Source quality:** fill in the six factor columns first (yes, partly, no or not applicable; primary or secondary), then the overall value. A source can have different ratings for different chapters or themes.
- **Evidence confidence:** apply the Codebook 6 criteria. Cap at Medium if `machine_translated` is true. Lower by one level if the item is flagged `hedged` or `ocr`, unless the claim is corroborated.
- **Direction of travel:** base it on the sequence of EU standard-scale wording across years (`preparation_level`, `progress_level`) first, then on independent evidence. Cite the items for each year used. If the Commission wording is unchanged for three or more reports, the default is `persistent`. Use only wording with `eu_scale.applies_to` `chapter` for a chapter-wide issue; use `sub_area` wording only for an issue that matches that sub-area, and say so in the reason. The standard scale rates a whole chapter. For an issue that comes from a cross-cutting theme, or that is only part of a chapter, use the chapter's scale as context only: base the judgement on the issue's own items (repeated or changed recommendations and findings) and say in the reason that the scale was not decisive.
- **Unresolved gap:** compare the latest EU requirement items for the issue with the implementation status of the interventions that respond to them. At stage 10 these statuses are still proposals, so say so in the reason; the reviewers check both together at G6. Describe in one sentence what remains.
- **Success and attribution:** only judge an outcome that has a `leads_to` link. Never judge success from government reporting alone (Codebook 2).
- **Priority:** consider whether the issue appears in EU benchmarks or repeated key recommendations, and how central it is to the chapter or theme. **Tractability:** consider the mechanisms involved, the actors needed and evidence of past progress.
- **Conflicting evidence:** when items contradict each other, say so in the reason and cite both sides. Do not resolve a conflict by choosing the higher-quality source without saying so.

## 4. Re-runs

- Never change the value, reason or `review_status` of a judgement that is `validated` or `overridden`.
- If new evidence or a new rules version would change such a judgement, add a new proposed row whose `supersedes` field names the old judgement, set `rereview_flag` to `yes` on the old row (the only field that may be touched), and list both in the gate package for the next G6. The old judgement stays validated and in use until the analyst decides.

## Change log

- 0.2 (29 Oct 2026): direction of travel distinguishes chapter-level from sub-area progress wording (rule issue R3, approved by the analyst).
- 0.1b (29 Oct 2026): pre-G0 reconfiguration of the pilot (decisions A5 to A9 and D6). Country-neutral wording; source quality per chapter or theme; direction of travel and priority for issues from cross-cutting themes.
- 0.1 (23 Oct 2026): first draft from the approved architecture.
