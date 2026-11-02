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
| RUN-2026-02 | Montenegro | MNE | Negotiating since 2012, all chapters open, several closed. The alpha found an EU common position on Chapter 2 (AD 26/26, restricted, LIM-0028): check whether the chapter is provisionally closed, in which case issues are about implementation and closing-benchmark follow-up. 17 sources already held from the comparator pilot. Languages: Montenegrin (no ISO 639-1 code; record as `cnr` in notes, `sr` in the field), Albanian |
| RUN-2026-03 | Albania | ALB | Negotiating; check which clusters are open and the Chapter 2 benchmarks. Growth Plan Reform Agenda as for North Macedonia. 5 sources held. Language: Albanian (`sq`) |
| RUN-2026-04 | Moldova | MDA | The Commission reported on 13 October 2026 that the internal market cluster, which contains Chapter 2, was opened: check its opening benchmarks and any closing benchmarks. Moldova Growth Plan and Reform Agenda. 13 sources held. Language: Romanian (`ro`) |
| RUN-2026-05 | Ukraine | UKR | Same cluster opened on 13 October 2026. The Ukraine Facility and Ukraine Plan replace a Reform Agenda. Wartime context limits some evidence. Language: Ukrainian (`uk`) |
| RUN-2026-06 | Serbia | SRB | Negotiating; check whether the internal market cluster is open. 10 sources held. Language: Serbian (`sr`), Cyrillic and Latin scripts |
| RUN-2026-07 | Bosnia and Herzegovina | BIH | Candidate; check the state of negotiations and of screening. Several levels of government hold competence for labour and digital matters. Languages: Bosnian, Croatian, Serbian (`bs`, `hr`, `sr`) |
| RUN-2026-08 | Georgia | GEO | Candidate; the accession process has stalled. Check that the latest Commission report still assesses Chapter 2. Language: Georgian (`ka`), a separate script |
| RUN-2026-09 | Türkiye | TUR | Negotiations at a standstill since 2018; older negotiating framework. Check what the latest report says on Chapter 2. Language: Turkish (`tr`) |
| RUN-2026-10 | Kosovo | XKX | Potential candidate under a Stabilisation and Association Agreement; no screening. Use the EU designation "Kosovo*" with its standard footnote in outputs. `XKX` is the code in common use, not an official ISO code. Languages: Albanian, Serbian (`sq`, `sr`) |

Runs go one at a time, in this order. Each run's evidence freeze date is set by Sofia at its G0. It is set after the 2026 Enlargement Package (due 4 November 2026) where possible, so that each run includes its 2026 report.

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
- **Open point for RUN-2026-02 G0 (data model, tier 3):** an evidence file holds one extraction record per source, so a second run cannot yet record its own extraction of a source already held. Recommended option: add an optional `earlier_extractions` list to the evidence file (evidence schema 1.3). The main `extraction` record then describes the latest run, items keep their IDs, new items continue the numbering with `role` `target`, and the register `role` may hold `comparator;target`. This only affects the four countries above and is decided before their extraction starts.

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
