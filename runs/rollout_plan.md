# Multi-country rollout plan

Decision E19 (2 November 2026). Sofia decided to scale the method across the remaining EU accession countries, one run per country, after the North Macedonia alpha (RUN-2026-01) closed at G8. This settles the next-run question left open at G8 (G8-D03). This file is the plan; it starts no run. A run starts only when Sofia asks for it, and then follows its own G0.

## Principles

1. **North Macedonia is the methodological baseline, not the substantive template.** Every country uses the same codebooks, rules, procedures, data model, taxonomy logic, judgement framework, comparator approach and output structure. Nothing found for North Macedonia is assumed for another country. Each run checks its own accession status, Chapter 2 context, official documents, languages and evidence base at its own G0 and G1.
2. **One shared taxonomy.** All countries classify against the same reform issues and mechanisms, so that the same issue can be compared across countries. New-country evidence is never forced into an existing issue: an item that fits none goes to `taxonomy/unmatched_queue.csv`, and a new shared issue is proposed at that run's G4 or G5, as in the alpha.
3. **One shared core, one small folder per run.** The shared core is the codebooks, rules, procedures, schemas, taxonomy, registers, judgements, links, entities and tools. A run adds only `runs/<run_id>/` (run record, run notes, learning log), plus its sources, evidence, review packages and outputs, which are already filed by country and run.
4. **No new gates.** Each run passes G0 to G8 as the alpha did, with the comparator step (G1b, G2b, G5b, G6b) when comparators are used.
5. **Comparisons use validated judgements only.** A country appears in comparisons on the regional page only after its G6 has passed.
6. **RUN-2026-01 stays closed.** Its evidence, judgements and outputs are not changed by the rollout. Its 2026 refresh (E18) remains a separate step, waiting for the 2026 Enlargement Package.

## Shared-core versions for RUN-2026-02 onwards

The changes PC-01 to PC-17, approved at G8 (GATE-0013), were applied before RUN-2026-02 as new shared-core versions:

- Codebooks 1.3 (Codebooks 1 to 6) and 1.2 (Codebook 7);
- extraction rules 0.5, classification rules 0.4, judgement rules 0.5;
- data dictionary 1.5;
- procedures with `<run_id>` in place of the alpha's run ID.

The taxonomy stays at version 1.1. PC-12 is applied through Codebook 5 and the classification rules. PC-11 (consider adding MEC-04, weak enforcement or oversight, to RI-TEC-028) is carried to RUN-2026-02's G4 as a proposal: changing the shared row now would change how a validated North Macedonia issue is shown.

The details are in `codebooks/CHANGELOG.md`. RUN-2026-01 keeps the versions recorded in its run record and evidence files.

## Runs

The order below is Sofia's. Points to check are starting points for each run's G0 and G1, not facts: each is confirmed from authoritative EU sources at stage 1.

| Run | Country | Code | Points to check at G0 and G1 |
|---|---|---|---|
| RUN-2026-01 | North Macedonia | MKD | Completed alpha (G8, GATE-0013). Baseline only; 2026 refresh pending (E18) |
| RUN-2026-02 | Moldova | MDA | Closed: G8 passed 6 November 2026 (GATE-0030). 53 issues judged, 56 outputs signed off at G7 (GATE-0029), comparator step on RI-FMW-015, RI-TEC-038 and RI-TEC-036. Approved changes PC-18 to PC-32 to be applied before RUN-2026-03. Language: Romanian (`ro`) |
| RUN-2026-03 | Montenegro | MNE | Held: starts only after Sofia reviews what RUN-2026-02 teaches (E20). Negotiating since 2012, all chapters open, several closed. The alpha found an EU common position on Chapter 2 (AD 26/26, restricted, LIM-0028): check whether the chapter is provisionally closed, in which case issues are about implementation and closing-benchmark follow-up. 17 sources already held from the comparator pilot. Languages: Montenegrin (no ISO 639-1 code; record as `cnr` in notes, `sr` in the field), Albanian |
| RUN-2026-04 | Albania | ALB | Negotiating; check which clusters are open and the Chapter 2 benchmarks. Growth Plan Reform Agenda as for North Macedonia. 5 sources held. Language: Albanian (`sq`) |
| RUN-2026-05 | Ukraine | UKR | Same cluster opened on 13 October 2026. The Ukraine Facility and Ukraine Plan replace a Reform Agenda. Wartime context limits some evidence. Language: Ukrainian (`uk`) |
| RUN-2026-06 | Serbia | SRB | Negotiating; check whether the internal market cluster is open. 10 sources held. Language: Serbian (`sr`), Cyrillic and Latin scripts |
| RUN-2026-07 | Bosnia and Herzegovina | BIH | Candidate; check the state of negotiations and of screening. Several levels of government hold competence for labour and digital matters. Languages: Bosnian, Croatian, Serbian (`bs`, `hr`, `sr`) |
| RUN-2026-08 | Georgia | GEO | Candidate; the accession process has stalled. Check that the latest Commission report still assesses Chapter 2. Language: Georgian (`ka`), a separate script |
| RUN-2026-09 | Türkiye | TUR | Negotiations at a standstill since 2018; older negotiating framework. Check what the latest report says on Chapter 2. Language: Turkish (`tr`) |
| RUN-2026-10 | Kosovo | XKX | Potential candidate under a Stabilisation and Association Agreement; no screening. Use the EU designation "Kosovo*" with its standard footnote in outputs. `XKX` is the code in common use, not an official ISO code. Languages: Albanian, Serbian (`sq`, `sr`) |

Runs go one at a time, in this order. The order was changed by decision E20 (3 November 2026): Moldova first, then Montenegro, with the other runs unscheduled until the scaling review below. Each run's evidence freeze date is set by Sofia at its G0. It is set after the 2026 Enlargement Package (due 4 November 2026) where possible, so that each run includes its 2026 report.

## 2026 Enlargement Package: availability for future runs

Checked on 5 November 2026 on the Commission's strategy and reports page. The package was adopted on 4 November 2026: the 2026 Communication on EU enlargement policy, COM(2026) 690 final (registered as MKD-EU-2026-009, horizontal, used by RUN-2026-01 and RUN-2026-02), and a report and factsheet for each of the ten countries. Only the North Macedonia and Moldova documents are downloaded and registered. For the other countries nothing is downloaded, registered or analysed: each run finds and registers its own report at stage 2 and confirms its G0 and G1 points from it. Report page URLs (the PDF link is on each page):

| Country | Run | 2026 report | Status |
|---|---|---|---|
| North Macedonia | RUN-2026-01 | enlargement.ec.europa.eu/north-macedonia-report-2026_en (SWD(2026) 693 final) | Registered, MKD-EU-2026-007; factsheet MKD-EU-2026-008 |
| Moldova | RUN-2026-02 | enlargement.ec.europa.eu/moldova-report-2026_en (SWD(2026) 698 final) | Registered, MDA-EU-2026-012; factsheet MDA-EU-2026-013 |
| Montenegro | RUN-2026-03 (next, held under E20) | enlargement.ec.europa.eu/montenegro-report-2026_en | Registered by RUN-2026-02 as a comparator source, MNE-EU-2026-003; RUN-2026-03 confirms it at its G1 |
| Albania | RUN-2026-04 | enlargement.ec.europa.eu/albania-report-2026_en | Published; not downloaded |
| Ukraine | RUN-2026-05 | enlargement.ec.europa.eu/ukraine-report-2026_en | Published; not downloaded |
| Serbia | RUN-2026-06 | enlargement.ec.europa.eu/serbia-report-2026_en | Published; not downloaded |
| Bosnia and Herzegovina | RUN-2026-07 | enlargement.ec.europa.eu/bosnia-and-herzegovina-report-2026_en | Published; not downloaded |
| Georgia | RUN-2026-08 | enlargement.ec.europa.eu/georgia-report-2026_en | Published; not downloaded |
| Türkiye | RUN-2026-09 | enlargement.ec.europa.eu/turkiye-report-2026_en | Published; not downloaded |
| Kosovo | RUN-2026-10 | enlargement.ec.europa.eu/kosovo-report-2026_en | Published; not downloaded |

Each country also has a 2026 factsheet (`eu-and-<country>-factsheet-enlargement-package-2026_en`). The package also includes pages on gradual integration strands, the state of play of negotiations per country and the accession process step by step; the state-of-play page is a useful starting point for each run's G0 check of open clusters. The Commission said before publication that the package would include indicative roadmaps for Montenegro, Albania, Moldova and Ukraine: check at each run's stage 2 whether they were issued as separate documents.

## Controlled scaling (E20)

Decision E20 (3 November 2026). Sofia moved the rollout into a controlled scaling phase:

- **One test country first.** Moldova (RUN-2026-02) is the first scaling test of the shared architecture. Run IDs follow start order, so Moldova takes RUN-2026-02 and Montenegro RUN-2026-03; references in the shared core to "RUN-2026-02" (PC-11 at G4, the held-sources data-model point at G0) now apply to Moldova.
- **Scaling review before the second test.** Montenegro does not start automatically. It starts only after Sofia has reviewed what the Moldova run teaches, using `runs/RUN-2026-02/scaling_note.md` and the run's learning log. The review is recorded in `decisions/decision_log.md`; it is not a new gate.
- **Later runs unscheduled.** Albania onwards keep their place in the table for planning only. No run after Montenegro is scheduled until the Montenegro run has been reviewed in the same way.
- **No redesign by default.** The method changes only where a genuine scaling problem requires it, through the normal gate route.

## Default scope of each run

These are set in the run record from the template in `runs/_template/`:

- **Chapter 2:** all of Chapter 2 (Freedom of movement for workers), in its EU meaning, as in the alpha.
- **Technology and AI:** the cross-cutting theme as defined in `taxonomy/themes.csv`.
- **Time window:** from 2020-01-01 to the run's evidence freeze date, including the latest Commission country report and the 2026 Enlargement Package where available.
- **Deviations:** any deviation from the default needs a country-specific reason. It is recorded in the run record and approved at G0.

## Reusing evidence the project already holds

The alpha's comparator pilot registered and partly extracted sources for Montenegro, Albania, Moldova and Serbia, and for Croatia.

- **Registration:** these sources are not downloaded or registered again (IDs are permanent). At the new run's G1 they are matched to its requirement lines. At its G2 they are confirmed or excluded like any other source.
- **Earlier items:** they were extracted for three issues only (LIM-0026). They are kept unchanged and stay valid for the alpha's comparator cases.
- **Settled at RUN-2026-02 G0 (decision E21, GATE-0014):** implemented as evidence schema 1.3 and data dictionary 1.6, with `tools/start_extraction.py`. Items belong to one run only, so a later run creates its own items rather than reusing earlier ones. The original open point read: an evidence file holds one extraction record per source, so a second run cannot yet record its own extraction of a source already held. Recommended option: add an optional `earlier_extractions` list to the evidence file (evidence schema 1.3). The main `extraction` record then describes the latest run, items keep their IDs, new items continue the numbering with `role` `target`, and the register `role` may hold `comparator;target`. This only affects the four countries above and is decided before their extraction starts.

## Comparator step in later runs

Procedure P4 applies unchanged, with one simplification approved with this plan:

- comparators are chosen first from countries already in the project, whose validated evidence and judgements are reused;
- new comparator evidence is collected only where a needed comparator is missing, for example a member state that reformed before accession.

## Pages

- **`analysis.html`:** the regional landing page. It covers:
  - country selection;
  - headline findings by country;
  - priority reform issues;
  - technology and AI themes;
  - the same issue compared across countries;
  - links into each country page.

  It lists every country in the table above with its status, and compares only validated judgements.
- **`analysis/<code>.html`:** one detailed page per country, with the same structure and navigation as the North Macedonia page. Before a run's G7 it is a labelled draft review aid.
- **`index.html`:** the review page of the active run, meaning the latest run with a run record. A closed run keeps its review page as `review_<run_id>.html`.
- **Summaries:** `alpha_summary.html` stays the alpha's management summary. A later run may add a one-page summary as `summary/<code>.html`, which the pages link to when it exists.
- **Building:** all pages are rebuilt with `tools/build_review_page.py`.

## Starting a run

When Sofia asks to start a country:

1. Copy `runs/_template/` to `runs/<run_id>/`.
2. Fill in the run record's fields and settings for the country (see the template's checklist).
3. Record the start in `decisions/decision_log.md`.
4. Proceed with procedure P1, stage 0. Sofia sets the evidence freeze date and approves G0.
