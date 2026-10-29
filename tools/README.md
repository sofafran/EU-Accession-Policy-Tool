# Helper tools

These small scripts do the mechanical, repeatable work so that the agent does not do it by hand. They were built and tested at stage 0 of RUN-2026-01 (29 Oct 2026); their versions are recorded in the run record. Each prints its purpose with `--help` and its version with `--version`.

**Set-up:** `pip install -r tools/requirements.txt`, plus the system packages listed at the top of that file (Tesseract with the English, Macedonian and Albanian language data, and Poppler). Shared helpers are in `tools/common.py`.

**Tests:** `python3 tools/tests/test_tools.py --report tools/tests/last_report.csv` runs every tool on small generated samples in a temporary copy of the project; it never touches the real data. Run it after any change to a tool and before each gate, and record the result in the run record.

To build or change a tool: test it on a small sample and record its version in the run record.

Write them in Python, keep each one short and single-purpose, and give each a `--help` description.

| Tool | What it does | Used in |
|---|---|---|
| `hash_file.py` | Computes the SHA-256 fingerprint of a file. | Stage 2 |
| `next_id.py` | Returns the next free ID of a given type by reading the relevant CSV or evidence folder. Never reuses an ID. | All stages |
| `convert_to_text.py` | Converts PDF, HTML, DOCX and XLSX originals to text, writing `=== PAGE n ===` before each page and keeping headings. Uses text recognition for scanned PDFs, in the languages listed in the run record (including Cyrillic scripts where needed), and reports when it did. | Stage 2 |
| `verify_quotes.py` | Checks that every `stated_text` in an evidence file appears word for word at the cited location of the text file (the page for paged documents, the section for webpages), ignoring only differences in whitespace, line-break hyphenation and Unicode normalisation form (both texts are compared in NFC). It must not treat Latin and Cyrillic letters that look alike as equal. Sets `quote_verified` and writes a report. | Stages 5, 7, 8 and run 1b |
| `validate_data.py` | Checks evidence files against `schemas/evidence_item.schema.json`, checks CSV headers against the data dictionary, checks that IDs are unique and that every ID referred to exists, checks theme codes against `taxonomy/themes.csv`, and warns if the value, reason or review status of a validated or overridden judgement has changed. | Before every gate |
| `export_review.py` | Builds the review spreadsheets for each gate from the CSV and JSON files, so the analyst never reads raw JSON. Version 1.1.0 builds the G0, G1 and G2 packages and the stage 5 hand-coding workbook (`G3-handcoding`), which reads `review/<run_id>/G3_sample.csv` (source_id, pages, reason) and `review/<run_id>/G3_passages.csv` (passage_id, source_id, page, start_text, end_text, why). Sheets for later gates are added and tested before those gates, when there is data to test them on. | Every gate |
| `build_review_page.py` | Regenerates `index.html` and the analysis mock-up `analysis.html` (linked from it) from the run record, gate log, limits log, registers, taxonomy, judgements, outputs and alpha learning log. Writes one self-contained file (inline styles, no external scripts or fonts, data embedded) so it works offline and on GitHub Pages. Assigns each item a status label (`Validated`, `Pending review`, `Proposed`, `Draft`, `Not started`) from the gate log and review status, never from its own judgement. Shows no content that is not in the project files. | When a gate package is prepared and after every gate decision |

Later, not in run 1: `build_index.py`, which builds a search index or small database from the files for the country and thematic views. It must always be rebuildable from the files and is never the master copy.
