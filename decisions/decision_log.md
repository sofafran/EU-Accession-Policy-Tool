# EU Accession Reform Intelligence Tool: Architecture Decision Log

Purpose: record of the architecture decisions taken before building the tool in Claude Code.

Inputs reviewed: Codebooks 1 to 6 (versions dated 20 Oct 2026).

Status key: Open | Proposed | Approved | Modified (approved with changes) | Amended (partly replaced by a later decision) | Superseded (wholly replaced by a later decision) | Rejected

Overall status (23 Oct 2026): **architecture confirmed by Sofia.** All decisions approved. Final package prepared: ARCHITECTURE.md, CLAUDE.md, procedures, rules, schemas, templates, Codebooks 1 to 6 version 1.1 and new Codebook 7.

Overall status (29 Oct 2026): **pilot reconfigured by Sofia before gate G0.** Decisions A5 to A9, D6, E5 and F2 approved; A2, A3 and A4 superseded; A1 and D5 amended. The architecture is otherwise unchanged. To be confirmed in the G0 package.

Later on 29 Oct 2026: E6 to E9 approved (alpha product, review page, alpha learning log, George as alpha reviewer); E4 amended by E7. Folded into the same pre-G0 versions.

## Decision register

| ID | Group | Decision | Status | Outcome |
|---|---|---|---|---|
| A1 | Scope | How comparator countries are handled in run 1 | Amended by A5 (target country) | Run 1 split: 1a Serbia diagnostic; 1b comparator pilot on 2 to 3 analyst-selected issues, comparator evidence tagged as such, expansion logged as deliberate |
| A2 | Scope | Thematic scope of run 1 | Superseded by A6 and A9 | One chapter for run 1: Chapter 5 Public procurement. Chapter 15 Energy and a Chapter 23 sub-area deferred; expand only after run 1 is tested |
| A3 | Scope | Time window and evidence freeze date | Superseded by A7 (freeze date rule kept) | Evidence from 2014 onward; fixed freeze date just after this year's Commission enlargement package (set at G0); older documents by logged exception only |
| A4 | Scope | Language policy | Superseded by A8 | English primary; Serbian only for core documents with no English version; original quote plus flagged machine translation; no Serbian-speaking reviewer available, so machine-translated evidence is capped at Medium confidence and listed in the limits report |
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
| D5 | Data | Minimum set of matching fields | Amended by D6 (cross-cutting themes) | Controlled fields on every item; no free-text keywords; cross-chapter themes deferred |
| E1 | Process | Sample parse and review | Approved | 10 to 12 documents across five families; three hand-coded passages; automatic quote check; checklist; max two refinement loops; EU family first, then taxonomy, then the rest |
| E2 | Process | Control gates; AI authority | Approved | Gates G0 to G8, all blocking, gate log; three tiers of authority. Reviewers: Sofia at all gates; Sofia and George at G6, G6b and G7 |
| E3 | Process | Future runs and versioning | Approved | Incremental versioned runs; unchanged sources reused; updates kept as versions; targeted re-runs; validated judgements never overwritten; G8 run review feeds codebook changes |
| E4 | Process | What run 1 produces | Amended by E7 (review page) | Internal analyst products; draft policy options only for run 1b issues; no dashboard in run 1; new Codebook 7 (Outputs) |
| A5 | Scope | Pilot country for run 1 | Approved | North Macedonia (MKD) replaces Serbia as the target country. The run 1a and 1b structure of A1 is unchanged |
| A6 | Scope | Thematic scope of run 1 | Approved | (a) All of Chapter 2, Freedom of movement for workers; (b) recommendations materially relating to technology and AI wherever they occur in the accession material. Theme areas: artificial intelligence; digital government and digital public services; digital infrastructure and connectivity; data and data governance; cybersecurity; digital identity; interoperability and electronic systems; digitalisation of government or economic activity. Incidental references to technology are out of scope. The full analytical chain is followed for every issue originating from an in-scope Chapter 2 item or technology and AI recommendation |
| A7 | Scope | Time window | Approved | Evidence from 1 January 2020 to the evidence freeze date; freeze date rule from A3 kept; earlier evidence only by logged exception where needed to understand the origin or evolution of an in-scope issue |
| A8 | Scope | Language policy | Approved | English primary; Macedonian where a core relevant source has no suitable English version; Albanian-language official material not excluded automatically: where a core relevant source exists only in Albanian it is recorded and the same translation and confidence safeguards apply; machine translation flagged and capped at Medium confidence |
| A9 | Scope | Deferred chapters and material outside the scope | Approved | The Serbia-era deferral of Chapter 15 and a Chapter 23 sub-area is removed and no replacement list is kept. Material outside Chapter 2 and the technology and AI theme is out of scope unless it is needed to follow the analytical chain of an issue already in scope |
| D6 | Data | Cross-cutting themes | Approved | Controlled theme list in `taxonomy/themes.csv` with a materiality test; evidence items carry `themes` and `scope_basis` (chapter, theme, chain, exception); pass 2 scope check with `out_of_scope` status; theme columns added to the source requirements, source register and reform issues; brought forward from the deferral in D5 because A6 requires it |
| E5 | Process | Handling the pilot change | Approved | RUN-2026-01 kept, as no acquisition, extraction or analysis had taken place; treated as a pre-G0 configuration change; superseded limits marked `superseded` and replaced by new rows; new versions: codebooks 1.2 (1 to 6) and 1.1 (7), rules 0.1b, data dictionary 1.1, evidence schema 1.1, mechanism list 0.1a, theme list 1.0, ARCHITECTURE.md 1.1 |
| E6 | Process | Purpose of run 1 | Approved | RUN-2026-01 is an alpha product and methodology test. Besides the analysis, it tests the end-to-end workflow, source collection and processing, extraction and classification, taxonomy and matching, human review gates, assessment and judgement, outputs, and the usefulness of the review page. The method stays reusable and country-neutral |
| E7 | Process | Single HTML review page | Amended by E11 (analysis page) | `index.html` in the repository root, intended for later hosting on GitHub Pages. Read-only review interface showing validated material and relevant work in progress, each labelled Validated, Pending review, Proposed, Draft or Not started. Not the formal gate-decision mechanism: decisions stay in the review spreadsheets and the gate log. Generated by `tools/build_review_page.py` once built; rebuilt after each gate decision and when a gate package is prepared. Replaces the "no dashboard" element of E4 for this page only; no interactive country or thematic dashboard in run 1 |
| E8 | Process | Alpha learning log | Approved | `runs/RUN-2026-01/alpha_learning_log.csv` holds curated, material lessons from the alpha, especially for scaling to more chapters, clusters and countries. It cross-references the limits log, decision log, gate log and run notes instead of repeating them. `run_notes.md` stays the low-threshold working diary. The agent proposes rows; Sofia confirms them at gates. Feeds the run review at G8 |
| E9 | Process | George's role in the alpha | Approved | George is an alpha reviewer of the developing product and the review page throughout the run. Formal gate responsibilities are unchanged (Sofia at all gates; Sofia and George at G6, G6b and G7). George's feedback goes to Sofia separately; material feedback is recorded in the alpha learning log and, where relevant, in the decision log, limits log or run record |
| E10 | Process | Visibility of the repository and review page | Approved | The GitHub repository and the GitHub Pages review page stay public for the alpha. Agreed by Sofia with George on 29 Oct 2026. Treated as settled; not to be reopened unless Sofia asks |
| E11 | Process | Analysis mock-up page | Approved | Amends E7: besides the single review page, a second generated page, `analysis.html`, linked by a button at the bottom of `index.html`, shows in one scroll how the evidence and later the analysis are built along the chain. Real evidence (quotes, sources, item IDs) where it exists; labelled placeholders elsewhere; items inside hand-coding passages left out until hand-coded. Draft review aid, not a product; rebuilt with the review page at every gate |
| F1 | Package | Format of revised codebooks | Approved | Markdown copies in the Claude Code folder (followed by agents) plus Word copies with tracked changes against the 20 Oct originals for human review; Codebook 7 in both forms |
| F2 | Package | Country neutrality | Approved | Codebooks, procedures and rules use "target country" or "pilot country"; run-specific settings (country, chapters, themes, time window, languages, source hints, area codes) sit in the run record, CLAUDE.md and the limits log |

## Points added while preparing the package (for review)

- Of Codebook 4's eleven information types, seven are extracted as claim types and four (status, date, actor, source reference) are recorded as details on every item. This follows from B2.
- Where Codebook 6 already named categories (implementation status, direction of travel, success), those are used as the scales. Attribution, comparator relevance, priority and tractability use High/Medium/Low; transferability uses likely/conditional/unlikely; unresolved gap uses open/partly addressed/largely closed. Every scale allows "insufficient evidence".
- The Commission's standard preparation and progress wording is captured word for word on EU findings, to support direction of travel.
- Run 1b uses gates G1b, G2b, G5b and G6b.
- The project folder should be a git repository with a commit after every gate decision, to support E3.
- A draft list of ten problem mechanisms is provided for approval at G4.

## Resolutions recorded before G0 (29 Oct 2026)

Confirmed by Sofia after the pilot reconfiguration. These are to be included in the G0 package.

- **Schema and status (D6):** the new evidence item fields (`themes`, `scope_basis`), `extraction.themes_version`, nullable `cluster` and `chapter`, the `theme_doubtful` flag and the `out_of_scope` classification status are approved design choices for this pilot and are kept in the methodology.
- **Reviewers and translation (A8):** no Macedonian- or Albanian-speaking reviewer is named for RUN-2026-01. The Medium confidence cap and the translation safeguards for machine-translated evidence remain in force.
- **Area codes:** the proposed reform-issue area codes `FMW` and `TEC` are left unresolved and will be decided at G4, based on the evidence and the draft taxonomy.
- **Accession status facts:** statements about North Macedonia's negotiation, cluster or benchmark status are not treated as established. They are verified against authoritative EU sources during stage 1 before being used analytically.
- **Word copies (F1):** decision F1 stays in this log as a historical decision. Word copies are not created or updated for this pilot at this stage.
- **Process flow diagram:** `process_flow.png` and `process_flow.dot`, referred to in `ARCHITECTURE.md`, are missing from the repository. Recorded as a known, non-blocking documentation gap; no replacements are made at this stage.

## Change history

- 2026-10-23: Log created after first full review of Codebooks 1 to 6. Group A proposed.
- 2026-10-23: Group A approved (A2 modified to two to three chapters). Group B proposed.
- 2026-10-23: Group B approved. Group C/D part 1 proposed.
- 2026-10-23: Group C/D part 1 approved. Part 2 proposed (C1, C5, C4, D4); D5 added.
- 2026-10-23: C1, C5, C4, D4 approved. Final group proposed (D5, E1 to E4).
- 2026-10-23: D5 and E1 to E4 approved.
- 2026-10-23: Follow-ups settled: run 1 narrowed to one chapter, Chapter 5 (A2 modified); no Serbian speaker (A4); Sofia and George review G6, G6b and G7 (E2); codebook format agreed (F1). Architecture confirmed as ready. Final package prepared.
- 2026-10-29: Before G0, Sofia reconfigured the pilot from Serbia, Chapter 5 to North Macedonia, Chapter 2 plus a technology and AI theme. A5 to A9, D6, E5 and F2 approved; A2 to A4 superseded; A1 and D5 amended. Codebooks, procedures and rules made country-neutral.
- 2026-10-29: Pre-G0 resolutions recorded (schema and `out_of_scope` status confirmed; no Macedonian- or Albanian-speaking reviewer; area codes left to G4; accession status facts to be verified at stage 1; no Word copies for this pilot at this stage; missing process flow diagram recorded as a non-blocking gap).
- 2026-10-29: E6 to E9 approved (alpha product, review page, alpha learning log, George as alpha reviewer); E4 amended; LIM-0007 superseded by LIM-0013. Folded into the current pre-G0 versions.
- 2026-10-29: E10 approved: repository and review page public for the alpha, agreed with George.
- 2026-10-29: G0 passed with conditions (GATE-0001). The pre-G0 decisions (A5 to A9, D6, E5 to E10, F2) and versions confirmed; freeze date set to 2026-10-29.
- 2026-10-29: Before G3, Sofia decided rule issues R1 to R11 from the first sample (review/RUN-2026-01/G3_rule_issues.csv): R4, R5, R7, R9, R10 and R11 as proposed; R1 narrower materiality test; R2 digital skills only when linked; R3 record chapter or sub-area level of progress wording; R6 pre-2020 claims as controlled exceptions; R8 Chapter 2 in its EU meaning. Extraction rules 0.2, classification and judgement rules 0.2, theme list 1.1, schema and data dictionary 1.2, limits LIM-0020 to LIM-0022.
- 2026-10-29: E11 approved by Sofia: analysis mock-up page `analysis.html`, generated with the review page; E7 amended.
