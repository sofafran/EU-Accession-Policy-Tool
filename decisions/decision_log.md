# EU Accession Reform Intelligence Tool: Architecture Decision Log

Purpose: record of the architecture decisions taken before building the tool in Claude Code.

Inputs reviewed: Codebooks 1 to 6 (versions dated 20 Oct 2026).

Status key: Open | Proposed | Approved | Modified (approved with changes) | Rejected

Overall status (23 Oct 2026): **architecture confirmed by Sofia.** All decisions approved. Final package prepared: ARCHITECTURE.md, CLAUDE.md, procedures, rules, schemas, templates, Codebooks 1 to 6 version 1.1 and new Codebook 7.

## Decision register

| ID | Group | Decision | Status | Outcome |
|---|---|---|---|---|
| A1 | Scope | How comparator countries are handled in run 1 | Approved | Run 1 split: 1a Serbia diagnostic; 1b comparator pilot on 2 to 3 analyst-selected issues, comparator evidence tagged as such, expansion logged as deliberate |
| A2 | Scope | Thematic scope of run 1 | Modified | One chapter for run 1: Chapter 5 Public procurement. Chapter 15 Energy and a Chapter 23 sub-area deferred; expand only after run 1 is tested |
| A3 | Scope | Time window and evidence freeze date | Approved | Evidence from 2014 onward; fixed freeze date just after this year's Commission enlargement package (set at G0); older documents by logged exception only |
| A4 | Scope | Language policy | Approved | English primary; Serbian only for core documents with no English version; original quote plus flagged machine translation; no Serbian-speaking reviewer available, so machine-translated evidence is capped at Medium confidence and listed in the limits report |
| B1 | Concepts | One canonical analytical chain and shared vocabulary | Approved | Ten-link chain: EU requirement, reform issue, country response, implementation, outcome, unresolved gap, comparator evidence, lesson, priority, policy option. "Finding/stated" = what a source says; "judgement/assessed" = what we conclude |
| B2 | Concepts | Unit of analysis and record types | Approved | Evidence item = one claim, one information type, exact quote and location, with separate speaker and subject actors. Layered records: sources, evidence items, analytical entities, links (incl. corroborates/contradicts), judgements |
| B3 | Concepts | Which object each judgement attaches to | Approved | Each judgement attaches to the object it describes. Adds relevance and unresolved gap. Each judgement records value, reason, cited evidence items, made by, review status, codebook version |
| C1 | Sources | How the agent discovers and acquires documents | Approved | Requirements-led acquisition, analyst approval at G1, official domains preferred, originals plus page-numbered text, webpage snapshots, OCR and translation flagged, no bypassing of paywalls or logins, every failure logged, manual drop-in folder |
| C2 | Sources | Master source register fields | Approved | Every document ever considered, with status and reason (full field list in schemas/data_dictionary.md). Separate limits log for scope-level limits |
| C3 | Sources | Folder structure and naming rules | Approved | sources/<country>/<family>/originals and /text; file name = source ID plus short label, no spaces |
| C4 | Sources | Source quality method; confidence and relevance | Approved | Source quality per source per topic, High/Medium/Low from six factors plus one-line reason. Confidence and relevance on the same levels with own criteria. Never merged. AI proposes; analyst reviews by exception at G2 |
| C5 | Sources | Civil society monitoring as a fifth source family | Approved | New family CSO with its own use, limits and default guidance |
| D1 | Data | CSV, JSON or a combination | Approved | CSV for anything reviewed or edited; JSON for evidence items, one file per source; spreadsheet exports at gates; any database rebuilt from files |
| D2 | Data | Identifier scheme | Approved | Permanent semi-readable IDs, never reused or changed; reform issue IDs country-neutral |
| D3 | Data | Extraction and classification as separate passes | Approved | Pass 1 extraction; pass 2 classification; taxonomy changes re-run pass 2 only |
| D4 | Data | Taxonomy and problem mechanisms | Approved | Hybrid, two levels; agent proposes, analyst approves; versioned; retired IDs never reused |
| D5 | Data | Minimum set of matching fields | Approved | Controlled fields on every item; no free-text keywords; cross-chapter themes deferred |
| E1 | Process | Sample parse and review | Approved | 10 to 12 documents across five families; three hand-coded passages; automatic quote check; checklist; max two refinement loops; EU family first, then taxonomy, then the rest |
| E2 | Process | Control gates; AI authority | Approved | Gates G0 to G8, all blocking, gate log; three tiers of authority. Reviewers: Sofia at all gates; Sofia and George at G6, G6b and G7 |
| E3 | Process | Future runs and versioning | Approved | Incremental versioned runs; unchanged sources reused; updates kept as versions; targeted re-runs; validated judgements never overwritten; G8 run review feeds codebook changes |
| E4 | Process | What run 1 produces | Approved | Internal analyst products; draft policy options only for run 1b issues; no dashboard in run 1; new Codebook 7 (Outputs) |
| F1 | Package | Format of revised codebooks | Approved | Markdown copies in the Claude Code folder (followed by agents) plus Word copies with tracked changes against the 20 Oct originals for human review; Codebook 7 in both forms |

## Points added while preparing the package (for review)

- Of Codebook 4's eleven information types, seven are extracted as claim types and four (status, date, actor, source reference) are recorded as details on every item. This follows from B2.
- Where Codebook 6 already named categories (implementation status, direction of travel, success), those are used as the scales. Attribution, comparator relevance, priority and tractability use High/Medium/Low; transferability uses likely/conditional/unlikely; unresolved gap uses open/partly addressed/largely closed. Every scale allows "insufficient evidence".
- The Commission's standard preparation and progress wording is captured word for word on EU findings, to support direction of travel.
- Run 1b uses gates G1b, G2b, G5b and G6b.
- The project folder should be a git repository with a commit after every gate decision, to support E3.
- A draft list of ten problem mechanisms is provided for approval at G4.

## Change history

- 2026-10-23: Log created after first full review of Codebooks 1 to 6. Group A proposed.
- 2026-10-23: Group A approved (A2 modified to two to three chapters). Group B proposed.
- 2026-10-23: Group B approved. Group C/D part 1 proposed.
- 2026-10-23: Group C/D part 1 approved. Part 2 proposed (C1, C5, C4, D4); D5 added.
- 2026-10-23: C1, C5, C4, D4 approved. Final group proposed (D5, E1 to E4).
- 2026-10-23: D5 and E1 to E4 approved.
- 2026-10-23: Follow-ups settled: run 1 narrowed to one chapter, Chapter 5 (A2 modified); no Serbian speaker (A4); Sofia and George review G6, G6b and G7 (E2); codebook format agreed (F1). Architecture confirmed as ready. Final package prepared.
