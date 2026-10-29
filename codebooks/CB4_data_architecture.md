# EU Accession Reform Intelligence Tool | Data architecture

Version 1.2, 29 October 2026. Made country-neutral, with scope and theme tags added to the first pass, when the pilot was reconfigured before gate G0 (decisions D6 and F2). Version 1.1 followed the architecture review (decisions B2, C1, C2, C3, D1, D2, D3 and E1).

This codebook defines how source documents should be prepared, parsed and converted into structured information that can later be matched and assessed.

Before parsing begins, the required source documents should first be brought into a consistent and usable form. This may include PDFs, webpages or other document types. They should be saved in a folder for each country and source family, with the original file kept untouched next to a converted text version that preserves page numbers. Each file is named with its source ID followed by a short readable label, so that the source universe can be reviewed before any deeper processing takes place.

A master source register records what has been collected, where it came from, when it was retrieved, whether it is usable and which source requirement it satisfies (see Codebook 2). Every source receives a permanent ID that is never changed or reused, made of the country code, the source family, the publication year and a running number: for example, the first EU document from 2025 about a country with the code CCC is CCC-EU-2025-001.

Only after this source set has been reviewed and approved by the analyst should parsing begin.

Parsing means breaking the documents into evidence items. An evidence item is one claim, of one information type, with its exact quote and location. If a sentence contains both a finding and a recommendation, it produces two items. The main types of information to extract should include:

- **Assessment or finding: a judgement about a country, reform area or current situation.**
- **Recommendation or expectation: something the EU, government or another institution says should happen next.**
- **Reform action or intervention: something proposed, adopted or implemented.**
- **Status: where that action currently sits, as stated by the source. This stated status is kept separate from the status the tool later assesses.**
- **Date or milestone: when an assessment, action or outcome occurred. Three dates are kept apart: when the document was published, the period it covers, and when the event itself happened.**
- **Actor or institution: who is responsible for or involved. The tool records separately who is speaking, for example the European Commission, and who the claim is about, for example a national ministry.**
- **Problem or barrier: evidence about what is preventing progress.**
- **Outcome or result: what happened after an intervention.**
- **Lesson: what appears to have worked, failed or mattered.**
- **Evidence or metric: information supporting an assessment or result.**
- **Source reference: where the information came from.**

Seven of these are types of claim: assessment or finding, recommendation or expectation, reform action or intervention, problem or barrier, outcome or result, lesson, and evidence or metric. The other four (status, date, actor and source reference) are recorded as details on every item rather than as items of their own.

Different source types are likely to contain different combinations of these information types, but these should remain expected patterns rather than rigid rules. A lesson, assessment or outcome may appear in more than one source family.

The system should distinguish between what the information is and where it came from.

Each evidence item receives a permanent ID made of its source ID and a running number, for example CCC-EU-2025-001-0042, so that every piece of evidence can always be traced back to its document.

The structured information is stored in two formats. Anything a person reviews or edits is a CSV table: the source register, the limits log, the taxonomy, the lists of interventions and actors, the links and the judgements. The evidence items extracted from each source are stored as one JSON file per source document, because a single item can hold lists, such as several actors or reform issues. At each review point the agent exports the items to a spreadsheet, so that the analyst never needs to read raw JSON. Any database or search index used later is rebuilt from these files and is never the master copy.

Besides sources and evidence items, the data has three further layers: analytical entities that are recorded once and referenced by many items (reform issues, interventions, actors and comparator cases), links between records (for example one item corroborating or contradicting another, or an intervention leading to an outcome), and judgements (see Codebook 6).

Parsing happens in two passes. The first pass, extraction, stays close to the text: information type, exact quote, location, dates, actors, stated status, and tags given by the structure of the document, such as a chapter heading, together with why the item is in scope (its chapter, a cross-cutting theme it materially concerns, or an explicit connection to an issue already in scope). The second pass, classification, adds the interpretive layer: reform issue, problem mechanism, links to interventions and actors, and links between items. Keeping the passes apart means a change to the taxonomy only requires classification to be re-run, not the documents to be read again.

Before the complete evidence base is parsed, the agent should process a small representative sample first: about ten to twelve documents covering all five source families, including Commission reports from early, middle and recent years, one document not in English where such documents are approved, and one difficult format. Before seeing the agent's output, the analyst hand-codes three short passages, so that missed items can be found as well as wrong ones. The agent automatically checks that every quote appears word for word at the cited location. The extracted information should then be reviewed to test whether the agent is identifying the right kinds of insights and interpreting them correctly.

If problems are found, the parsing instructions should be updated before the system processes the full evidence base. If the sample still fails after two rounds of refinement, the rules are reconsidered rather than patched further.

After the sample is approved, the EU sources are parsed first, because the reform-issue taxonomy is drafted from the EU requirements (see Codebook 5). The remaining sources are parsed once the taxonomy is approved.

The overall process is:

- **Identify the required sources**
- **Collect and organize sources**
- **Review the source set**
- **Parse a sample**
- **Review what is being extracted**
- **Refine the rules**
- **Parse the EU sources and draft the taxonomy**
- **Parse the full evidence base.**
- **Classify and link the evidence**
