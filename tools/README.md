# Helper tools (to be built at stage 0)

These small scripts do the mechanical, repeatable work so that the agent does not do it by hand. None exists yet: building them is the first implementation task, at stage 0, before gate G0. Each must be tested on a small sample and its version recorded in the run record.

Write them in Python, keep each one short and single-purpose, and give each a `--help` description.

| Tool | What it does | Used in |
|---|---|---|
| `hash_file.py` | Computes the SHA-256 fingerprint of a file. | Stage 2 |
| `next_id.py` | Returns the next free ID of a given type by reading the relevant CSV or evidence folder. Never reuses an ID. | All stages |
| `convert_to_text.py` | Converts PDF, HTML, DOCX and XLSX originals to text, writing `=== PAGE n ===` before each page and keeping headings. Uses text recognition for scanned PDFs and reports when it did. | Stage 2 |
| `verify_quotes.py` | Checks that every `stated_text` in an evidence file appears word for word at the cited location of the text file (the page for paged documents, the section for webpages), ignoring only differences in whitespace and line-break hyphenation. Sets `quote_verified` and writes a report. | Stages 5, 7, 8 and run 1b |
| `validate_data.py` | Checks evidence files against `schemas/evidence_item.schema.json`, checks CSV headers against the data dictionary, checks that IDs are unique and that every ID referred to exists, and warns if the value, reason or review status of a validated or overridden judgement has changed. | Before every gate |
| `export_review.py` | Builds the review spreadsheets for each gate from the CSV and JSON files, so the analyst never reads raw JSON. | Every gate |

Later, not in run 1: `build_index.py`, which builds a search index or small database from the files for the country and thematic views. It must always be rebuildable from the files and is never the master copy.
