# Classification rules (pass 2)

Version 0.1, 23 October 2026. Status: draft, to be refined at gates G4 and G5. Changes create a new version and are listed in the change log at the end of this file.

Pass 2 adds the interpretive layer to evidence items that have passed pass 1. It implements Codebook 5. It never changes the pass 1 fields (quote, type, location, dates, stated status). If a pass 1 error is found, it is recorded in the review queue for correction under the extraction rules rather than silently fixed.

Pass 2 always runs against a specific, approved taxonomy version and mechanism list version, both recorded in the `classification` block of each evidence file. When the taxonomy changes, re-run pass 2 only on items tagged with, or queued against, the issues that changed, plus the unmatched queue.

## 1. Chain link

Assign one `chain_link` per item, using this table as the default and departing from it only with a `classification_note`.

| Information type | Default chain link | Notes |
|---|---|---|
| `finding` (EU source) | `eu_requirement` | Includes EU statements of the gap, which also feed the unresolved gap judgement |
| `recommendation` (EU source) | `eu_requirement` | Benchmarks and expectations |
| `finding` (other sources) | `implementation` or `unresolved_gap` | `implementation` if it concerns how a named intervention is applied; otherwise `unresolved_gap` |
| `recommendation` (other sources) | `unresolved_gap` | Records what others think is still missing |
| `intervention` | `country_response` |  |
| `barrier` | `unresolved_gap` | Explains why the gap persists |
| `outcome` | `outcome` |  |
| `metric` | `implementation` or `outcome` | `outcome` only if the source links it to a named intervention |
| `lesson` | `lesson` |  |
| any item with role `comparator` | `comparator_evidence` | Also keep the link the item would have had for its own country in `classification_note` |

## 2. Reform issues

- Assign between one and three `reform_issue_ids`, listing the best fit first.
- Assign only issues with status `approved` in the current taxonomy version.
- If no approved issue fits, set `classification_status` to `queued_unmatched` and add a row to `taxonomy/unmatched_queue.csv` with a proposed label and definition. Never add an issue to the taxonomy directly.
- If two or more issues fit equally well and the choice matters for the analysis, set `classification_status` to `queued_ambiguous` and add a row to `taxonomy/ambiguous_queue.csv` for gate G5.
- Use the issue definitions and exclusion notes in the taxonomy, not the issue labels alone.

## 3. Problem mechanisms

- Assign between zero and three `mechanism_ids` from `taxonomy/mechanisms.csv`.
- Assign a mechanism only when the item itself, or a barrier item linked to it, gives support for it. An EU finding that "limited progress was made" supports no mechanism on its own.

## 4. Interventions and actors

- Link each intervention named in an item to a record in `entities/interventions.csv`. Create a new record if none exists, using the next free ID.
- Treat different names for the same measure as one intervention (for example an English title and a Serbian title for the same law). Record the alternative names in the intervention record.
- Treat amended or replaced laws as separate interventions, linked with a `replaces` or `amends` link.
- Link speakers and subjects to `entities/actors.csv` in the same way. Record ministries under their current name and list former names, so that renamed institutions are not duplicated.

## 5. Links between items

Create links in `links/links.csv` only where the connection is clear from the evidence.

| Link type | From | To | Create when |
|---|---|---|---|
| `corroborates` | item | item | Two independent sources state the same fact or judgement |
| `contradicts` | item | item | Two sources make claims that cannot both be true |
| `responds_to` | intervention | EU requirement item or reform issue | The source states, or the dates and content clearly show, that the intervention addresses the requirement |
| `leads_to` | intervention | outcome item | A source links the outcome to the intervention |
| `explains` | barrier item | reform issue | The barrier is given as a reason for the issue persisting |
| `lesson_from` | lesson item | intervention or comparator case | The lesson is drawn from that experience |
| `replaces`, `amends` | intervention | intervention | Legal succession |
| `same_as_earlier` | item | item | The same EU wording repeats from an earlier report |

Two items from the same source never corroborate each other. A government source and a government statistic do not count as independent of each other.

## 6. Queues for the analyst

Every item starts with `classification_status` `not_classified` (set in pass 1) and ends pass 2 with one of:

- `auto`: classified with no doubts.
- `queued_ambiguous`: waiting for the analyst at G5.
- `queued_unmatched`: no approved issue fits; waiting for a taxonomy decision.
- `analyst_resolved`: decided by the analyst, who is recorded in the gate log.

## Change log

- 0.1 (23 Oct 2026): first draft from the approved architecture.
