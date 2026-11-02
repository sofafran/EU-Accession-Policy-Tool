# EU Accession Reform Intelligence Tool | Matching considerations

Version 1.3, 2 November 2026. Approved changes PC-01 to PC-17 from G8 of RUN-2026-01 (GATE-0013) applied before RUN-2026-02, with the multi-country rollout (decision E19): one taxonomy shared across countries, and problems raised only by national or independent sources (PC-12). Version 1.2, 29 October 2026. Made country-neutral, with cross-cutting themes brought forward from a later stage, when the pilot was reconfigured before gate G0 (decisions D6 and F2). Version 1.1 followed the architecture review (decisions B1, B2, D4 and D5).

This codebook defines how the information in the tool should **connect** so that users can explore the same evidence base from different starting points.

The tool should not treat assessments, reforms, outcomes, lessons and other information as isolated records. Each piece of information should carry consistent identifiers that allow it to be connected to related evidence and retrieved in different ways.

A user should be able to start with a **country**. Selecting a country should bring together the relevant EU assessments, government responses, implementation evidence, outcomes, lessons and **comparator cases** connected to it.

A user should also be able to start with a **theme, cluster, chapter or policy area**. Selecting energy, for example, should eventually allow the tool to look horizontally across all countries covered by the system and retrieve the relevant **assessments, reforms, outcomes and lessons** associated with energy. In practice, a theme lookup uses the cluster and chapter structure of the accession negotiations: energy, for example, corresponds mainly to Chapter 15 in Cluster 4. Themes that cut across chapters, such as technology and AI, are handled through a controlled list of theme codes in `taxonomy/themes.csv`, each with a definition and a materiality test. Every evidence item carries the theme codes it materially concerns, so a theme lookup works across chapters and countries. Only the analyst can add, change or retire a theme.

The same principle should apply to a specific **reform issue**. Different countries may describe the same underlying problem using different language, so the tool should connect information that relates to the same reform issue while preserving the original wording and country context.

This depends on a reform-issue taxonomy: a controlled list that every evidence item can be linked to. It has two levels:

- **Reform issues:** specific problems, drafted by the agent from the EU requirements found in the sources and approved by the analyst. An issue should be specific enough that a single EU requirement maps clearly to it, and general enough that another country could plausibly face the same issue. Reform issue IDs carry no country code, so the same issue can be found across countries.
- **Problem mechanisms:** a short fixed list of underlying reasons why reforms stall, such as a legal gap, weak enforcement, lack of institutional independence or vested interests. Two countries can describe an issue differently but share the same mechanism, which is what makes comparison and transferability possible.

The taxonomy is a living file with version numbers. The agent may propose a new issue when evidence fits none of the existing ones, but only the analyst can add, merge, split or retire issues. Retired IDs are never reused, and each new version of the taxonomy triggers a re-run of classification for the evidence affected by the change. The evidence of a closed run keeps the taxonomy version it was classified with.

The taxonomy is shared by all countries, which is what makes comparison possible. A country's evidence is assigned to an existing issue only where the issue's definition genuinely fits; it is never stretched to fit an issue first defined from another country's evidence. Evidence that fits no issue goes to the unmatched queue and may lead to a new shared issue, proposed at the run's taxonomy or classification gate.

Issues are usually derived from EU requirements. A problem raised only by national or independent sources may also be proposed as an issue when it falls within the scope and more than one source raises it. Its definition states that the EU material does not raise it, that origin is shown wherever the issue is reported, and under the judgement rules such evidence never raises priority on its own.

Information should also connect across **time**, allowing the tool to follow how the same issue develops across several years and link assessments, reforms and outcomes. To do this reliably, the publication date of a document, the period it covers and the date of the event described are recorded separately.

To make these lookups possible, every evidence item carries the following matching fields. Each takes its value from a controlled list or an ID rather than free text:

- **Country and role (target or comparator)**
- **Dates (publication, period covered, event)**
- **Source**
- **Cluster**
- **Chapter**
- **Theme**
- **Information type and chain link**
- **Reform issue**
- **Problem mechanism**
- **Intervention**
- **Actor / institution (speaker and subject)**

Free-text keywords are not used as matching fields because they drift over time; searching the stored exact quotes covers that need. The principle remains that each evidence item should carry enough structured information to support both lookup and cross-comparison.

Where evidence allows, the tool should also connect information along the analytical chain set out in Codebook 1:

- **EU requirement**
- **Reform issue**
- **Country response**
- **Implementation**
- **Outcome**
- **Unresolved gap**
- **Comparator evidence**
- **Lesson**
- **Priority**
- **Policy option**

These connections are recorded as links between records. Besides links along the chain, the tool records when one item corroborates or contradicts another, so that conflicting evidence is preserved rather than resolved silently, as Codebook 2 requires.
