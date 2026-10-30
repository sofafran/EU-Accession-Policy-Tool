# Procedure P4: Comparator pilot, run 1b

Read this file before starting the comparator pilot. It applies only to the two or three reform issues chosen at G6. It reuses stages 1 to 11 on a small scale, with gates marked with the suffix `b` (G1b, G2b, G5b, G6b) in the gate log. Follow "Around every gate" in procedure P1 for the learning log and the review page; comparator material appears in its own section of the page.

## Step 1: Record the expansion

Add a limits log entry stating that comparator evidence is being gathered for the named issues only, as a deliberate expansion approved at G6, with no full country model.

## Step 2: Choose comparator countries (gate G1b)

For each selected issue, propose two or three comparator countries, with a reason for each:

- the same or a closely similar reform issue appears in that country's EU reports, ideally with the same mechanism;
- the country has attempted a reform on it, with some evidence of what happened;
- evidence is likely to be available in English.

Candidates include other accession countries and recent member states. Propose comparator source requirement lines (`role` `comparator`) in `registers/source_requirements.csv`. The analyst approves countries and lines at G1b.

## Step 3: Acquire and register (gate G2b)

Follow stages 2 to 4 of procedure P1, filing documents under `sources/<country code>/<family>/`. Comparator documents are registered with `role` `comparator`. Present a short G2b package.

## Step 4: Extract and classify (gate G5b)

- Extract with the approved extraction rules. There is no new sample loop, but the first two comparator sources are spot-checked in full at G5b.
- Classify against the same taxonomy. Comparator items that fit no approved issue go to the unmatched queue; do not stretch a target-country issue to fit them.
- Create comparator case records in `entities/comparator_cases.csv`, one per country and issue.

## Step 5: Judge (gate G6b)

Propose, with reasons and evidence:

- comparator relevance for each case (how closely it matches the target-country issue and its mechanisms, and how the context differs);
- implementation status, success and attribution for the comparator interventions;
- lessons stated by sources, and transferability of each lesson to the target country, with conditions.

**G6b decision (the reviewer or reviewers named in the run record):** validate or override. Only validated cases and lessons may be used for draft policy options.
