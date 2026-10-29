# Extraction rules (pass 1)

Version 0.3, 29 October 2026. Status: approved by the analyst before G3 (rule issues R1 to R20 from two sample rounds); to be confirmed at gate G3 after the second revision of the sample. This is the second and last refinement loop allowed before G3. Every change after G3 creates a new version (0.2, 0.3 and so on) and is listed in the change log at the end of this file.

These rules tell the agent how to turn a converted source text into evidence items. They implement Codebook 4. Pass 1 stays close to the text: it records what a source says, not what it means for the analysis. Classification (reform issue, mechanism, links) happens in pass 2 and must not be attempted here.

The run record sets the target country, the in-scope chapters, the cross-cutting themes, the time window and the languages for the run. These rules refer to them in general terms.

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
| `metric` | gives a number or indicator (number of work permits issued, share of public services available online, processing time) | IO, GOV, CSO | `finding` (a qualitative judgement) |

When a passage is genuinely ambiguous between two types, choose the closer one and add the flag `ambiguous_type` with a short `extraction_note`. Do not create duplicate items to cover both options.

## 3. Details recorded on every item

- **Location:** page number (and end page if the quote spans pages), the section heading as printed, and paragraph number if the document numbers its paragraphs. A quote may run over a page break: set `page_end`, and leave out the printed page numbers, running headers or footers and footnotes that sit between the pages; they must never appear in `stated_text`. Cut each quote to the claim: it starts at the claim's first word, and a quote longer than three sentences is checked by the validation tool. For webpages, the section heading and the snapshot file.
- **Three dates, kept apart:**
  - `publication_date` comes from the source register.
  - `period_covered` comes from the source register or the document (Commission reports usually cover roughly the previous twelve months).
  - `event_date` is the date of the event in the claim, only if the text states it. Record its precision (`day`, `month`, `year`). If no date is stated, leave it empty. Never infer an event date from the publication date.
- **Speaker:** who makes the claim, normally the issuing institution. If the document reports someone else's view ("the government reports that…"), the speaker is the party whose view it is, and the flag `reported_view` is added.
- **Subjects:** the institutions the claim is about, as named in the text. Record names exactly as printed, including earlier names of the country or of renamed institutions; pass 2 links them to the current actor record.
- **Stated status** (interventions only): `proposed`, `adopted`, `implemented`, `in_practice`, `in_progress` (the source says the work is under way, for example "being developed" or "being upgraded"), `reversed` (repealed, suspended or withdrawn) or `unclear`, based only on the wording of the source. "The law was adopted" is `adopted`, even if other sources say it is not applied.
- **Systems that do not work:** where a source says a named system exists but does not function, use `unclear` and explain in `extraction_note`.
- **Intervention or finding:** a named law, strategy, action plan, programme, institution or system is an `intervention`. A description of the legal or institutional situation that names no measure is a `finding`.
- **EU standard scale** (EU findings only): if a Commission report uses its standard wording, record it exactly: `preparation_level` (for example "some level of preparation", "moderately prepared") and `progress_level` (for example "limited progress", "some progress"). These fields drive the later direction-of-travel judgement, so they must be copied exactly as printed. Set `applies_to` to `chapter` when the wording rates the whole chapter, and to `sub_area` when it rates only part of it (for example "some progress was made in the e-government area"), and name the sub-area in `extraction_note`.
- **Metric details** (metrics only): indicator, value, unit and reference period, as stated.
- **Structural tags:** country, role (target or comparator), cluster and chapter (two-digit code, for example `02`), taken from the heading or subject of the passage itself, not from how the whole source is registered. Where neither the document nor the register gives a chapter (for example a national digital strategy), leave `cluster` and `chapter` empty rather than infer them. Pass 1 never assigns reform issues or mechanisms.
- **Scope basis and themes:** see section 4.
- **Pass 2 placeholders:** pass 1 sets the file's `classification.status` to `not_started` and each item's `pass2` block to empty lists with `classification_status` `not_classified` and `chain_link` null.

## 4. Scope: chapters, themes and the chain

A run's thematic scope can have two parts: one or more in-scope chapters, and one or more cross-cutting themes defined in `taxonomy/themes.csv`. Every item records why it is in scope in `scope_basis` (one or more values) and the theme codes it materially concerns in `themes`.

| `scope_basis` | Use when | Who decides |
|---|---|---|
| `chapter` | The passage sits under an in-scope chapter heading, or its subject is an in-scope chapter as bounded in the run record. Being in a source registered against the chapter is not enough | Tier 1 (structural tag) |
| `theme` | The passage materially concerns a theme area, wherever it occurs | Tier 2 if clear-cut; flag `theme_doubtful` if not |
| `chain` | The passage is outside the in-scope chapters and themes, but the text itself explicitly connects it to an in-scope matter (it names an in-scope intervention, recommendation or requirement, or states that it responds to one) | Tier 2; confirmed in pass 2 |
| `exception` | The analyst has allowed the passage by a logged exception; cite the limit ID in `extraction_note` | Analyst |

**The materiality test for themes.** A passage materially concerns a theme area only when the technology or digital issue itself is the subject of the claim: for example, a recommendation to connect to an EU electronic exchange system, adopt rules on artificial intelligence, protect personal data, secure networks or introduce electronic identification. A passage does not qualify when an IT tool, database or online channel is mentioned within a reform of another sector (for example a customs, plant health, fisheries or market disclosure system described as part of that sector's reform), when it publishes something online, or when it refers to "modernisation" with no digital content. Such sector tools qualify only when the text itself frames them as digital transformation of government or as interoperability with EU electronic systems. Online public services that citizens or businesses use directly (for example an e-procurement portal used by bidders, tax e-services, eHealth appointments or land registry e-services) are digital government (`TECH-DGOV`) wherever they sit; back-office systems used inside a sector reform (for example court case management or customs processing) are not. The 112 emergency number is out of scope unless the claim is about a digital or AI solution itself. Use the definitions and the material and incidental examples in `taxonomy/themes.csv`, not the theme labels alone.

- Digital skills are not a theme area. Extract them only where the text directly links them to an in-scope technology or AI recommendation, and tag the theme code of that recommendation.
- Tag every theme code that applies; an item can be in scope on both `chapter` and `theme`.
- Items from an in-scope chapter carry `themes` codes too, where the materiality test is met, so that the theme view finds them.
- When it is unclear whether the test is met, extract the item, tag the closest theme code, add the flag `theme_doubtful` and explain in `extraction_note`. Doubtful items are listed for the analyst at the next gate. Do not leave them out silently.
- The run record sets the boundary of each in-scope chapter. Material outside that boundary is out of scope even when it sits under the chapter's subject in a non-EU source.
- Outside the in-scope chapters, extract recommendations that meet the materiality test and the other items (findings, interventions, barriers, outcomes, lessons and metrics) that meet it too, because they may form the chain of an issue that originates from such a recommendation. Pass 2 decides whether each one belongs to an in-scope issue.
- Pass 1 never decides that a `chain` passage belongs to a particular issue. It records the explicit connection in the text; pass 2 confirms it or marks the item `out_of_scope`.

## 5. What not to extract

- Background description that makes no claim (for example a description of how the accession process works).
- Headings, and lead-in sentences that only introduce a list or table ("the following table shows…"); extract the claims they introduce instead. A heading or lead-in that states a claim of its own, not repeated in the items below it, is extracted.
- Repeated boilerplate that appears in the same form every year, unless the wording or scale changes. Within one document, a claim that appears in more than one place in the running text (for example in a summary and in the detailed section) is extracted at each place, as separate items; pass 2 links them with `same_as_earlier`, and they never corroborate each other. Summary tables and annexes that only restate a claim already extracted from the same document are not extracted again; add "also at page n" to the extracted item's `extraction_note`.
- Content outside the run scope (another chapter or theme, another country) that does not qualify under section 4, unless the source register marks it as comparator material.
- Your own conclusions, causes, or lessons the source does not state.
- Tables of contents, acknowledgements, annexes listing meetings.

## 6. Translation (sources not in English)

- Quote the original text in `stated_text` and set `quote_language` to its ISO 639-1 code (for example `mk` for Macedonian, `sq` for Albanian).
- Provide an English translation in `translation_en` and set `machine_translated` to `true`.
- Keep the script exactly as it appears in the source, whether Cyrillic or Latin, including any mixture of the two.
- Evidence confidence for this item is capped at Medium (Codebook 2).

## 7. Flags

Use these flags only. Each must be explained in `extraction_note` where it is not self-evident.

| Flag | Meaning |
|---|---|
| `ambiguous_type` | Two information types fit almost equally well |
| `reported_view` | The source reports another party's claim |
| `hedged` | The source itself expresses uncertainty ("appears", "reportedly") |
| `table` | The quote comes from a table and may lose structure |
| `ocr` | The text comes from text recognition and may contain errors |
| `possible_misread` | The converted text looks garbled around the quote |
| `out_of_window` | The claim is mainly about an event before the start of the run's time window and is kept as a controlled exception because it is needed to explain an in-scope issue; say why in `extraction_note`. Claims about the current situation that only refer back to an earlier event are in scope and are not flagged |
| `theme_doubtful` | It is unclear whether the passage meets the materiality test for the theme code given |

## 8. Automatic quote check

After extracting a source, the agent runs the quote verification tool. For PDFs and documents with pages, it checks the cited page; for webpages, which have no pages, it checks the cited section of the text file. Every item whose quote is not found word for word at the cited location is set to `quote_verified: false` and must be corrected or removed before the source counts as extracted. No item with `quote_verified: false` may reach a review sheet as final.

## 9. Illustrative examples

The passages below are invented for illustration only. They show the expected split, not real evidence. "The country" stands for the target country's name as printed.

**An in-scope chapter section** (Chapter 2: Freedom of movement for workers):

> "The country has some level of preparation in the area of freedom of movement for workers. Limited progress was made during the reporting period. In the coming year, the country should in particular complete the technical preparations for connecting to the Electronic Exchange of Social Security Information system."

| item | type | speaker | subjects | stated_text (abridged) | EU scale | scope_basis | themes |
|---|---|---|---|---|---|---|---|
| …-0001 | finding | European Commission | the country | "The country has some level of preparation…" | preparation: some level of preparation | chapter |  |
| …-0002 | finding | European Commission | the country | "Limited progress was made…" | progress: limited progress | chapter |  |
| …-0003 | recommendation | European Commission | the country | "In the coming year, the country should…" |  | chapter; theme | TECH-INTEROP |

**A section outside the in-scope chapters** (for example Chapter 10: Information society and media):

> "In the coming year, the country should in particular: adopt the law on electronic identification and trust services; publish the annual report of the regulatory agency on its website."

| item | type | stated_text (abridged) | scope_basis | themes | note |
|---|---|---|---|---|---|
| …-0010 | recommendation | "adopt the law on electronic identification and trust services" | theme | TECH-EID | Material: the required action concerns digital identity |
| none |  | "publish the annual report … on its website" |  |  | Not extracted: the reference to a website is incidental |

## Change log

- 0.3 (29 Oct 2026): approved by the analyst after the re-run (rule issues R12 to R20). Online public services used by citizens or businesses are digital government wherever they sit; back-office sector systems are not (R12); the in-scope chapter boundary is set in the run record (R13, R14); headings that carry their own claim are kept (R15); summary tables and annexes that only restate are not extracted again (R16); quotes over page breaks skip footnotes too (R17); quotes are cut to the claim and long quotes are flagged by validation (R18); `unclear` for named systems that do not work (R19); the 112 emergency number is out unless the claim is about a digital or AI solution (R20).
- 0.2 (29 Oct 2026): approved by the analyst after the first sample (rule issues R1 to R11, review/RUN-2026-01/G3_rule_issues.csv). Narrower materiality test (R1); digital skills only when linked to an in-scope recommendation (R2); `eu_scale.applies_to` for chapter or sub-area wording (R3); quotes may cross page breaks, without printed page numbers or headers (R4); `in_progress` stated status (R5); `out_of_window` limited to claims mainly about pre-window events, as controlled exceptions (R6); chapter tags from the passage, not the source registration (R7); in-scope chapter boundaries set in the run record (R8); no headings or lead-in sentences (R9); repeated claims extracted at each place and linked in pass 2 (R10); named measures are interventions, unnamed legal situations are findings (R11).
- 0.1b (29 Oct 2026): pre-G0 reconfiguration of the pilot (decisions A5 to A9 and D6). Rules made country-neutral; scope section added with `scope_basis`, theme tags and the materiality test; `theme_doubtful` flag; `out_of_window` tied to the run's time window; `cluster` and `chapter` may be empty for sources with no chapter structure; translation rule covers any non-English source language; examples replaced.

- 0.1a (23 Oct 2026): consistency fixes before first use (reversed status, pass 2 placeholders, webpage quote check, translation cap wording).

- 0.1 (23 Oct 2026): first draft from the approved architecture.
