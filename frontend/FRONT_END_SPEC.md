# Front-End Specification: EU Accession Reform Intelligence Tool

Version 0.2, 3 November 2026. Status: approved for alpha implementation.

This specification defines the user-facing interface of the tool. It does not change the method. The analytical chain, codebooks, gates, evidence model, authority tiers and project architecture stay exactly as set out in `CLAUDE.md` and the codebooks. Where this specification and `CLAUDE.md` appear to differ, `CLAUDE.md` wins and the difference is raised with the analyst.

The interface is designed around the data the project already stores. It adds no analytical fields of its own. What the project does not store is listed in Appendix B, and the interface shows a labelled empty state there rather than a substitute.

Visual reference: `tool-explainer.html` (colours, shapes, tone and the six element types).

Change from version 0.1: the Appendix questions are answered from the repository (Appendix A); data the project does not store is recorded (Appendix B); the alpha scope is reduced to a lean first version (sections 13 and 14).

---

## 1. Product objective

Give senior users a fast, trustworthy view of EU accession reform priorities, country by country and across the region. Every claim on screen must trace back to reviewed judgements and exact evidence.

The interface follows one hierarchy throughout:

**Summary → analytical judgement → evidence**

A senior user reads the summary. An analyst or sceptical reader opens the judgement. Anyone verifying a point opens the evidence. The interface never makes the reader start at the evidence.

The front end **renders** what exists in the project files. It never generates, infers or summarises analysis of its own. If something does not exist in the files, the interface shows a labelled empty state, not a guess. Text that the project records as agent synthesis is always labelled as such.

---

## 2. User types and key questions

| User | Typical use | Main entry point |
|---|---|---|
| Regional directors | Regional picture in under a minute; where to focus | Regional overview |
| TBI country teams | Country priorities, what is stuck, what could be done | Country page |
| Colleagues preparing senior government engagements | Briefing on a few priority issues, with evidence they can stand behind | Country page, then reform issue detail |
| Analysts | Checking judgements, evidence, contradictions and status | Reform issue detail |
| Colleagues looking across countries | Common patterns, shared gaps, Technology and AI | Cross-country comparison, Technology and AI section |

The eight questions the interface must answer quickly:

| # | Question | Answered by |
|---|---|---|
| 1 | What are the most important reform issues in this country? | Country page: top priorities |
| 2 | Which issues are improving, persistent or worsening? | Direction-of-travel indicators, country page and comparison |
| 3 | What remains unresolved? | Unresolved gap, country page and issue detail |
| 4 | Which issues are highest priority? | Priority badges and default sort |
| 5 | What does the evidence say? | Evidence drawer in issue detail |
| 6 | What have comparable countries done? | Comparator cards in issue detail |
| 7 | What possible policy options emerge? | Policy options block in issue detail |
| 8 | How does this country compare with others? | Regional overview and cross-country comparison |

---

## 3. Information architecture

Four levels, plus one cross-cutting section.

```
Regional overview  (analysis.html)
 ├── Cross-country comparison        (section within analysis.html)
 ├── Technology and AI               (section within analysis.html)
 └── Country page                    (analysis/<country code>.html)
       └── Reform issue detail       (panel within the country page, shareable link)
```

Rules:
- **No new page types.** The structure uses the pages `CLAUDE.md` already defines: the regional page `analysis.html` and one country page per run at `analysis/<country code>.html`, where the country code is the three-letter code in `tools/common.py` (for example `analysis/MKD.html`, `analysis/MDA.html`). The review page `index.html` stays the analyst's review interface and is not part of this product.
- **One build command, separate page modules.** `tools/build_review_page.py` stays the single build command for all pages, as `CLAUDE.md` and procedure P1 require, and is run around every gate. The page logic already lives in separate modules, and the front end keeps that split:
  - `tools/build_review_page.py`: the review page `index.html` and the draft country page used before G7;
  - `tools/product_page.py`: the country product page, once a run's outputs have passed G7;
  - `tools/regional_page.py`: the regional page `analysis.html`;
  - shared design tokens, the shared header and the display mapping table (section 10.3) go in one shared module used by all three.
  There is no server, database or login.
- **Shareable links.** Each section and each issue has a stable link (for example `analysis/<code>.html#<reform issue ID>`), so a colleague can send a direct link to one issue.
- **Explainer.** A "How the tool works" link in the header of every page opens `tool-explainer.html`, using the same label as the link already on `index.html`.

Persistent header on every page:
- product name;
- breadcrumb (Region › Country › Issue);
- country switcher;
- "How the tool works" link.

---

## 4. Regional overview specification

**Purpose:** a senior user understands the regional picture in under one minute.

**Data rule:** the regional page uses **validated judgements only** (review status `validated` or `overridden`, not superseded), and only for countries that have passed G6 (`CLAUDE.md`, Pages). Countries before G6 appear with their run status but contribute no judgements.

**Layout, top to bottom:**

1. **Header strip.**
   - Countries covered, as a count.
   - Evidence period covered.
   - Scope line: "Chapter 2 (Freedom of movement for workers) and Technology and AI recommendations".
   - Date the page was built.

2. **Country status cards** (one per country, in rollout order from `runs/rollout_plan.md`). Each shows:
   - country name;
   - run status, as plain text (section 10.2);
   - evidence cut-off (freeze date);
   - for countries past G6: the top three priority issues, as short names, and a direction-of-travel summary (counts of issues by direction, shown as a small stacked bar with text labels);
   - an "Open country" action where a country page exists, marked "Draft" where that page is still a draft review aid.

   Countries not started show the card with "Not started" and nothing else.

3. **Regional pattern heatmap** (the main visual).
   - Rows are reform issues that appear validated in at least one country. Columns are countries.
   - Each cell shows direction of travel as colour plus an arrow symbol and a text label, and unresolved gap as cell fill strength. Cells are never colour only.
   - An empty cell means "not assessed in this country". It is drawn as a blank, outlined cell, not as a neutral colour.
   - Clicking a cell opens that issue for that country. Clicking a row label opens the cross-country comparison for that issue.
   - Default rows: issues sorted by how many countries rate them `High` priority, then by how many have an `open` gap. Limit to the top 12, with "Show all".

4. **Common reform themes.** Later (section 14): cards for the cross-cutting theme areas and mechanisms are not in the alpha.

5. **Technology and AI section** (section 8).

**Single-country state:** while only one country has passed G6, the overview still works. The heatmap has one column, and a line explains that comparison grows as further runs are validated. The overview should not look broken or empty.

---

## 5. Country page specification

**Purpose:** the main analytical product for one country.

**Status rule:** before G7, the country page is a draft review aid. After G7, it is the product (`CLAUDE.md`, Pages). Everything shown carries a status label. Nothing is presented as validated before its gate has passed. The alpha improves the product page (after G7), starting with North Macedonia; the draft page used before G7 keeps its current form.

### 5.1 Top of page: the summary layer

| Element | Content | Source |
|---|---|---|
| Country and run | Country name, run ID shown small, run status as plain text | Run record, gate log |
| Evidence cut-off | Evidence freeze date | Run record |
| Scope | Default scope plus any country deviation approved at G0, in one line | Run record |
| Overall assessment | The Summary of the run's scope overview, signed off at G7, labelled "Agent synthesis, validated at G7" | `review/<run_id>/stage12/narrative/scope_overview.md`, as used for `outputs/<run_id>/scope_overview.md`. If no such text has passed G7, show "Overall assessment: Not started". Never generated by the front end. |
| Top priority issues | Up to five issue cards, `High` priority first | Priority judgements |
| What is improving | Issues whose direction of travel is `improving` or `largely_resolved`, as a short list | Direction-of-travel judgements |
| What remains stuck | Issues whose direction of travel is `persistent` or `worsening`, or whose unresolved gap is `open` | Direction-of-travel and unresolved-gap judgements |
| Major implementation gaps | Issues with at least one linked intervention whose latest implementation status is `adopted` or `implemented`, and none `in_practice` | Implementation status judgements |

The three lists ("improving", "stuck", "implementation gaps") are filters over existing judgements, not new judgements. Each list item links to the issue.

### 5.2 Below: browse all reform issues

A filterable grid of **issue cards** (one per reform issue in scope for the country). Each card shows:

| Field | Display |
|---|---|
| Reform issue | Short issue name (taxonomy `label`); theme tag if Technology and AI |
| EU requirement | The approved issue definition from the taxonomy (`definition`, approved at G4), plus a factual line built from counts only: the number of linked EU requirement items and the years they span, for example "14 EU requirements, 2020 to 2025", with an "EU" source marker. No single quote or item summary is chosen to represent the issue. |
| Short assessment | The recorded `reason` of the priority judgement, shown in full or truncated visually with "Show more", never cut to a different sentence. Omitted if there is no priority judgement. |
| Implementation status | Chip summarising linked interventions by their latest status (for example "2 adopted · 1 in practice"). Counts only, no invented overall score. |
| Direction of travel | Arrow indicator plus label |
| Unresolved gap | Gap label |
| Priority | Priority badge |
| Tractability | Tractability badge |
| Evidence | Number of evidence items. Source quality, evidence confidence and relevance are shown separately for each item in the evidence drawer (rule 11: never merged into one score). |
| Comparator analysis | "Comparator analysis available" chip, or nothing |
| Status | Content status label of the issue (section 10.4), with a separate "Flagged for re-review" note where it applies |

**Default sort:** priority (`High` first), then unresolved gap (`open` first). `insufficient_evidence` values sort last.

**Card states:** collapsed by default. "Open" goes to the reform issue detail. Evidence is never shown on the card.

**Alternative view:** later (section 14). The alpha has the card grid only.

---

## 6. Reform issue detail specification

Opens as a full-width panel over the country page, with its own shareable link. It closes back to the same scroll position.

### 6.1 Header

- Issue name, country, theme tags.
- Four headline badges: direction of travel, unresolved gap, priority, tractability.
- Content status label for each badge, and a separate "Flagged for re-review" note on any badge whose judgement carries the flag.
- One-paragraph assessment: the "In brief" text of the issue's G7 narrative where it exists, labelled "Agent synthesis, validated at G7". Where it does not exist, the paragraph is omitted and the judgement reasons are shown with each badge instead.

### 6.2 The analytical chain

A vertical chain of nine steps. The reform issue itself is the page subject, so it heads the chain rather than appearing as a step.

EU requirement → Country response → Implementation → Outcome → Unresolved gap → Comparator evidence → Lesson → Priority → Policy option

Each step is a row with three parts:

| Part | Content |
|---|---|
| Label | Step name, marked **Stated** (what sources say) or **Assessed** (what reviewers conclude), following the explainer's colours |
| Summary | One or two lines: for stated steps, a count of the step's evidence items and the years they span; for assessed steps, the judgement value and its content status |
| Evidence | A count ("4 evidence items") that opens the evidence drawer for that step only |

A step's evidence is the issue's evidence items whose recorded chain link matches the step (`eu_requirement`, `country_response`, `implementation`, `outcome`, `unresolved_gap`, `lesson`).

Step-specific behaviour:
- **EU requirement:** the count and years of linked EU requirement items. Where the issue's G7 narrative has the section "How the EU requirement has changed", it is shown here, labelled "Agent synthesis, validated at G7". No other synthesis is shown.
- **Implementation:** list the linked interventions with their implementation status chips.
- **Outcome:** show success and attribution judgements separately, with the reminder "Adoption is not success" shown once as small text.
- **Unresolved gap:** the gap judgement, plus the direction-of-travel judgement.
- **Comparator evidence and Lesson:** comparator cards (6.4). If the issue was not chosen for comparator analysis at G6, show "No comparator analysis for this issue in this run".
- **Priority:** priority and tractability, side by side, each with its reason.
- **Policy option:** draft options with their status, each labelled "Internal draft" as the G7 decision requires (GATE-0012: policy options remain internal drafts until a separate decision adapts them for an external audience). If none exist, show "No policy options for this issue in this run".

### 6.3 Evidence drawer

Opens from any step. It shows only that step's evidence.

Each evidence item shows:
- the **exact quote**, as recorded, never shortened in a way that changes its meaning; long quotes are truncated visually with "Show full quote";
- source title, institution and publication date;
- page or section;
- source quality, evidence confidence and relevance as three separate labels;
- a "Machine translation" flag where relevant;
- a small reference ID for traceability, shown in muted text.

Behaviour:
- Show up to five items at first, ordered by relevance then confidence, with "Show all (n)".
- **Contradictions:** only `contradicts` links with review status `validated` are shown. They appear at the top of the drawer in a distinct amber "Conflicting evidence" block, with both sides visible. They are never hidden or resolved by the interface. Rejected links are not shown.
- **Evidence gaps:** where a step has no evidence, the drawer says "No evidence recorded for this step in this run". It never says "no evidence exists". Where a judgement is `insufficient_evidence`, that value is shown plainly.

### 6.4 Comparator cards

One card per comparator case (`entities/comparator_cases.csv`). Each shows:
- comparator country;
- what was done: the case's recorded `description`, truncated visually with "Show more" (no one-line field exists; see Appendix B);
- lesson: the case's `practical_lesson`, labelled "Agent synthesis, validated at G6b" as decided at G6b;
- comparator relevance and transferability, each with its content status;
- the number of supporting evidence items, which opens the same evidence drawer.

Clicking a comparator country opens that country's page if it is in the project. If that page is still a draft review aid (its run has not passed G7), the link is labelled "Draft country page" before it is followed. If the country has no page, there is no link.

---

## 7. Cross-country comparison specification

**Entry:** from the regional heatmap (row label), from an issue detail ("Compare across countries"), or from the comparison selector on `analysis.html`.

**Selector:** choose one reform issue. Comparison by theme is later (section 14).

**Layout:** the existing one-issue comparison on `analysis.html`, restyled as a comparison matrix, with countries as columns (up to six visible, horizontal scroll within the matrix beyond that) and these rows:

| Row | Display |
|---|---|
| Status | Run status as plain text, and the content status label of the judgements |
| Direction of travel | Arrow plus label, coloured |
| Unresolved gap | Fill-strength cell plus label |
| Priority | Badge |
| Implementation | Intervention status counts |
| Evidence | Item count |
| Comparator relevance | Label, where a comparator case links the countries |

Pattern aids:
- a one-line automatic pattern note built only from counts (for example "Gap open in 3 of 4 countries"), never interpretive text;
- clicking any cell opens the issue detail for that country.

**Data rule:** as on the regional overview, validated judgements only, from countries past G6.

---

## 8. Technology and AI section

**Purpose:** easy access to the cross-cutting Technology and AI scope.

**Definition:** an issue belongs here if it carries a Technology and AI theme code (theme group `TECH`) from `taxonomy/themes.csv`. The section adds no new classification of its own.

**Content (a section within `analysis.html`):**
1. **Headline strip:** number of Technology and AI issues, number of countries, split by direction of travel.
2. **Issue-by-country heatmap:** the same component as the regional heatmap, filtered to the theme.
3. **Where governments are making progress:** issues whose direction of travel is `improving` or `largely_resolved`, by country.
4. **Where implementation is lagging:** issues with an `open` gap, or with interventions adopted or implemented but not `in_practice`.
5. **Shared open gaps:** issues with an `open` gap in two or more countries, shown as a count-based pattern list.

**Advisory opportunities.** The tool has no judgement or field for "advisory opportunity", and the front end must not invent one. In the alpha, "shared open gaps" is the closest factual signal. A caption reads: "Shared gaps may indicate where advisory support is relevant. That assessment is made by colleagues, not by the tool."

Also available as a filter preset ("Technology and AI") on every country page.

---

## 9. Navigation and filtering

**Global:**
- header breadcrumb and country switcher on every page;
- every section and issue has a stable link.

**Filters (country page):**

| Filter | Values |
|---|---|
| Theme | Chapter 2, Technology and AI |
| Priority | `High`, `Medium`, `Low`, `insufficient_evidence` |
| Direction of travel | `new`, `worsening`, `persistent`, `improving`, `largely_resolved`, `insufficient_evidence` |
| Unresolved gap | `open`, `partly_addressed`, `largely_closed`, `insufficient_evidence` |
| Status | Validated, Pending review, Proposed, Draft, Not started |
| Comparator analysis | Available / not available |
| Search | Free text across issue names and definitions |

Values are shown to the user through the display labels in section 10.3, not as stored codes. Filters show as removable chips above the results, with a count of matching issues and "Clear all".

Not in the alpha: the "Validated only" switch and the "Present" mode (section 14).

---

## 10. Status and judgement labels

### 10.1 Content status (fixed by `CLAUDE.md`)

| Label | Meaning on screen | Style |
|---|---|---|
| Validated | Passed its gate | Green chip |
| Pending review | Waiting for a gate decision | Amber chip |
| Proposed | Proposed by AI, not yet reviewed | Violet chip |
| Draft | Draft output, not signed off | Blue chip |
| Not started | Not yet produced | Grey outlined chip |

These are the only coloured status chips. No other status words are styled as chips, and nothing is labelled Validated before its gate has passed. A judgement with review status `overridden` is shown as Validated, because the analyst decided it at the gate.

### 10.2 Run status (plain text, derived from the run record and gate log)

Run status is descriptive text, styled differently from the content status chips. The first matching line applies:

| Text | Shown when |
|---|---|
| Not started | No run record for the country |
| Closed: alpha complete | Run closed after G8 (for example the North Macedonia alpha) |
| Outputs signed off | G7 passed, run not closed |
| Judgements validated | G6 passed, G7 not passed |
| In progress: [stage] | Run started; stage from `current_stage` in the run record |

### 10.3 Judgement values

The values are those in `rules/judgement_rules.md` (version 0.5) and `schemas/data_dictionary.md` (version 1.6). The front end never adds or renames values; the display mapping table only gives each stored value a text label, an icon and a colour.

| Judgement | Stored values |
|---|---|
| Direction of travel | `new`, `worsening`, `persistent`, `improving`, `largely_resolved` |
| Unresolved gap | `open`, `partly_addressed`, `largely_closed` |
| Priority, tractability | `High`, `Medium`, `Low` |
| Implementation status | `proposed`, `adopted`, `implemented`, `in_practice`, `reversed`, `unclear` |
| Success | `worked`, `failed`, `mixed`, `too_early` |
| Attribution, comparator relevance | `High`, `Medium`, `Low` |
| Transferability | `likely`, `conditional`, `unlikely` |
| Source quality, evidence confidence, relevance | `High`, `Medium`, `Low` |
| Review status (of a judgement) | `proposed`, `validated`, `overridden` |

Every judgement scale also allows `insufficient_evidence`.

- Display labels are plain renderings of the stored values (for example `partly_addressed` → "Partly addressed", `in_practice` → "In practice", `largely_resolved` → "Largely resolved", `too_early` → "Too early to tell"). Example mapping for direction of travel: improving ↑ green, persistent → grey, worsening ↓ red, new ● neutral, largely resolved ✓ green.
- **`insufficient_evidence`** is a real value, shown as "Insufficient evidence". It always gets its own neutral, hatched style and is never treated as zero, low or missing.
- Every badge carries a text label. Colour is never the only signal.

### 10.4 Issue status

An issue card's content status is set by the review status of its four main judgements (`issue_country` judgements for priority, direction of travel, unresolved gap and tractability), not by priority alone:

- **Validated** when all four that exist are `validated` or `overridden` and their gate (G6) has passed;
- **Proposed** when any of them is `proposed`, or **Pending review** while it is in a gate package awaiting decision;
- **Draft** or **Not started**, following the run's stage, when the issue has no such judgements yet (for example every Moldova issue before G6).

The lowest status among the four applies. The "Flagged for re-review" note is shown separately from the status label whenever any of the four carries a `rereview_flag`; it does not change the status. In North Macedonia this applies to three issue-level judgements set at G7 (priority for RI-FMW-003 and RI-TEC-017, unresolved gap for RI-TEC-033).

---

## 11. Evidence and citation behaviour

- **Hierarchy:** summary, then judgement, then evidence. Evidence is always one click away and never shown by default.
- **Exactness:** quotes appear exactly as recorded. The interface never paraphrases a quote or merges two quotes.
- **Separation:** stated evidence and assessed judgements are always visually distinct, using the explainer's stated and assessed styles.
- **Agent synthesis:** any text recorded as agent synthesis carries that label and the gate at which it was validated.
- **Traceability path:** from any judgement, the user can reach the evidence it relies on, then the quote, page or section, and source details.
- **No file structures:** the interface never shows file paths, folder names, CSV or JSON names, or internal field names. Reference IDs appear only as small muted text in the evidence drawer.
- **Volume:** never more than five evidence items visible at once without a deliberate "Show all".
- **Conflicts:** only validated contradictions are shown, and they are surfaced, never resolved by the interface.
- **Sources outside the page:** links to original documents open the source's `url` from the source register where one is recorded.
- **Printed and exported text:** where a brief is printed or exported, evidence item IDs go in an annex, not the running text, matching `CLAUDE.md`.

---

## 12. Visual hierarchy and interaction principles

**Look and feel.** Follow `tool-explainer.html`:
- the same colour tokens and the six element styles;
- restrained, professional, plenty of white space;
- a policy product, not a developer dashboard.

**Hierarchy on every screen:**
1. One headline answer (the summary).
2. Badges and indicators (the judgements).
3. Expandable detail (the evidence).

**Components (alpha):**
- issue cards;
- priority, tractability and gap badges;
- direction-of-travel arrows;
- content status chips and the re-review note;
- heatmap;
- comparison matrix;
- evidence drawer;
- comparator cards;
- filter chips;
- empty-state panels.

**Interaction principles:**
- Progressive disclosure: open, do not overwhelm.
- One click from summary to judgement; one more click to evidence.
- Every empty state explains itself in one sentence ("No comparator analysis for this issue in this run").
- Readable on a projector: minimum 16px body text, 14px secondary, high contrast.
- Works from 1280px wide upwards for meetings; usable on a tablet; readable on a phone.
- Keyboard accessible; colour never the only signal; respects reduced-motion settings.
- Plain British English. No em dashes. No internal jargon: "evidence item" is acceptable, "JSON", "pass 2" and "tier 3" are not.
- Page weight: the country page embeds only the evidence it shows. The current `analysis/MKD.html` is about 1.7 MB, and the alpha should not grow it substantially.

---

## 13. Alpha build now

The first front-end version works within the existing modules (section 3) and builds, in this order:

1. **Shared visual and design layer:** design tokens from `tool-explainer.html`, the shared header (product name, breadcrumb, country switcher, "How the tool works" link) and the display mapping table (section 10.3), in one shared module.
2. **Improved North Macedonia country product page** (`tools/product_page.py`): the summary layer (section 5.1).
3. **Issue cards and filters** (section 5.2 and section 9), including the Technology and AI filter preset.
4. **Issue detail and analytical-chain view** (sections 6.1 and 6.2).
5. **Evidence drawer** (section 6.3), with validated contradictions only.
6. **Comparator cards and labelled draft policy options** (sections 6.2 and 6.4).
7. **Regional page with country status cards** (`tools/regional_page.py`, section 4), with run status as plain text.
8. **Single-country heatmap state** (section 4).
9. **Technology and AI section and filter** (section 8).
10. **Existing one-issue comparison, restyled** (section 7).
11. **Accuracy, browser and rebuild tests** (section 15), including a check that `index.html`, the closed run's review page and the North Macedonia outputs rebuild unchanged.

All pages are static HTML, generated from the project files by `tools/build_review_page.py` and rebuilt around every gate.

---

## 14. Leave for later, and do not build

**Leave for later:**
- the "Validated only" switch (it adds nothing while North Macedonia is fully validated and Moldova has no judgements before G6);
- "Present" mode;
- comparison by theme;
- compact list view;
- theme and mechanism cards;
- any feature that would need a new analytical field (Appendix B), including an analyst-authored advisory note, which would need a data field and an analyst decision first;
- charts over time (trend lines across years), once more than one run per country exists.

**Do not build:**
- Any server, database, user accounts, logins or permissions.
- Any feature that generates, summarises or rewrites analysis in the browser or at build time, including AI-written country or issue summaries.
- Any combined score that merges source quality, evidence confidence and relevance.
- An "advisory opportunity" label, score or ranking.
- Editing, commenting or gate decisions in the product pages. Decisions stay in the review spreadsheets and the gate log.
- Changes to `index.html`, the analyst review page, beyond the shared header link (already added).
- Exports to PowerPoint or Word, and printable briefing packs.
- Live data feeds, notifications or automatic updates between gates.
- Views of material outside the run's scope, or of runs that have not started.

---

## 15. Acceptance criteria for the first front-end version

**Accuracy and integrity**
1. Every judgement, quote and status shown exists in the project files. A spot check of ten items finds no mismatch.
2. The regional page and cross-country comparison show only validated judgements from countries past G6. Draft or proposed material cannot appear there.
3. No item is labelled Validated unless its gate has a pass or pass-with-conditions row in the gate log.
4. Source quality, evidence confidence and relevance always appear as three separate labels.
5. Every quote matches the recorded text exactly.
6. Validated contradictions linked in the project appear in the evidence drawer for the relevant step, and rejected ones do not.
7. `insufficient_evidence` is displayed as its own value everywhere it occurs.
8. Every judgement value shown is one of the stored values in section 10.3, through its display label.
9. Every piece of agent synthesis carries that label; every policy option carries "Internal draft".
10. Only the five content labels appear as coloured status chips.

**Usability**

11. A first-time senior user can name the top three priority issues for a country within 30 seconds of opening its page.
12. From the regional overview, a user reaches any single piece of evidence in no more than three clicks.
13. No screen shows more than five evidence items or more than twelve heatmap rows without a deliberate "Show all".
14. No file paths, folder names, file formats or internal field names appear anywhere.
15. Every empty state shows a one-sentence explanation.

**Technical**

16. All pages are generated by the single build command `tools/build_review_page.py` from the project files, and rebuild without manual editing.
17. Pages work offline, with no external data calls.
18. Layout works at 1280px and above with no horizontal page scroll, and remains readable on a phone.
19. Every section and every issue has a stable, shareable link.
20. All text and badges meet WCAG AA contrast, and no meaning is carried by colour alone.
21. Rebuilding leaves `index.html`, `review_RUN-2026-01.html` and `outputs/RUN-2026-01/` unchanged apart from build dates and the shared header.

---

## Appendix A: questions resolved from the repository (3 November 2026)

1. **Judgement values:** as in section 10.3, from `rules/judgement_rules.md` 0.5 and `schemas/data_dictionary.md` 1.6. There is no value "better". `largely_resolved`, `largely_closed` and `likely` are allowed but not yet used in any validated judgement.
2. **Summary text:** every judgement records a `reason` of one to three sentences, validated with the judgement; the priority reason supplies the short assessment on issue cards (median about 310 characters, so it is shown in full or truncated visually). There is no analyst-written country or issue summary. The country Summary and each issue's "In brief" and "How the EU requirement has changed" are agent synthesis, held in `review/<run_id>/stage12/narrative/` and signed off at G7 through the run outputs.
3. **EU requirements per issue:** each EU requirement is an evidence item whose recorded chain link is `eu_requirement`, tagged with one or more reform issues. In North Macedonia an issue has between 2 and 116 such items (median 14). No single short form exists, so cards use the taxonomy definition plus counts and years (section 5.2).
4. **Country codes:** three capital letters from `tools/common.py` and the data dictionary (`MKD`, `MDA`, `MNE`, and `XKX` for Kosovo); pages are `analysis/<code>.html`.
5. **Issue status:** set by the review status of the four main issue judgements, with the re-review flag shown separately (section 10.4).

## Appendix B: data the project does not store

The interface is designed around existing data and adds no analytical fields for display purposes. The project does **not** currently store:

- **analyst-written overall country assessments:** the country summary is agent synthesis validated at G7 (section 5.1);
- **a single one-line EU requirement per issue:** cards use the taxonomy definition plus counts (section 5.2);
- **an advisory-opportunity field:** none is shown (section 8);
- **a one-line "what was done" field for comparator cases:** cards use the recorded `description`, truncated visually (section 6.4);
- **direct reform-issue IDs on older North Macedonia intervention records:** `reform_issue_ids` was added in data dictionary 1.5 and is blank for RUN-2026-01 interventions, so their link to an issue is taken through the evidence items that name both, as the run outputs already do.
