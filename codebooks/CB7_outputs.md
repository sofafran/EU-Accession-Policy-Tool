# EU Accession Reform Intelligence Tool | Outputs

Version 1.1, 29 October 2026. Made country-neutral, with cross-cutting themes added to the scope overview and a review page added, when the pilot was reconfigured before gate G0 (decisions A6, E7 and F2). Version 1.0 was added after the architecture review (decision E4).

This codebook defines what the tool produces from the evidence it has extracted, connected and assessed, and the rules those outputs must follow. The other codebooks describe how evidence enters the system and how it is judged; this one describes how it leaves.

The first run is an alpha: a test of the methodology rather than of a full user interface. Its outputs are therefore internal analyst products, written in plain language and stored as files. An interactive dashboard offering the country view and thematic view described in Codebook 1 can be built later from the same files once the data structure has proved itself.

Reviewers follow the run through a single static review page, `index.html`, generated from the project files. The page shows validated material and relevant work in progress side by side, each with one of five labels: **Validated** (passed its gate), **Pending review** (in a gate package awaiting decision), **Proposed** (an agent proposal not yet in a gate package), **Draft** (unfinished work) and **Not started**. The page is a review interface only; gate decisions are made in the review spreadsheets and recorded in the gate log. The usefulness of the page is itself one of the things the alpha tests.

## Principles for every output

- **Traceable:** every statement of fact or judgement can be traced to the evidence items and sources behind it. Internal outputs cite evidence item IDs in an annex or footnote, not in the running text.
- **Stated and assessed kept apart:** an output shows what sources say separately from what the tool or analyst concludes. Adoption is never presented as success.
- **Three judgements visible:** where evidence is presented, source quality, evidence confidence and relevance are shown side by side and never merged into a single score.
- **No more certain than the evidence:** uncertainty, gaps and conflicting evidence are reported, not smoothed over. "Insufficient evidence" is a legitimate finding.
- **Limits stated:** each output says what it does not cover, including the scope of the run and any reliance on machine translation.
- **Validated before use:** an output may only include judgements that have passed the analytical validation gate. Anything still a proposal is labelled as such, in the outputs and on the review page.

## Outputs of the first run

- **Scope overview:** the reform issues identified for the target country across the in-scope chapters and cross-cutting themes, grouped by chapter and theme, with direction of travel, unresolved gap, priority and tractability for each, and a short note on evidence coverage.
- **Issue briefs:** one brief per reform issue, following the analytical chain: the EU requirement and how its wording has changed over the time window, the country response, implementation, outcomes, the unresolved gap, direction of travel and priority. Each brief includes a table of the key evidence with its three judgements, any conflicting evidence, and open questions.
- **Source coverage and limits report:** which source requirements were met and which were not, what was excluded and why, which documents were inaccessible, how much of the analysis relies on machine translation, and the methodological limitations found during testing.
- **Run review:** what the agent got wrong and how often, what happened at each control gate, the changes proposed for the codebooks, rules and taxonomy before the next run, and readiness for scaling, drawn from the alpha learning log.
- **Review page:** the single page through which reviewers follow the run; updated at every gate.
- **Comparator briefs and draft policy options (run 1b only):** for the two or three issues selected for the comparator pilot, the comparator cases and how closely they match, what was done, what happened and why, which lessons are transferable and under what conditions, and draft policy options.

## Rules for policy options

A policy option may only be drafted for a reform issue that has a validated unresolved gap and validated comparator evidence. Each option must state:

- the target-country reform issue and the gap it addresses;
- the problem mechanism it targets;
- the comparator evidence and lessons it draws on, with their transferability judgement and conditions;
- the main risks and preconditions;
- which institution in the target country would need to act.

A reform is never proposed simply because another country adopted it. Draft options are internal and are labelled as drafts until both reviewers named in the run record have signed them off at the outputs gate.

## Format

First-run outputs are written as Markdown files in the outputs folder for the run, in plain British English, without em dashes. If any output is later adapted for a client or government audience, it is rewritten at a high level, with references moved out of the body text into an annex, and it is signed off again before it is shared.
