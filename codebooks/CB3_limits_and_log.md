# EU Accession Reform Intelligence Tool | Limits

Version 1.1, 23 October 2026. Revised after the architecture review (decisions A1, A2, A3, A4, C2, E2 and E3).

This codebook defines the initial limits of the tool, what is deliberately excluded, and how those limits should change as the model develops.

The first operational version of the tool will focus on **Serbia** and on **Chapter 5 (Public procurement)** only. Serbia should be treated as the first test case for a methodology that is intended to become reusable across other accession countries.

Other countries may later be introduced as comparator cases or full country models, but the system should not expand beyond the agreed Serbia scope automatically.

The one deliberate exception in the first run is the comparator pilot (run 1b). For two or three Serbia reform issues selected by the analyst at the analytical validation gate, the tool gathers targeted evidence from comparator countries. This evidence is tagged as comparator material, does not create a full country model, and is recorded in the limits log as a deliberate expansion.

The first version should recognise several types of limit:

- **Country scope:** Serbia only for the first full run, plus targeted comparator evidence for the run 1b pilot.
- **Thematic scope:** one chapter for the first run, Chapter 5 (Public procurement). Further chapters, starting with Chapter 15 (Energy) and a rule-of-law sub-area of Chapter 23, are deferred until the first run has been tested.
- **Time scope:** evidence from 2014, when Serbia's accession negotiations opened, up to a fixed evidence freeze date set at the start of each run. Older documents are used only by logged exception, for example to explain the origin of an issue that is still open.
- **Evidence scope:** not every theoretically useful document will necessarily be available or retrievable.
- **Accessibility:** sources that cannot be obtained reliably or in a usable format should be recorded rather than silently ignored. Paywalls and logins are never bypassed.
- **Language:** English is the primary language. Serbian-language documents are used only where they are core and no English version exists. Machine translations are flagged and capped at Medium confidence, because no Serbian-speaking reviewer is available for the first run.
- **Analytical scope:** AI can support extraction, matching and first-cut assessment, but important analytical judgements remain subject to human review at the control gates set out in the architecture and procedures.
- **Methodological scope:** the initial taxonomy, matching rules and assessment categories should remain open to revision after testing.

The tool keeps two records of what is included and excluded. The master source register lists every document ever considered, including those that turned out to be inaccessible, excluded, duplicated or superseded, with the reason. The limits log records limits that are not about a single document, such as scope boundaries and methodological issues found during testing. Each entry records what was limited or excluded, why, whether the limitation is temporary or permanent, who decided, and when it should be revisited.

Examples include:

- **Document unavailable**
- **Outside current country scope**
- **Outside agreed time period**
- **Inaccessible format**
- **Duplicate source**
- **Insufficient relevance**
- **Machine translation only**
- **Methodological issue identified during review**

The system should also be designed so that future runs can reuse the established scope, exclusions and previous results rather than restarting from the beginning each time.

Each run has a run record stating its scope, its evidence freeze date, its reviewers and the versions of the codebooks, parsing rules and taxonomy it used. Every extracted item and judgement records the versions that produced it. When a new run starts, the tool distinguishes between:

- **Material already processed:** documents whose file fingerprint is unchanged are reused as they are.
- **New documents:** for example the next annual Commission report, which are registered and processed.
- **Updated versions of existing documents:** registered as new sources linked to the earlier version. The earlier version is marked as superseded but kept, because the history matters for direction of travel.
- **Changes to the codebooks or rules:** only the affected material is reprocessed. A change to the taxonomy re-runs classification; a change to the parsing rules re-extracts the affected sources.
- **Validated judgements:** judgements validated or overridden by the analyst are never overwritten. If new evidence or new rules affect them, they are flagged for re-review.

After the first complete Serbia run, the limits and log should be reviewed to capture what was learned and what needs to change before the next run or country is added. The agent drafts a run review covering error patterns, gaps and proposed changes. The analyst approves any changes, which then become a new version of the codebooks before the next run starts.

The system should never start a new run or widen its scope on its own. Automatic checks for new documents may be added later, but they may only propose a new run.

The overall approach is:

- **Start with Serbia**
- **Record what is included and excluded**
- **Test the model**
- **Learn from the first run**
- **Refine the limits**
- **Expand deliberately**
