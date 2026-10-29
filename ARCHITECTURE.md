# EU Accession Reform Intelligence Tool: Agreed Architecture

Version 1.1, 29 October 2026. Version 1.0 was agreed by Sofia on 23 October 2026 after the architecture review of Codebooks 1 to 6. Version 1.1 records the pre-G0 reconfiguration of the pilot (decisions A5 to A9, D6, E5 and F2) and the alpha set-up (decisions E6 to E9). The full record of options and reasons is in `decisions/decision_log.md`.

## 1. What the tool does

The tool turns EU accession assessments into clear reform priorities and practical policy options. It extracts evidence from five families of sources, organises it around common reform issues, follows each issue along a ten-link analytical chain, and supports the analyst in judging what has happened, what remains and what could work. AI extracts, organises and proposes. The analyst makes the important judgements at fixed control gates.

The first run covers **North Macedonia: all of Chapter 2 (Freedom of movement for workers), plus recommendations materially relating to technology and AI wherever they occur**, from 1 January 2020 to a fixed evidence freeze date. The full analytical chain is followed for every issue that originates from this material. The run has two parts: a North Macedonia diagnostic (run 1a) and a comparator pilot on two or three issues chosen by the analyst (run 1b). Run-specific settings are kept in the run record; the codebooks, procedures and rules are country-neutral. Until 29 October 2026, before gate G0, the first run was configured for Serbia, Chapter 5 (Public procurement).

RUN-2026-01 is an **alpha product and methodology test**. Besides the analysis, it tests the end-to-end workflow, source collection and processing, extraction and classification, taxonomy and matching, the human review gates, assessment and judgement, the outputs, and the usefulness of a single review page (`index.html`). Material lessons are kept in an alpha learning log and inform scaling to further chapters, clusters and countries.

## 2. Decisions at a glance

| ID | Decision | Agreed outcome |
|---|---|---|
| A1, A5 | Pilot country and comparators in run 1 | Run 1a North Macedonia diagnostic; run 1b comparator pilot on 2 to 3 analyst-selected issues, logged as a deliberate expansion |
| A6, A9 | Thematic scope | All of Chapter 2 plus the technology and AI theme (recommendations materially relating to it, wherever they occur); full chain for issues originating there; other material only where needed to follow that chain; no deferred-chapter list |
| A7 | Time window | 1 January 2020 to a fixed evidence freeze date; older material by logged exception |
| A8 | Language | English primary; Macedonian or Albanian only for core sources without a suitable English version; machine translation flagged and capped at Medium confidence |
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
| D5, D6 | Matching fields | Controlled fields only; no free-text keywords; cross-cutting themes as a controlled list of theme codes, with a scope basis on every item |
| E1 | Sample | 10 to 12 documents across all families; three hand-coded passages; automatic quote check; at most two refinement loops |
| E2 | Gates | G0 to G8, all blocking; three tiers of AI authority |
| E3 | Future runs | Incremental, versioned runs; validated judgements never overwritten |
| E4, E7 | Run 1 outputs | Internal analyst products; draft options only for run 1b issues; no interactive dashboard yet; new Codebook 7; a single static review page with status labels |
| E5 | Pilot reconfiguration | RUN-2026-01 kept; scope changed before G0; earlier limits marked superseded |
| E6 | Alpha | Run 1 is an alpha product and methodology test |
| E8 | Alpha learning log | Curated lessons in `runs/RUN-2026-01/alpha_learning_log.csv`; `run_notes.md` stays the raw diary |
| E9 | George's role | Alpha reviewer of the product and review page throughout; formal gate roles unchanged |
| F2 | Country neutrality | Codebooks, procedures and rules are country-neutral; run-specific settings sit in the run record, CLAUDE.md and the limits log |

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

Around every gate, the agent proposes alpha learning log rows in the gate package and rebuilds the review page; after the decision it updates the log statuses, rebuilds the page and offers a commit (procedure P1, "Around every gate").

Known gap (29 Oct 2026): `process_flow.png` and `process_flow.dot` are not in the repository. This is recorded as a non-blocking documentation gap; the stage table below is the authoritative description of the process.

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

Reviewers for run 1: Sofia at every gate; Sofia and George together at G6, G6b and G7. George is also an alpha reviewer of the developing product and the review page throughout the run; this is not a formal gate role.

**Review page.** `index.html` in the repository root is the human-facing review interface. It shows validated material and work in progress, labelled `Validated`, `Pending review`, `Proposed`, `Draft` or `Not started`. It is generated from the project files by `tools/build_review_page.py` and is never the place where a gate decision is made.

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
sources/<country>/<EU|GOV|IO|RES|CSO>/originals/   untouched originals
sources/<country>/<EU|GOV|IO|RES|CSO>/text/        converted text with page markers
sources/_inbox/                                     files added by hand
```

**File names:** source ID plus a short label, for example `MKD-EU-2025-001_EC_North-Macedonia-Report-2025.pdf` in run 1.

**Register:** one row per document ever considered, including inaccessible, excluded, duplicate and superseded ones. Fields: source ID, family, institution, author, title, document type, country, role, chapters, themes, requirement ID, publication date, period covered, language, translation used, URL, retrieval date, local file, file format, file fingerprint, status, status reason, earlier version, run added, notes. Full definitions are in `schemas/data_dictionary.md`.

## 7. Data structure

| Layer | What it holds | Format and location |
|---|---|---|
| Sources | One row per document | `registers/source_register.csv` |
| Evidence items | One claim each, with quote and location | One JSON file per source in `evidence/<country>/` |
| Entities | Reform issues, mechanisms, cross-cutting themes, interventions, actors, comparator cases; unmatched and ambiguous queues | CSV in `taxonomy/` and `entities/` |
| Links | Corroborates, contradicts, responds to, leads to, explains, lesson from, replaces, amends, same as earlier | `links/links.csv` |
| Judgements | Source quality, and every other judgement | CSV in `judgements/` |
| Logs | Requirements, limits, gate decisions | CSV in `registers/` |

**Identifiers:** `RUN-2026-01`, `REQ-012`, `MKD-EU-2025-001`, `MKD-EU-2025-001-0042`, `RI-FMW-007`, `MEC-04`, `TECH-AI`, `INT-MKD-0012`, `ACT-MKD-0003`, `CMP-0001`, `LNK-000123`, `JDG-000123`. IDs are permanent and never reused.

**Two passes:**
- Extraction records what the text says, and why each item is in scope (chapter, theme or chain).
- Classification adds reform issues, mechanisms, entities and links, and confirms that theme and chain items belong to an in-scope issue.

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
- cluster, chapter and theme;
- information type and chain link;
- reform issues and mechanisms;
- interventions;
- speaker and subject actors.

All values come from controlled lists or IDs.

| Lookup | How it works |
|---|---|
| Country view (for example North Macedonia) | Filter on the country code (`MKD`) and role `target`, grouped by reform issue and chain link |
| Thematic view (for example Chapter 2, or technology and AI) | Filter on chapter, cluster or theme code across all countries |
| Reform issue across countries | Filter on the country-neutral reform issue ID, and on mechanisms for near matches |
| Over time | Sort an issue's items by period covered and event date; follow `same_as_earlier` links between yearly reports |
| Along the chain | Follow `responds_to`, `leads_to`, `explains` and `lesson_from` links |
| Conflicting evidence | Follow `contradicts` links |

## 10. Assessment

| Judgement | Attached to | Scale | Tier |
|---|---|---|---|
| Source quality | Source, per chapter or theme | High, Medium, Low | 2 |
| Evidence confidence | Evidence item | High, Medium, Low | 2 |
| Relevance | Item, for a reform issue | High, Medium, Low | 2 |
| Implementation status | Intervention at a date | proposed, adopted, implemented, in practice, reversed, unclear | 2 or 3 |
| Direction of travel | Issue in a country | new, worsening, persistent, improving, largely resolved | 3 |
| Unresolved gap | Issue in a country | open, partly addressed, largely closed | 3 |
| Success | Intervention to outcome link | worked, failed, mixed, too early | 3 |
| Attribution | Intervention to outcome link | High, Medium, Low | 3 |
| Comparator relevance | Target-country issue and comparator case | High, Medium, Low | 3 |
| Transferability | Lesson, for the target country | likely, conditional, unlikely | 3 |
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
- North Macedonia only, plus the run 1b comparators;
- Chapter 2 plus the technology and AI theme, with other material only where needed to follow the chain of an in-scope issue;
- the 1 January 2020 start;
- the language rule;
- no interactive dashboard in run 1; a single static review page only.

LIM-0001 to LIM-0006 recorded the earlier Serbia configuration, and LIM-0007 the earlier no-dashboard rule; all are marked superseded.

Each run has a run record with its scope, freeze date, reviewers and versions. In a later run, the agent handles material as follows:
- documents with an unchanged fingerprint are reused;
- new documents are processed;
- updated versions are registered as new sources, with the old version kept as superseded;
- rule changes trigger targeted re-runs;
- validated judgements are flagged for re-review and never overwritten.

The run review at G8 turns lessons into approved changes and new codebook versions. The system never starts a new run or widens its scope on its own.

## 12. Changes to the codebooks

Version 1.2 of Codebooks 1 to 6 and version 1.1 of Codebook 7 (29 October 2026) made them country-neutral and added cross-cutting themes; see `codebooks/CHANGELOG.md`. The table below records the version 1.1 changes agreed after the architecture review.

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
  index.html                 review page (generated; hosted on GitHub Pages)
  analysis.html              analysis mock-up linked from the review page (generated; decision E11)
  CLAUDE.md                  instructions every agent session reads first
  ARCHITECTURE.md            this document
  codebooks/                 Codebooks 1 to 7 (Markdown) and CHANGELOG.md
  procedures/                P1 to P5: step-by-step instructions per stage
  rules/                     extraction, classification and judgement rules (versioned)
  schemas/                   data dictionary, evidence JSON schema, example file
  registers/                 requirements, source register, limits log, gate log
  sources/                   _inbox/ and <country>/<family>/originals and text (MKD in run 1)
  evidence/<country>/        one JSON file per source (MKD in run 1)
  taxonomy/                  reform issues, mechanisms, themes, unmatched and ambiguous queues
  entities/                  interventions, actors, comparator cases
  links/                     links between records
  judgements/                source quality and all other judgements
  review/RUN-2026-01/        spreadsheets prepared for each gate
  outputs/RUN-2026-01/       run outputs
  runs/RUN-2026-01/          run record, run notes, alpha learning log and, at the end, run review
  decisions/                 architecture decision log
  tools/                     helper scripts (specified, built at stage 0)
```

## 14. Before the first session

- **Freeze date:** set at G0, just after this year's Commission enlargement package is published.
- **Helper tools:** specified in `tools/README.md` and built and tested at stage 0.
- **Version history:** the project folder should be a git repository, with a commit after every gate decision, so that every version of the rules, taxonomy and judgements can be recovered.
- **Mechanism list:** the ten mechanisms in `taxonomy/mechanisms.csv` are a draft for approval at G4.
- **Theme list:** the technology and AI theme areas in `taxonomy/themes.csv` were approved by Sofia on 29 October 2026 and are confirmed at G0.
