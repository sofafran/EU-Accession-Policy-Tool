# EU Accession Reform Intelligence Tool | Matching considerations

Version 1.1, 23 October 2026. Revised after the architecture review (decisions B1, B2, D4 and D5).

This codebook defines how the information in the tool should **connect** so that users can explore the same evidence base from different starting points.

The tool should not treat assessments, reforms, outcomes, lessons and other information as isolated records. Each piece of information should carry consistent identifiers that allow it to be connected to related evidence and retrieved in different ways.

A user should be able to start with a **country**. Selecting Serbia, for example, should bring together the relevant EU assessments, government responses, implementation evidence, outcomes, lessons and **comparator cases** connected to Serbia.

A user should also be able to start with a **theme, cluster, chapter or policy area**. Selecting energy, for example, should eventually allow the tool to look horizontally across all countries covered by the system and retrieve the relevant **assessments, reforms, outcomes and lessons** associated with energy. In practice, a theme lookup uses the cluster and chapter structure of the accession negotiations: energy, for example, corresponds mainly to Chapter 15 in Cluster 4. Themes that cut across chapters can be added later as a controlled list of tags.

The same principle should apply to a specific **reform issue**. Different countries may describe the same underlying problem using different language, so the tool should connect information that relates to the same reform issue while preserving the original wording and country context.

This depends on a reform-issue taxonomy: a controlled list that every evidence item can be linked to. It has two levels:

- **Reform issues:** specific problems, drafted by the agent from the EU requirements found in the sources and approved by the analyst. An issue should be specific enough that a single EU requirement maps clearly to it, and general enough that another country could plausibly face the same issue. Reform issue IDs carry no country code, so the same issue can be found across countries.
- **Problem mechanisms:** a short fixed list of underlying reasons why reforms stall, such as a legal gap, weak enforcement, lack of institutional independence or vested interests. Two countries can describe an issue differently but share the same mechanism, which is what makes comparison and transferability possible.

The taxonomy is a living file with version numbers. The agent may propose a new issue when evidence fits none of the existing ones, but only the analyst can add, merge, split or retire issues. Retired IDs are never reused, and each new version of the taxonomy triggers a re-run of classification for the evidence affected by the change.

Information should also connect across **time**, allowing the tool to follow how the same issue develops across several years and link assessments, reforms and outcomes. To do this reliably, the publication date of a document, the period it covers and the date of the event described are recorded separately.

To make these lookups possible, every evidence item carries the following matching fields. Each takes its value from a controlled list or an ID rather than free text:

- **Country and role (target or comparator)**
- **Dates (publication, period covered, event)**
- **Source**
- **Cluster**
- **Chapter**
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
