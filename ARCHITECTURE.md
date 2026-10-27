# EU Accession Reform Intelligence Tool: Agreed Architecture

Version 1.0, 23 October 2026. Agreed by Sofia after the architecture review of Codebooks 1 to 6. The full record of options and reasons is in `decisions/decision_log.md`.

## 1. What the tool does

The tool turns EU accession assessments into clear reform priorities and practical policy options. It extracts evidence from five families of sources, organises it around common reform issues, follows each issue along a ten-link analytical chain, and supports the analyst in judging what has happened, what remains and what could work. AI extracts, organises and proposes. The analyst makes the important judgements at fixed control gates.

The first run covers **Serbia, Chapter 5 (Public procurement)**, from 2014 to a fixed evidence freeze date. It has two parts: a Serbia diagnostic (run 1a) and a comparator pilot on two or three issues chosen by the analyst (run 1b).

## 2. Decisions at a glance

| ID | Decision | Agreed outcome |
|---|---|---|
| A1 | Comparators in run 1 | Run 1a Serbia diagnostic; run 1b comparator pilot on 2 to 3 analyst-selected issues, logged as a deliberate expansion |
| A2 | Thematic scope | Chapter 5 Public procurement only; Chapter 15 and a Chapter 23 sub-area deferred |
| A3 | Time window | 2014 to a fixed evidence freeze date; older material by logged exception |
| A4 | Language | English primary; Serbian only for core documents without English; machine translation flagged and capped at Medium confidence (no Serbian-speaking reviewer) |
| B1 | Chain and vocabulary | Ten-link chain; "finding/stated" for what a source says, "judgement/assessed" for what we conclude |
| B2 | Unit and record types | Evidence item = one claim, one type, exact quote and location; layers of sources, items, entities, links and judgements |
| B3 | Where judgements sit | Each judgement attaches to the object it describes; relevance and unresolved gap added |
| C1 | Finding sources | Requirements-led acquisition with analyst approval and a manual drop-in folder |
| C2 | Source register | One row per document ever considered, with status and reason; separate limits log |
| C3 | Folders and naming | `sources/<country>/<family>/originals` and `/text`; file name = source ID plus short label |
| C4 | Source quality | High, Medium, Low per source per topic from six factors; confidence and relevance rated separately; never merged |
| C5 | Civil society | Fifth source family, `CSO` |
| D1 | Formats | CSV for anything reviewed or edited; one JSON file per source for evidence items; spreadsheet exports at gates |
| D2 | Identifiers | Permanent, semi-readable IDs, never reused; reform issue IDs have no country code |
| D3 | Two passes | Extraction (close to the text) then classification (interpretive) |
| D4 | Taxonomy | Reform issues drafted from EU requirements and approved by the analyst; short fixed list of problem mechanisms |
| D5 | Matching fields | Controlled fields only; no free-text keywords |
| E1 | Sample | 10 to 12 documents across all families; three hand-coded passages; automatic quote check; at most two refinement loops |
| E2 | Gates | G0 to G8, all blocking; three tiers of AI authority |
| E3 | Future runs | Incremental, versioned runs; validated judgements never overwritten |
| E4 | Run 1 outputs | Internal analyst products; draft options only for run 1b issues; no dashboard yet; new Codebook 7 |

## 3. The analytical chain

1. **EU requirement:** what the EU finds, recommends or sets as a benchmark.
2. **Reform issue:** the common underlying problem behind the EU wording.
3. **Country response:** what the government has proposed, adopted or done.
4. **Implementation:** whether the response is applied in practice.
5. **Outcome:** what happened as a result.
6. **Unresolved gap:** what the EU asks for that has not been achieved.
7. **Comparator evidence:** how comparable countries dealt with the same issue.
8. **Lesson:** what worked, failed or mattered, and why.
9. **Priority:** how important the issue is and how realistic progress is.
10. **Policy option:** practical reform options, signed off by the reviewers.

## 4. Process flow

![Process flow](process_flow.png)

Amber diamonds are human control gates. The diagram source is `process_flow.dot`.

| Stage | What happens | AI does | Analyst does | Gate | Procedure |
|---|---|---|---|---|---|
| 0 Run setup | Fix scope, freeze date, reviewers, versions; build helper tools | Drafts run record, builds tools | Sets freeze date, approves | G0 | P1 |
| 1 Requirements | List the documents that should exist | Drafts the list from Codebook 2 | Edits and approves | G1 | P1 |
| 2 Acquire | Search, download, convert, record failures | All | Drops in files the agent cannot fetch | none | P1 |
| 3 Register | Register, de-duplicate, rate source quality, coverage note | All | none | none | P1 |
| 4 Source review | Confirm the source universe | Prepares review sheet | Adds, removes, confirms exclusions and ratings | G2 | P1 |
| 5 Sample | Extract 10 to 12 documents | Extracts, checks quotes | Hand-codes three passages first | none | P2 |
| 6 Extraction review | Find errors, refine rules | Compares, proposes rule changes | Reviews items, approves rules | G3 | P2 |
| 7 EU extraction and taxonomy | Extract EU sources, draft reform issues | Extracts, drafts issues and mechanisms | Edits and approves taxonomy | G4 | P2 |
| 8 Full extraction | Extract remaining sources | Extracts, checks quotes, prepares spot check | none | none | P2 |
| 9 Classify and link | Tag issues, mechanisms, entities, links | Classifies, queues doubtful cases | Resolves queues, approves new issues | G5 | P3 |
| 10 Assessment | First-cut judgements | Proposes all judgements with reasons | none | none | P3 |
| 11 Validation | Check tier 3 judgements, choose 1b issues | Prepares issue dossiers | Validates or overrides (Sofia and George) | G6 | P3 |
| 1b Comparator pilot | Small repeat of stages 1 to 11 for 2 to 3 issues | As above | As above | G1b, G2b, G5b, G6b | P4 |
| 12 Outputs | Write overview, briefs, reports, draft options | Drafts | Sign off (Sofia and George) | G7 | P5 |
| 13 Close | Run review and proposed changes | Drafts | Approves changes | G8 | P5 |
| 14 Next run | Incremental update | Reuses, updates, flags | Starts it | G0 onward | P5 |

## 5. Control gates and AI authority

Every gate is blocking and is recorded in `registers/gate_log.csv` with the date, reviewers, decision and any conditions.

| Tier | Meaning | Covers |
|---|---|---|
| 1. AI decides and logs | No review needed; the log can be checked | File naming and IDs, conversion, exact-duplicate detection, recording retrieval failures, quote verification, structural tags |
| 2. AI decides; analyst reviews in bulk or by exception | Goes ahead, surfaces at the next gate | Clear-cut exclusions, extraction once rules are approved, source quality, evidence confidence, relevance, uncontested implementation status |
| 3. AI proposes only; analyst decides | Nothing proceeds without a decision | Requirements list, judgement-based exclusions, taxonomy changes, ambiguous classification, comparator selection and relevance, direction of travel, unresolved gap, success, attribution, transferability, priority and tractability, policy options, codebook and scope changes |

Reviewers for run 1: Sofia at every gate; Sofia and George together at G6, G6b and G7.

## 6. Sources: acquisition, folders and register

**Five source families:** `EU` (formal EU and accession sources), `GOV` (national government), `IO` (international organisations), `RES` (think tanks, academic and specialist analysis), `CSO` (civil society and independent monitoring).

**Acquisition rules:**
- Search against an approved requirements list.
- Prefer official websites.
- Keep originals untouched, with a page-numbered text version alongside.
- Save webpages as dated snapshots.
- Flag text recognition and translation.
- Never bypass paywalls or logins.
- Register every failure.
- Accept manual drop-ins through `sources/_inbox/`.

**Folders:**

```
sources/SRB/<EU|GOV|IO|RES|CSO>/originals/   untouched originals
sources/SRB/<EU|GOV|IO|RES|CSO>/text/        converted text with page markers
sources/_inbox/                               files added by hand
```

**File names:** source ID plus a short label, for example `SRB-EU-2025-001_EC_Serbia-Report-2025.pdf`.

**Register:** one row per document ever considered, including inaccessible, excluded, duplicate and superseded ones. Fields: source ID, family, institution, author, title, document type, country, role, chapters, requirement ID, publication date, period covered, language, translation used, URL, retrieval date, local file, file format, file fingerprint, status, status reason, earlier version, run added, notes. Full definitions are in `schemas/data_dictionary.md`.

## 7. Data structure

| Layer | What it holds | Format and location |
|---|---|---|
| Sources | One row per document | `registers/source_register.csv` |
| Evidence items | One claim each, with quote and location | One JSON file per source in `evidence/<country>/` |
| Entities | Reform issues, mechanisms, interventions, actors, comparator cases; unmatched and ambiguous queues | CSV in `taxonomy/` and `entities/` |
| Links | Corroborates, contradicts, responds to, leads to, explains, lesson from, replaces, amends, same as earlier | `links/links.csv` |
| Judgements | Source quality, and every other judgement | CSV in `judgements/` |
| Logs | Requirements, limits, gate decisions | CSV in `registers/` |

**Identifiers:** `RUN-2026-01`, `REQ-012`, `SRB-EU-2025-001`, `SRB-EU-2025-001-0042`, `RI-PP-007`, `MEC-04`, `INT-SRB-0012`, `ACT-SRB-0003`, `CMP-0001`, `LNK-000123`, `JDG-000123`. IDs are permanent and never reused.

**Two passes:**
- Extraction records what the text says.
- Classification adds reform issues, mechanisms, entities and links.

A taxonomy change re-runs classification only.

## 8. Parsing

Seven information types are extracted as items: finding, recommendation, intervention, barrier, outcome, lesson and metric. Status, dates, actors and source reference are recorded on every item. Each item records:
- the three dates separately (publication, period covered, event);
- the speaker separately from the subjects;
- the stated status, for interventions;
- the Commission's standard preparation and progress wording, word for word, where it is used.

Every quote is checked automatically against the text. Full rules are in `rules/extraction_rules.md` (version 0.1, refined at G3).

## 9. Matching and lookups

Every evidence item carries:
- country and role;
- source;
- the three dates;
- cluster and chapter;
- information type and chain link;
- reform issues and mechanisms;
- interventions;
- speaker and subject actors.

All values come from controlled lists or IDs.

| Lookup | How it works |
|---|---|
| Country view (Serbia) | Filter on country `SRB` and role `target`, grouped by reform issue and chain link |
| Thematic view (for example public procurement) | Filter on chapter or cluster across all countries |
| Reform issue across countries | Filter on the country-neutral reform issue ID, and on mechanisms for near matches |
| Over time | Sort an issue's items by period covered and event date; follow `same_as_earlier` links between yearly reports |
| Along the chain | Follow `responds_to`, `leads_to`, `explains` and `lesson_from` links |
| Conflicting evidence | Follow `contradicts` links |

## 10. Assessment

| Judgement | Attached to | Scale | Tier |
|---|---|---|---|
| Source quality | Source, per topic | High, Medium, Low | 2 |
| Evidence confidence | Evidence item | High, Medium, Low | 2 |
| Relevance | Item, for a reform issue | High, Medium, Low | 2 |
| Implementation status | Intervention at a date | proposed, adopted, implemented, in practice, reversed, unclear | 2 or 3 |
| Direction of travel | Issue in a country | new, worsening, persistent, improving, largely resolved | 3 |
| Unresolved gap | Issue in a country | open, partly addressed, largely closed | 3 |
| Success | Intervention to outcome link | worked, failed, mixed, too early | 3 |
| Attribution | Intervention to outcome link | High, Medium, Low | 3 |
| Comparator relevance | Serbia issue and comparator case | High, Medium, Low | 3 |
| Transferability | Lesson, for Serbia | likely, conditional, unlikely | 3 |
| Priority, tractability | Issue in a country | High, Medium, Low each | 3 |

Every scale also allows "insufficient evidence". Every judgement records:
- its reason;
- the evidence it relies on;
- who made it;
- its review status;
- the versions used.

Validated or overridden judgements are never overwritten.

## 11. Limits and future runs

Active limits are recorded in `registers/limits_log.csv`. They cover:
- Serbia only, plus the run 1b comparators;
- Chapter 5 only;
- the 2014 start;
- the language rule;
- no dashboard in run 1.

Each run has a run record with its scope, freeze date, reviewers and versions. In a later run, the agent handles material as follows:
- documents with an unchanged fingerprint are reused;
- new documents are processed;
- updated versions are registered as new sources, with the old version kept as superseded;
- rule changes trigger targeted re-runs;
- validated judgements are flagged for re-review and never overwritten.

The run review at G8 turns lessons into approved changes and new codebook versions. The system never starts a new run or widens its scope on its own.

## 12. Changes to the codebooks

| Codebook | Main changes in version 1.1 |
|---|---|
| 1 Project explanation | Ten-link chain; finding versus judgement vocabulary; run 1 scope (Serbia, Chapter 5, runs 1a and 1b); human review principle; list of seven codebooks |
| 2 Sources | Fifth family (civil society); "evidence weight" renamed default guidance; register and evidence item fields separated; three-level ratings; requirements list; language rule |
| 3 Limits and log | Chapter 5 scope; comparator exception; time and language limits; register and limits log roles; future-run logic; no automatic expansion |
| 4 Data architecture | Evidence item defined; seven claim types and four details; three dates; speaker and subject; IDs; CSV and JSON; record layers; two passes; sample design; EU-first sequence |
| 5 Matching | Theme lookup through clusters and chapters; two-level taxonomy and its governance; controlled matching fields; full chain; corroborate and contradict links |
| 6 Assessment | Judgement vocabulary; object and scale for each judgement; relevance and unresolved gap added; six source quality factors; confidence and relevance criteria; judgement records; authority tiers |
| 7 Outputs (new) | Output principles; run 1 products; rules for policy options; format |

## 13. Project structure

```
eu-accession-tool/
  CLAUDE.md                  instructions every agent session reads first
  ARCHITECTURE.md            this document
  codebooks/                 Codebooks 1 to 7 (Markdown) and CHANGELOG.md
  procedures/                P1 to P5: step-by-step instructions per stage
  rules/                     extraction, classification and judgement rules (versioned)
  schemas/                   data dictionary, evidence JSON schema, example file
  registers/                 requirements, source register, limits log, gate log
  sources/                   _inbox/ and SRB/<family>/originals and text
  evidence/SRB/              one JSON file per source
  taxonomy/                  reform issues, mechanisms, unmatched queue
  entities/                  interventions, actors, comparator cases
  links/                     links between records
  judgements/                source quality and all other judgements
  review/RUN-2026-01/        spreadsheets prepared for each gate
  outputs/RUN-2026-01/       run outputs
  runs/RUN-2026-01/          run record and, at the end, run review
  decisions/                 architecture decision log
  tools/                     helper scripts (specified, built at stage 0)
```

## 14. Before the first session

- **Freeze date:** set at G0, just after this year's Commission enlargement package is published.
- **Helper tools:** specified in `tools/README.md` and built and tested at stage 0.
- **Version history:** the project folder should be a git repository, with a commit after every gate decision, so that every version of the rules, taxonomy and judgements can be recovered.
- **Mechanism list:** the ten mechanisms in `taxonomy/mechanisms.csv` are a draft for approval at G4.
