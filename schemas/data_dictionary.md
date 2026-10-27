# Data dictionary

Version 1.0a, 23 October 2026 (consistency fixes before first use). This file defines every table and field in the project. The CSV templates in the project contain exactly these columns, in this order. Changing a column is a codebook change and must be approved at a gate.

General rules:

- CSV files are UTF-8, comma-separated, with a header row. Lists inside a cell are separated by a semicolon and no space, for example `ACT-SRB-0001;ACT-SRB-0004`.
- Dates use `YYYY-MM-DD`, or `YYYY-MM` or `YYYY` when only that precision is known. A period is written as `start/end`, for example `2024-06/2025-06`.
- Chapters are written as two-digit codes in quotes in JSON and as plain two-digit codes in CSV, for example `05`, `15`, `23`. Lists of chapters are semicolon-separated.
- Country codes use three letters (`SRB`, `MNE`, `MKD`, `ALB`, `BIH`, `XKX` and so on). EU institutions use `EU`.
- IDs are permanent. They are never changed, reused or deleted, even if the record is later excluded or retired.

## Identifier formats

| Record | Format | Example |
|---|---|---|
| Run | `RUN-YYYY-NN` | `RUN-2026-01` |
| Source requirement | `REQ-NNN` | `REQ-012` |
| Source | `CCC-FAM-YYYY-NNN` (country, family, publication year, sequence) | `SRB-EU-2025-001` |
| Evidence item | source ID plus `-NNNN` | `SRB-EU-2025-001-0042` |
| Reform issue | `RI-AREA-NNN` (area code, no country) | `RI-PP-007` |
| Problem mechanism | `MEC-NN` | `MEC-04` |
| Intervention | `INT-CCC-NNNN` | `INT-SRB-0012` |
| Actor | `ACT-CCC-NNNN` or `ACT-EU-NNNN` or `ACT-INT-NNNN` | `ACT-SRB-0003` |
| Comparator case | `CMP-NNNN` | `CMP-0001` |
| Link | `LNK-NNNNNN` | `LNK-000123` |
| Judgement | `JDG-NNNNNN` | `JDG-000123` |
| Source quality rating | `SQ-NNNNN` | `SQ-00045` |
| Limit | `LIM-NNNN` | `LIM-0003` |
| Gate decision | `GATE-NNNN` | `GATE-0001` |

Family codes: `EU`, `GOV`, `IO`, `RES`, `CSO`. Area codes for reform issues are set when the taxonomy is drafted; public procurement uses `PP`.

## registers/source_requirements.csv

| Field | Meaning |
|---|---|
| requirement_id | `REQ-NNN` |
| source_family | `EU`, `GOV`, `IO`, `RES` or `CSO` |
| document_type | For example annual report, screening report, benchmark, law, strategy, implementation report, monitoring report, evaluation |
| issuing_institution | Who is expected to publish it |
| description | What is being looked for, in one sentence |
| country | Country code |
| role | `target` or `comparator` |
| chapters | Chapter numbers, semicolon-separated |
| years_from | First year wanted |
| years_to | Last year wanted |
| core_or_supporting | `core` or `supporting` |
| search_hints | Official website, likely titles, Serbian title if relevant |
| status | `open`, `found`, `partly_found`, `not_found`, `not_public` |
| matched_source_ids | Sources that satisfy this requirement |
| approved_at | Gate decision ID that approved the line |
| notes | Free text |

## registers/source_register.csv

| Field | Meaning |
|---|---|
| source_id | Permanent source ID |
| source_family | `EU`, `GOV`, `IO`, `RES` or `CSO` |
| institution | Issuing institution |
| author | Named author, if any |
| title | Title as printed (English, or original with English in notes) |
| document_type | As in the requirements list |
| country | Country code of the country the document is about |
| role | `target` or `comparator` |
| chapters_covered | Chapters, semicolon-separated |
| requirement_id | Requirement it satisfies (blank if found outside the list) |
| publication_date | Date of publication |
| period_covered | Period the document reports on |
| language | `en`, `sr` or other |
| translation_used | `yes` or `no` |
| url | Where it was retrieved |
| retrieval_date | Date retrieved |
| local_file | Path of the original file |
| file_format | `pdf`, `html`, `docx`, `xlsx` and so on |
| content_hash | SHA-256 fingerprint of the original file |
| status | `available`, `inaccessible`, `excluded`, `duplicate`, `superseded` |
| status_reason | Reason, using the Codebook 3 categories where possible |
| version_of | Source ID of the earlier version this one updates |
| added_in_run | Run ID |
| notes | Free text |

## registers/limits_log.csv

| Field | Meaning |
|---|---|
| limit_id | `LIM-NNNN` |
| run_id | Run in which it was recorded |
| limit_type | `country`, `thematic`, `time`, `evidence`, `accessibility`, `language`, `analytical`, `methodological` |
| description | What is limited or excluded |
| applies_to | `all`, or a typed reference: `chapter:15`, `requirement:REQ-012`, `source:SRB-EU-2025-001`, `country:MNE` |
| reason | Why |
| temporary_or_permanent | `temporary` or `permanent` |
| decided_by | Name, or `agent` for tier 1 or 2 decisions |
| decided_on | Date |
| gate_id | Gate decision that confirmed it |
| revisit_in | Run or condition for revisiting |
| status | `active`, `lifted` |

## registers/gate_log.csv

| Field | Meaning |
|---|---|
| gate_decision_id | `GATE-NNNN` |
| run_id | Run |
| gate | `G0` to `G8`, or `G1b`, `G2b`, `G5b`, `G6b` for the run 1b comparator pilot |
| date | Date of decision |
| reviewers | Names, semicolon-separated |
| decision | `pass`, `pass_with_conditions`, `fail` |
| conditions | Conditions attached to a pass |
| files_reviewed | Review sheets and files presented |
| linked_changes | Rules, taxonomy or codebook versions created as a result |
| notes | Free text |

## taxonomy/reform_issues.csv

| Field | Meaning |
|---|---|
| issue_id | `RI-AREA-NNN` |
| label | Short name |
| definition | One or two sentences |
| cluster | Cluster number |
| chapters | Chapters, semicolon-separated |
| mechanism_ids | Usual mechanisms, semicolon-separated |
| example_item_ids | Two or three evidence items that illustrate it |
| exclusion_notes | What does not belong here |
| status | `draft`, `approved`, `merged`, `retired` |
| merged_into | Issue ID if merged |
| taxonomy_version | Version in which the row last changed |
| created_in_run | Run ID |
| notes | Free text |

## taxonomy/mechanisms.csv

| Field | Meaning |
|---|---|
| mechanism_id | `MEC-NN` |
| label | Short name |
| definition | One sentence |
| examples | Short examples |
| status | `draft`, `approved`, `retired` |
| version | Version in which the row last changed |

## taxonomy/unmatched_queue.csv

| Field | Meaning |
|---|---|
| queue_id | Running number |
| item_id | Evidence item that fits no issue |
| proposed_label | Agent's suggested issue label |
| proposed_definition | Agent's suggested definition |
| similar_issue_ids | Nearest existing issues |
| status | `open`, `added`, `mapped_to_existing`, `rejected` |
| resolution | What the analyst decided |
| gate_id | Gate decision |

## taxonomy/ambiguous_queue.csv

| Field | Meaning |
|---|---|
| queue_id | Running number |
| item_id | Evidence item that fits two or more issues equally well |
| candidate_issue_ids | The issues that fit, semicolon-separated |
| agent_reasoning | One or two sentences on why the choice is unclear |
| status | `open`, `resolved` |
| resolution | Issues assigned by the analyst |
| gate_id | Gate decision |

## entities/interventions.csv

| Field | Meaning |
|---|---|
| intervention_id | `INT-CCC-NNNN` |
| country | Country code |
| name | English name |
| name_original | Name in the original language |
| other_names | Alternative names, semicolon-separated |
| intervention_type | `law`, `secondary_legislation`, `strategy`, `action_plan`, `institutional_change`, `programme`, `it_system`, `other` |
| responsible_actor_ids | Actors, semicolon-separated |
| chapters | Chapters |
| stated_adoption_date | Adoption date as stated by a source |
| first_item_id | First evidence item that mentions it |
| notes | Free text |

## entities/actors.csv

| Field | Meaning |
|---|---|
| actor_id | Actor ID |
| name | Current English name |
| name_original | Name in the original language |
| former_names | Earlier names, semicolon-separated |
| acronym | Acronym |
| country | Country code, `EU` or `INT` |
| actor_type | `eu_institution`, `government`, `independent_body`, `parliament`, `judiciary`, `international_org`, `cso`, `research`, `private`, `other` |
| parent_actor_id | Parent body, if any |
| notes | Free text |

## entities/comparator_cases.csv

| Field | Meaning |
|---|---|
| case_id | `CMP-NNNN` |
| country | Comparator country code |
| reform_issue_id | Serbia reform issue it is compared with |
| intervention_ids | Comparator interventions involved |
| description | One or two sentences |
| selected_at | Gate decision that selected it |
| notes | Free text |

## links/links.csv

| Field | Meaning |
|---|---|
| link_id | `LNK-NNNNNN` |
| from_id | Record the link starts from |
| to_id | Record the link points to |
| link_type | `corroborates`, `contradicts`, `responds_to`, `leads_to`, `explains`, `lesson_from`, `replaces`, `amends`, `same_as_earlier` |
| basis | One sentence on why the link exists |
| created_by | `agent` or a name |
| review_status | `proposed`, `validated`, `rejected` |
| run_id | Run |
| rules_version | Classification rules version |

## judgements/source_quality.csv

| Field | Meaning |
|---|---|
| sq_id | `SQ-NNNNN` |
| source_id | Source |
| topic | Chapter or topic the rating applies to |
| traceability | `yes`, `partly`, `no` |
| topic_expertise | `yes`, `partly`, `no` |
| method_transparency | `yes`, `partly`, `no`, `na` |
| primary_or_secondary | `primary`, `secondary`, `mixed` |
| independence | `yes`, `partly`, `no` |
| recency | `yes`, `partly`, `no`, `na` |
| overall | `High`, `Medium`, `Low`, `insufficient_evidence` |
| reason | One line |
| made_by | `agent` or a name |
| review_status | `proposed`, `validated`, `overridden` |
| rereview_flag | `yes` if new evidence or rules may change a validated or overridden rating; otherwise blank |
| reviewer | Name |
| review_date | Date |
| override_reason | Why the analyst changed it |
| codebook_version | Codebook version used |
| rules_version | Judgement rules version |
| run_id | Run |

## judgements/judgements.csv

| Field | Meaning |
|---|---|
| judgement_id | `JDG-NNNNNN` |
| judgement_type | `evidence_confidence`, `relevance`, `implementation_status`, `direction_of_travel`, `unresolved_gap`, `success`, `attribution`, `comparator_relevance`, `transferability`, `priority`, `tractability` |
| object_type | `item`, `intervention`, `issue_country`, `link`, `issue_comparator` |
| object_id | ID of the object: an item, intervention or link ID; for `issue_country`, the issue and country written as `RI-PP-007@SRB`; for `issue_comparator`, the comparator case ID (`CMP-NNNN`), which already names the Serbia issue |
| context_id | Extra context, for example the reform issue for a relevance judgement, or the date for implementation status |
| value | Value from the allowed scale in the judgement rules, or `insufficient_evidence` |
| reason | One to three sentences |
| evidence_item_ids | Items relied on, semicolon-separated |
| made_by | `agent` or a name |
| review_status | `proposed`, `validated`, `overridden` |
| rereview_flag | `yes` if new evidence or rules may change a validated or overridden judgement; otherwise blank |
| reviewer | Name |
| review_date | Date |
| override_reason | Why the analyst changed it |
| supersedes | Judgement ID this one would replace |
| codebook_version | Codebook version |
| rules_version | Judgement rules version |
| taxonomy_version | Taxonomy version in force when the judgement was made |
| run_id | Run |

## evidence/<country>/<source_id>.json

One file per source. The structure is defined in `schemas/evidence_item.schema.json`. In plain terms, each file has a header describing the source and how it was processed, followed by a list of evidence items. Each item holds the pass 1 fields described in the extraction rules and a `pass2` block filled in by classification.
