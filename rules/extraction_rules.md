# Extraction rules (pass 1)

Version 0.1, 23 October 2026. Status: draft, to be refined at gate G3 using the sample review. Every change after G3 creates a new version (0.2, 0.3 and so on) and is listed in the change log at the end of this file.

These rules tell the agent how to turn a converted source text into evidence items. They implement Codebook 4. Pass 1 stays close to the text: it records what a source says, not what it means for the analysis. Classification (reform issue, mechanism, links) happens in pass 2 and must not be attempted here.

## 1. The evidence item

An evidence item is **one claim, of one information type, with its exact quote and location**.

- If one sentence makes two claims of different types, create two items that share the same location.
- If one claim is spread over two sentences, quote both sentences in one item.
- Quotes are copied word for word from the converted text. Do not correct spelling, shorten with ellipses or merge non-adjacent text. A quote is normally one to three sentences.
- Write a `summary` of no more than 25 words that restates the claim in plain English. The summary must not add meaning, causes or judgements that are not in the quote.

## 2. The seven information types

| Type | Use when the text… | Typical sources | Not to be confused with |
|---|---|---|---|
| `finding` | judges the current situation (level of preparation, progress, a problem, a strength) | EU, IO, RES, CSO | `recommendation` (looks forward), `outcome` (result of a named action) |
| `recommendation` | says what should happen next, including EU expectations and benchmarks | EU, IO, RES, CSO | `intervention` (something the government itself plans or did) |
| `intervention` | describes a law, strategy, action plan, institutional change, system or programme that has been proposed, adopted or implemented | GOV, EU, IO | `outcome` (what happened after it) |
| `barrier` | explains what prevents progress (lack of staff, political pressure, missing secondary legislation) | RES, CSO, IO, EU | `finding` (states that a problem exists without saying why) |
| `outcome` | reports what changed after a named intervention | GOV, IO, RES | `metric` without a link to an intervention |
| `lesson` | states what worked, failed or mattered, and why, in the source's own words | RES, IO, CSO | your own inference (never extract inferred lessons) |
| `metric` | gives a number or indicator (share of negotiated procedures, number of complaints, processing time) | IO, GOV, CSO | `finding` (a qualitative judgement) |

When a passage is genuinely ambiguous between two types, choose the closer one and add the flag `ambiguous_type` with a short `extraction_note`. Do not create duplicate items to cover both options.

## 3. Details recorded on every item

- **Location:** page number (and end page if the quote spans pages), the section heading as printed, and paragraph number if the document numbers its paragraphs. For webpages, the section heading and the snapshot file.
- **Three dates, kept apart:**
  - `publication_date` comes from the source register.
  - `period_covered` comes from the source register or the document (Commission reports usually cover roughly the previous twelve months).
  - `event_date` is the date of the event in the claim, only if the text states it. Record its precision (`day`, `month`, `year`). If no date is stated, leave it empty. Never infer an event date from the publication date.
- **Speaker:** who makes the claim, normally the issuing institution. If the document reports someone else's view ("the government reports that…"), the speaker is the party whose view it is, and the flag `reported_view` is added.
- **Subjects:** the institutions the claim is about, as named in the text.
- **Stated status** (interventions only): `proposed`, `adopted`, `implemented`, `in_practice`, `reversed` (repealed, suspended or withdrawn) or `unclear`, based only on the wording of the source. "The law was adopted" is `adopted`, even if other sources say it is not applied.
- **EU standard scale** (EU findings only): if a Commission report uses its standard wording, record it exactly: `preparation_level` (for example "some level of preparation", "moderately prepared") and `progress_level` (for example "limited progress", "some progress"). These fields drive the later direction-of-travel judgement, so they must be copied exactly as printed.
- **Metric details** (metrics only): indicator, value, unit and reference period, as stated.
- **Structural tags:** country, role (target or comparator), cluster and chapter (two-digit code, for example `05`), taken from the source register or from the document's own headings. Pass 1 never assigns reform issues or mechanisms.
- **Pass 2 placeholders:** pass 1 sets the file's `classification.status` to `not_started` and each item's `pass2` block to empty lists with `classification_status` `not_classified` and `chain_link` null.

## 4. What not to extract

- Background description that makes no claim (for example a description of how the accession process works).
- Repeated boilerplate that appears in the same form every year, unless the wording or scale changes.
- Content outside the run scope (another chapter, another country), unless the source register marks it as comparator material.
- Your own conclusions, causes, or lessons the source does not state.
- Tables of contents, acknowledgements, annexes listing meetings.

## 5. Translation (Serbian-language sources)

- Quote the original Serbian text in `stated_text` and set `quote_language` to `sr`.
- Provide an English translation in `translation_en` and set `machine_translated` to `true`.
- Keep the Latin or Cyrillic script exactly as it appears in the source.
- Evidence confidence for this item is capped at Medium (Codebook 2).

## 6. Flags

Use these flags only. Each must be explained in `extraction_note` where it is not self-evident.

| Flag | Meaning |
|---|---|
| `ambiguous_type` | Two information types fit almost equally well |
| `reported_view` | The source reports another party's claim |
| `hedged` | The source itself expresses uncertainty ("appears", "reportedly") |
| `table` | The quote comes from a table and may lose structure |
| `ocr` | The text comes from text recognition and may contain errors |
| `possible_misread` | The converted text looks garbled around the quote |
| `out_of_window` | The event lies before 2014 but is kept to explain a live issue |

## 7. Automatic quote check

After extracting a source, the agent runs the quote verification tool. For PDFs and documents with pages, it checks the cited page; for webpages, which have no pages, it checks the cited section of the text file. Every item whose quote is not found word for word at the cited location is set to `quote_verified: false` and must be corrected or removed before the source counts as extracted. No item with `quote_verified: false` may reach a review sheet as final.

## 8. Illustrative example

The passage below is invented for illustration only. It shows the expected split, not real evidence.

> "Serbia has some level of preparation in the area of public procurement. Limited progress was made during the reporting period. In the coming year, Serbia should in particular ensure that intergovernmental agreements do not exempt large infrastructure projects from the public procurement rules."

| item | type | speaker | subjects | stated_text (abridged) | EU scale |
|---|---|---|---|---|---|
| …-0001 | finding | European Commission | Serbia | "Serbia has some level of preparation…" | preparation: some level of preparation |
| …-0002 | finding | European Commission | Serbia | "Limited progress was made…" | progress: limited progress |
| …-0003 | recommendation | European Commission | Government of Serbia | "In the coming year, Serbia should…" |  |

## Change log

- 0.1a (23 Oct 2026): consistency fixes before first use (reversed status, pass 2 placeholders, webpage quote check, translation cap wording).

- 0.1 (23 Oct 2026): first draft from the approved architecture.
