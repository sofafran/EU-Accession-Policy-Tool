# Run record: RUN-2026-01

Status: **not started (awaiting gate G0)**

| Field | Value |
|---|---|
| Run ID | RUN-2026-01 |
| Current stage | 0 Run setup (update at the start of every stage, for example `9 Classify and link` or `1b step 3`) |
| Purpose | Alpha product and methodology test. Run 1 produces a North Macedonia diagnostic (run 1a) and a comparator pilot (run 1b), and tests the end-to-end workflow, source collection and processing, extraction and classification, taxonomy and matching, the human review gates, assessment and judgement, outputs, and the usefulness of the review page. Lessons are recorded in the alpha learning log to inform scaling to further chapters, clusters and countries |
| Target country | North Macedonia (MKD) |
| Thematic scope | (a) All of Chapter 2, Freedom of movement for workers (Cluster 2, Internal market); (b) the technology and AI theme: recommendations materially relating to the areas listed in `taxonomy/themes.csv` (theme group `TECH`), wherever they occur in the accession material. Incidental references to technology are out of scope. The full analytical chain is followed for every issue originating from an in-scope Chapter 2 item or technology and AI recommendation. Material outside (a) and (b) is out of scope unless it is needed to follow the chain of an issue already in scope. |
| Comparator scope | Run 1b only: two or three reform issues selected at G6, with two or three comparator countries each, approved at G1b |
| Time window | 2020-01-01 to the evidence freeze date; earlier material only by logged exception where needed to understand the origin or evolution of an in-scope issue |
| Evidence freeze date | TBC at G0 (to be set just after this year's Commission enlargement package) |
| Language | English primary; Macedonian or Albanian only for core relevant sources with no suitable English version, each recorded in the register; machine translation flagged and capped at Medium confidence |
| Reviewers | Formal gate approvers: Sofia (all gates); Sofia and George together (G6, G6b and G7) |
| Alpha reviewers | George reviews the developing product and the review page throughout the run, outside the formal gates. George's feedback reaches Sofia separately; material points are recorded in the alpha learning log |
| Review page | `index.html` in the repository root (hand-built skeleton until `tools/build_review_page.py` exists) |
| Alpha learning log | `runs/RUN-2026-01/alpha_learning_log.csv` |
| Codebooks version | 1.2 (Codebooks 1 to 6), 1.1 (Codebook 7) |
| Extraction rules version | 0.1b (to be revised at G3) |
| Classification rules version | 0.1b |
| Judgement rules version | 0.1b |
| Theme list version | 1.0 (`taxonomy/themes.csv`) |
| Taxonomy version | none yet (created at G4) |
| Mechanism list version | 0.1a draft (approved at G4) |
| Data dictionary version | 1.1 (29 Oct 2026) |
| Evidence schema version | 1.1 (29 Oct 2026) |
| Tools versions | to be recorded at G0 |
| Started | |
| Closed | |

## Run parts

- **Run 1a:** stages 0 to 11 for North Macedonia (procedures P1 to P3).
- **Run 1b:** comparator pilot for the issues chosen at G6 (procedure P4), then outputs and close (procedure P5).

## Run-specific settings

These settings apply the country-neutral procedures to this run.

- **Folders and IDs:** sources are filed under `sources/MKD/<family>/` and evidence under `evidence/MKD/`. Source IDs take the form `MKD-<family>-<year>-<sequence>`, for example `MKD-EU-2025-001_EC_North-Macedonia-Report-2025.pdf`.
- **Country names as printed:** documents published before February 2019 call the country "the former Yugoslav Republic of Macedonia". Quotes keep the name as printed; actor records list the earlier name under `former_names`. The same applies to ministries that have been renamed.
- **Accession stage (unverified):** the status of North Macedonia's negotiations, clusters and benchmarks is not treated as established. At stage 1, verify it against authoritative EU sources (Council and Commission documents) before it is used in the requirements list or in any analysis. Until then, list benchmark requirement lines with status `open` rather than assuming they exist or do not.
- **Source requirement hints for stage 1** (hints, not facts; confirm by searching):
  - EU: Commission annual reports on North Macedonia (Chapter 2 sections, and all sections for technology and AI recommendations); the screening report for Cluster 2 if public, and for clusters containing technology and AI material if public; Council conclusions; the Reform Agenda and Growth Plan documents and their assessments where they cover Chapter 2 or the theme.
  - GOV: laws on employment of foreigners, labour relations and social security coordination; bilateral social security agreements; reports of the public employment service; the National Programme for the Adoption of the Acquis; national strategies and laws on digital transformation, electronic government, electronic identification and trust services, personal data protection, cybersecurity and artificial intelligence, and reports of the bodies responsible for them.
  - IO: ILO, ETF, IOM, OECD (including SIGMA where it covers digital government), World Bank, UNDP, ITU and the Regional Cooperation Council, where they cover Chapter 2 or the theme.
  - RES and CSO: analyses and monitoring of labour mobility, digital government, data protection, digital rights and the use of AI in North Macedonia.
- **Original-language titles:** search hints include the Macedonian title, and the Albanian title where relevant.
- **Text recognition languages:** English, Macedonian (Cyrillic) and Albanian.
- **Reform-issue area codes (unresolved, decided at G4):** `FMW` for Chapter 2 issues and `TEC` for technology and AI issues are proposals only. They will be decided at G4 in the light of the evidence and the draft taxonomy.

## Notes

- **Pre-G0 resolutions (29 Oct 2026), confirmed by Sofia:**
  - the new evidence schema fields (`themes`, `scope_basis`, `extraction.themes_version`, nullable `cluster` and `chapter`), the `theme_doubtful` flag and the `out_of_scope` classification status are approved design choices for this pilot, kept in the methodology and included in the G0 package (decision D6);
  - no reviewer who reads Macedonian or Albanian is named for this run, so the Medium confidence cap and the translation safeguards for machine-translated evidence apply (decision A8);
  - the reform-issue area codes remain unresolved until G4;
  - statements about the country's negotiation, cluster or benchmark status are unverified until checked against authoritative EU sources at stage 1;
  - Word copies of the codebooks (decision F1) are not created or updated for this pilot at this stage;
  - `process_flow.png` and `process_flow.dot`, referred to in `ARCHITECTURE.md`, are missing from the repository. This is a known, non-blocking documentation gap; no replacements are made at this stage.
- **Alpha set-up (29 Oct 2026), confirmed by Sofia:** run 1 is treated as an alpha product and methodology test (E6); a single review page, `index.html`, shows validated material and labelled work in progress but is not the gate-decision mechanism (E7); an alpha learning log holds curated lessons, while `run_notes.md` stays the raw working diary (E8); George is an alpha reviewer, with formal gate responsibilities unchanged (E9). These were folded into the current pre-G0 versions.

- Active limits for this run are listed in `registers/limits_log.csv` (LIM-0008 to LIM-0013). LIM-0001 to LIM-0006 were recorded for the earlier Serbia configuration, and LIM-0007 before the review page was agreed; all were superseded on 29 Oct 2026, before G0.
- On 29 Oct 2026, before G0 and before any acquisition or extraction, the pilot was reconfigured from Serbia, Chapter 5 (Public procurement) to the scope above. The run kept its ID. Decisions behind this scope are recorded in `decisions/decision_log.md` (A5 to A9, D6, E5 to E9 and F2).
