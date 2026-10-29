# EU Accession Reform Intelligence Tool | Assessment

Version 1.2, 29 October 2026. Made country-neutral when the pilot was reconfigured before gate G0 (decision F2). Version 1.1 followed the architecture review (decisions B1, B3, C4 and E2).

This codebook defines the kinds of **judgement** the tool should eventually be able to make about the information it has extracted and connected.

The purpose is not to create a single scoring system. It is to set out the main questions future agents answer when they make judgements about individual pieces of evidence, interventions, outcomes or lessons, and the simple scales they use.

In this project, an assessment made by the EU is a finding recorded from a source. The judgements in this codebook are conclusions reached by the tool or the analyst. The two are always stored separately.

The tool should keep different types of judgement separate.

The main judgements, what each is attached to, and the scale each uses are:

- **Source quality:** how credible and authoritative is the source for this particular topic? Attached to a source, for a given chapter or theme. Rated High, Medium or Low.
- **Evidence confidence:** how strongly does the available evidence support the specific claim? Attached to an evidence item. Rated High, Medium or Low.
- **Relevance:** how applicable is this evidence to a specific reform issue in the target country? Attached to an evidence item for a given reform issue. Rated High, Medium or Low.
- **Implementation status:** has an action been proposed, adopted, implemented or actually used in practice? Attached to an intervention at a given date. Rated proposed, adopted, implemented, in practice, reversed or unclear.
- **Direction of travel:** is the issue new, worsening, persistent, improving or largely resolved? Attached to a reform issue in a country over time.
- **Unresolved gap:** what does the EU still require that has not been achieved? Attached to a reform issue in a country. Rated open, partly addressed or largely closed, with a short description of what remains.
- **Success or result:** did the intervention appear to work, fail, produce mixed results or remain too early to judge? Attached to the link between an intervention and an outcome.
- **Attribution:** how confident are we that the intervention contributed to the observed outcome? Attached to the same link. Rated High, Medium or Low.
- **Comparator relevance:** how closely does another country’s experience match the problem being analysed? Attached to a pair: a target-country reform issue and a comparator case. Rated High, Medium or Low.
- **Transferability:** could the underlying mechanism realistically work in the target country? Attached to a lesson, applied to the target country. Rated likely, conditional or unlikely, with the conditions stated.
- **Priority and tractability:** how important is the issue for accession and how realistic is it for government to make progress? Attached to a reform issue in a country. Priority and tractability are each rated High, Medium or Low.

Every scale also allows "insufficient evidence". The agent should use it rather than force a rating.

Source quality should not be based only on the general **reputation** of an institution. The agent marks six factors and then gives an overall rating with a one-line reason: traceability (is the document available, and can its claims be traced to a page or dataset?), topic expertise or mandate (does this institution specialise in, or have a mandate for, this topic?), method transparency, primary versus secondary evidence, independence from the subject (is it reporting on its own performance?), and recency where relevant. Institutional standing is considered through expertise and mandate for the specific topic, not as general reputation.

A specialist organisation may therefore be highly authoritative for one topic and much less useful for another.

Evidence confidence is High when a claim is stated directly and specifically and is either corroborated by independent evidence or uncontested. It is Medium when the claim is stated directly but is general, uncorroborated, comes from a weaker source or relies on machine translation. It is Low when the claim is inferred rather than stated, is vague, or is contradicted by stronger evidence. Source quality is one input but does not decide confidence on its own.

Relevance is High when the evidence concerns the same country and the same reform issue. It is Medium when it concerns the same issue in a comparable country, or an adjacent issue in the same country. It is Low when the connection is only general.

These judgements should be applied to the **object they actually describe**, not only to whole documents. A single report may contain a strong factual finding, a weaker explanation and a lesson that is only partly relevant to the target country.

The agent should be able to provide a **first-cut assessment and a short explanation** of why it reached that view, while preserving uncertainty where evidence is weak, incomplete or conflicting.

Every judgement record states its value, a short reason, the evidence items it relies on, who made it (the agent or a named analyst), its review status (proposed, validated or overridden) and the codebook version used. A judgement validated or overridden by the analyst is never overwritten by a later run; it is flagged for re-review instead.

The agent may make first-cut ratings of source quality, evidence confidence, relevance and uncontested implementation status, which the analyst reviews in bulk or by exception. All other judgements (direction of travel, unresolved gap, success, attribution, comparator relevance, transferability, priority and tractability) remain proposals until the analyst validates them. For the first run, analytical validation is carried out by the two reviewers named in the run record.

The overall principle is:

- **Assess the source**
- **Assess the evidence**
- **Assess what happened**
- **Assess how relevant and transferable it is**
- **Explain the judgement**
- **Leave the important calls to the analyst**
