#!/usr/bin/env python3
"""Stage 0 tests for the helper tools, run on small generated sample files in a temporary copy of the project.

Usage: python3 tools/tests/test_tools.py [--report tools/tests/last_report.csv]
Never touches the real project data: everything runs in a temporary folder.
"""

import argparse
import csv
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
COPY = ["schemas", "registers", "taxonomy", "entities", "links", "judgements", "runs", "decisions", "tools", "ARCHITECTURE.md"]
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
results = []


def check(tool, name, ok, detail=""):
    results.append((tool, name, "pass" if ok else "fail", detail))
    print(f"{'PASS' if ok else 'FAIL'}  {tool}: {name}" + (f"  ({detail})" if detail and not ok else ""))


def run(proj, tool, *args):
    return subprocess.run([sys.executable, str(proj / "tools" / tool), *args, *(["--root", str(proj)] if tool not in ("hash_file.py", "convert_to_text.py") else [])],
                          capture_output=True, text=True)


def minimal_pdf(pages):
    """A small text PDF with Helvetica, one string per line. Enough for text extraction tests."""
    objs = ["<< /Type /Catalog /Pages 2 0 R >>", None, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    kids = []
    for lines in pages:
        stream = "BT /F1 11 Tf 50 750 Td 14 TL " + " ".join(f"({l}) Tj T*" for l in lines) + " ET"
        objs.append(f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream")
        objs.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents {len(objs)} 0 R >>")
        kids.append(len(objs))
    objs[1] = f"<< /Type /Pages /Kids [{' '.join(f'{k} 0 R' for k in kids)}] /Count {len(kids)} >>"
    out, offsets = "%PDF-1.4\n", []
    for i, o in enumerate(objs, start=1):
        offsets.append(len(out.encode("latin-1")))
        out += f"{i} 0 obj\n{o}\nendobj\n"
    xref = len(out.encode("latin-1"))
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n" + "".join(f"{o:010d} 00000 n \n" for o in offsets)
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    return out.encode("latin-1")


def image_pdf(heading):
    """One page with a short text heading over an image body: the layout that hid text in ALN-0021."""
    stream = f"BT /F1 14 Tf 50 750 Td ({heading}) Tj ET q 500 0 0 600 50 100 cm /Im1 Do Q"
    objs = ["<< /Type /Catalog /Pages 2 0 R >>", "<< /Type /Pages /Kids [5 0 R] /Count 1 >>",
            "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            "<< /Type /XObject /Subtype /Image /Width 1 /Height 1 /ColorSpace /DeviceGray /BitsPerComponent 8 /Length 1 >>\nstream\n\x80\nendstream",
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> /XObject << /Im1 4 0 R >> >> /Contents 6 0 R >>",
            f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream"]
    out, offsets = "%PDF-1.4\n", []
    for i, o in enumerate(objs, start=1):
        offsets.append(len(out.encode("latin-1")))
        out += f"{i} 0 obj\n{o}\nendobj\n"
    xref = len(out.encode("latin-1"))
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n" + "".join(f"{o:010d} 00000 n \n" for o in offsets)
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    return out.encode("latin-1")


def scanned_pdf(path, lines):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (2480, 1200), "white")
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, 56)
    for i, line in enumerate(lines):
        d.text((120, 150 + i * 110), line, fill="black", font=font)
    img.save(path, "PDF", resolution=300)


def evidence(sid, items):
    return {"source_id": sid,
            "extraction": {"run_id": "RUN-2026-01", "rules_version": "0.1b", "extracted_at": "2026-10-29", "status": "sample",
                           "codebook_version": "1.2", "themes_version": "1.0"},
            "classification": {"status": "not_started"},
            "items": items}


def item(iid, quote, page=None, section=None, themes=None, basis=None):
    return {"item_id": iid, "information_type": "finding", "stated_text": quote, "quote_language": "en", "translation_en": None,
            "machine_translated": False, "summary": "Test item.", "location": {"page": page, "page_end": None, "section": section,
                                                                              "paragraph": None, "snapshot_file": None},
            "quote_verified": False, "country": "MKD", "role": "target", "cluster": "2", "chapter": "02",
            "scope_basis": basis or ["chapter"], "themes": themes or [],
            "dates": {"publication_date": "2025-11", "period_covered": None, "event_date": None, "event_date_precision": None},
            "speaker": {"name_as_stated": "European Commission", "actor_id": None}, "subjects": [], "flags": [], "extraction_note": None,
            "pass2": {"chain_link": None, "reform_issue_ids": [], "mechanism_ids": [], "intervention_ids": [],
                      "classification_status": "not_classified", "classification_note": None}}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--report", help="write results to this CSV (tool, test, result, detail)")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp) / "proj"
        proj.mkdir()
        for name in COPY:
            src = ROOT / name
            (shutil.copytree if src.is_dir() else shutil.copy2)(src, proj / name)
        samples = Path(tmp) / "samples"
        samples.mkdir()
        # The real taxonomy, queues, links, entities and judgements refer to real evidence items, which are not copied; start the sample project with empty ones, and likewise the queues, links, entities and judgements.
        for rel in ("taxonomy/reform_issues.csv", "taxonomy/unmatched_queue.csv", "taxonomy/ambiguous_queue.csv", "links/links.csv", "entities/comparator_cases.csv", "entities/interventions.csv", "entities/actors.csv", "judgements/judgements.csv"):
            ri = proj / rel
            ri.write_text(ri.read_text(encoding="utf-8").splitlines()[0] + "\n", encoding="utf-8")

        # hash_file
        f = samples / "a.txt"
        f.write_bytes(b"abc")
        r = run(proj, "hash_file.py", str(f))
        check("hash_file.py", "known SHA-256 of 'abc'", r.stdout.split()[0] == hashlib.sha256(b"abc").hexdigest(), r.stdout)

        # next_id
        # Expected values come from the copied data, so the tests keep working as the real registers grow.
        def highest(rel, col, prefix):
            with (proj / rel).open(encoding="utf-8") as fh:
                return max([int(r[col][len(prefix):]) for r in csv.DictReader(fh) if r[col].startswith(prefix)], default=0)
        r = run(proj, "next_id.py", "limit")
        want = f"LIM-{highest('registers/limits_log.csv', 'limit_id', 'LIM-') + 1:04d}"
        check("next_id.py", "next limit after the highest recorded", r.stdout.strip() == want, r.stdout)
        r = run(proj, "next_id.py", "lesson")
        want = f"ALN-{max(highest(str(f.relative_to(proj)), 'lesson_id', 'ALN-') for f in proj.glob('runs/RUN-*/*learning_log.csv')) + 1:04d}"
        check("next_id.py", "next lesson after the highest recorded", r.stdout.strip() == want, r.stdout)
        reg_path = proj / "registers" / "source_register.csv"
        reg_path.write_text(reg_path.read_text(encoding="utf-8").splitlines()[0] + "\n", encoding="utf-8")
        r = run(proj, "next_id.py", "source", "--country", "MKD", "--family", "EU", "--year", "2025")
        check("next_id.py", "first source ID", r.stdout.strip() == "MKD-EU-2025-001", r.stdout)
        with (proj / "registers" / "source_register.csv").open("a", encoding="utf-8") as fh:
            fh.write("MKD-EU-2025-004" + "," * 24 + "\n")
        r = run(proj, "next_id.py", "source", "--country", "MKD", "--family", "EU", "--year", "2025")
        check("next_id.py", "never reuses: continues after highest recorded source", r.stdout.strip() == "MKD-EU-2025-005", r.stdout)
        (proj / "evidence" / "MKD").mkdir(parents=True)
        (proj / "evidence" / "MKD" / "MKD-EU-2025-004.json").write_text(json.dumps(evidence("MKD-EU-2025-004", [
            item("MKD-EU-2025-004-0001", "x", page=1), item("MKD-EU-2025-004-0007", "y", page=1)])), encoding="utf-8")
        r = run(proj, "next_id.py", "item", "--source-id", "MKD-EU-2025-004")
        check("next_id.py", "next item after the highest in the file", r.stdout.strip() == "MKD-EU-2025-004-0008", r.stdout)
        (proj / "evidence" / "MKD" / "MKD-EU-2025-004.json").unlink()
        r = run(proj, "next_id.py", "source")
        check("next_id.py", "refuses a source ID without country, family and year", r.returncode != 0)

        # convert_to_text: text PDF
        sid = "MKD-EU-2025-001"
        text_dir = proj / "sources" / "MKD" / "EU" / "text"
        orig = samples / "report.pdf"
        orig.write_bytes(minimal_pdf([
            ["Chapter 2: Freedom of movement for workers", "The country has some level of preparation in this area.",
             "Limited progress was made on the long-", "term strategy during the reporting period."],
            ["In the coming year, the country should in particular complete the", "technical preparations for connecting to EESSI."]]))
        before = hashlib.sha256(orig.read_bytes()).hexdigest()
        r = run(proj, "convert_to_text.py", str(orig), str(text_dir / f"{sid}.txt"))
        txt = (text_dir / f"{sid}.txt").read_text(encoding="utf-8") if r.returncode == 0 else ""
        check("convert_to_text.py", "text PDF: page markers and text", "=== PAGE 1 ===" in txt and "=== PAGE 2 ===" in txt and "some level of preparation" in txt, r.stderr[-300:])
        check("convert_to_text.py", "text PDF: no text recognition needed", "ocr:" not in r.stdout, r.stdout)
        check("convert_to_text.py", "original file unchanged", hashlib.sha256(orig.read_bytes()).hexdigest() == before)
        check("convert_to_text.py", "density: characters per page reported for a text PDF", "density: 2 page(s), median" in r.stdout, r.stdout)
        thin = samples / "thin.pdf"
        thin.write_bytes(image_pdf("Annual report of the regulator: recommendations"))
        dens = samples / "thin_density.csv"
        r = run(proj, "convert_to_text.py", str(thin), str(samples / "thin.txt"), "--density-report", str(dens))
        tt = (samples / "thin.txt").read_text(encoding="utf-8") if r.returncode == 0 else ""
        check("convert_to_text.py", "density: thin page with an image flagged, text recognition not run, text kept",
              "thin page 1" in r.stdout and "page has an image" in r.stdout and "ocr:" not in r.stdout and "Annual report of the regulator" in tt, r.stdout + r.stderr[-300:])
        drows = list(csv.DictReader(dens.open(encoding="utf-8"))) if dens.exists() else []
        check("convert_to_text.py", "density: CSV report lists each page with image and thin flags",
              len(drows) == 1 and drows[0]["has_image"] == "yes" and drows[0]["thin"] == "yes", str(drows))
        check("convert_to_text.py", "density: whole document reported as thin", "document is thin" in r.stdout, r.stdout)

        # convert_to_text: scanned PDF with Macedonian Cyrillic
        scan = samples / "scan.pdf"
        scanned_pdf(scan, ["Министерство за информатичко општество", "Закон за електронска идентификација"])
        out_scan = samples / "scan.txt"
        r = run(proj, "convert_to_text.py", str(scan), str(out_scan), "--ocr-langs", "mkd+eng")
        stext = out_scan.read_text(encoding="utf-8") if r.returncode == 0 else ""
        check("convert_to_text.py", "scanned PDF: text recognition reported", "ocr: text recognition used on page(s) 1" in r.stdout, r.stdout + r.stderr[-300:])
        check("convert_to_text.py", "scanned PDF: Macedonian Cyrillic recognised", "Министерство" in stext and "електронска" in stext, stext[:200])

        # convert_to_text: HTML, DOCX, XLSX
        html_f = samples / "page.html"
        html_f.write_text("<html><body><nav>Menu</nav><h1>Digital agenda</h1><p>The country adopted a national cybersecurity strategy.</p>"
                          "<h2>Data protection</h2><p>The law on personal data protection is aligned.</p><script>x=1</script></body></html>", encoding="utf-8")
        r = run(proj, "convert_to_text.py", str(html_f), str(samples / "page.txt"))
        h = (samples / "page.txt").read_text(encoding="utf-8")
        check("convert_to_text.py", "HTML: section markers kept, scripts and menus removed",
              "=== SECTION: Data protection ===" in h and "x=1" not in h and "Menu" not in h, h)
        import docx
        d = docx.Document()
        d.add_heading("Implementation report", level=1)
        d.add_paragraph("The employment service connected to EURES in 2024.")
        d.save(samples / "doc.docx")
        r = run(proj, "convert_to_text.py", str(samples / "doc.docx"), str(samples / "doc.txt"))
        t = (samples / "doc.txt").read_text(encoding="utf-8") if r.returncode == 0 else ""
        check("convert_to_text.py", "DOCX: headings as section markers", "=== SECTION: Implementation report ===" in t and "EURES" in t, r.stderr[-300:])
        doc_url = "https://av.gov.mk/content/Dokumenti/Izvestaj%202023%20so%20prevod.doc"
        legacy = samples / "legacy.doc"
        got = subprocess.run(["curl", "-sL", "--max-time", "60", "-o", str(legacy), doc_url], capture_output=True)
        if got.returncode == 0 and legacy.exists() and legacy.read_bytes()[:4] == bytes.fromhex("d0cf11e0"):
            r = run(proj, "convert_to_text.py", str(legacy), str(samples / "legacy.txt"))
            t = (samples / "legacy.txt").read_text(encoding="utf-8") if r.returncode == 0 else ""
            check("convert_to_text.py", "DOC (legacy Word, Macedonian): Cyrillic text extracted", "=== PAGE 1 ===" in t and any("\u0400" <= ch <= "\u04ff" for ch in t), r.stderr[-300:])
        else:
            check("convert_to_text.py", "DOC (legacy Word): sample could not be downloaded", False, "network")
        from openpyxl import Workbook
        wb = Workbook()
        wb.active.title = "Permits"
        wb.active.append(["Year", "Work permits"])
        wb.active.append([2024, 1520])
        wb.save(samples / "data.xlsx")
        r = run(proj, "convert_to_text.py", str(samples / "data.xlsx"), str(samples / "data.txt"))
        t = (samples / "data.txt").read_text(encoding="utf-8") if r.returncode == 0 else ""
        check("convert_to_text.py", "XLSX: one page per sheet", "=== PAGE 1 ===" in t and "=== SECTION: Permits ===" in t and "1520" in t, r.stderr[-300:])

        # start_extraction and several runs per evidence file (evidence schema 1.3, E21)
        mx = proj / "evidence" / "MDA" / "MDA-EU-2099-001.json"
        mx.parent.mkdir(parents=True, exist_ok=True)
        cmp_item = item("MDA-EU-2099-001-0001", "A comparator claim.", page=1)
        cmp_item["country"], cmp_item["role"] = "MDA", "comparator"
        mx.write_text(json.dumps(evidence("MDA-EU-2099-001", [cmp_item])), encoding="utf-8")
        before = json.loads(mx.read_text(encoding="utf-8"))
        r = run(proj, "start_extraction.py", "MDA-EU-2099-001", "--run", "RUN-2026-02", "--date", "2026-11-03")
        after = json.loads(mx.read_text(encoding="utf-8")) if r.returncode == 0 else {}
        e0 = (after.get("earlier_extractions") or [{}])[0]
        check("start_extraction.py", "earlier run's records kept unchanged with run, country, role and items",
              e0.get("extraction") == before["extraction"] and e0.get("classification") == before["classification"]
              and e0.get("run_country") == "MKD" and e0.get("role") == "comparator" and e0.get("item_ids") == ["MDA-EU-2099-001-0001"]
              and after["items"] == before["items"] and after["extraction"]["run_id"] == "RUN-2026-02" and after["extraction"]["run_country"] == "MDA",
              r.stdout + r.stderr[-300:])
        sys.path.insert(0, str(proj / "tools"))
        import common as cm
        new_item = item("MDA-EU-2099-001-0002", "A comparator claim.", page=1)
        new_item["country"] = "MDA"
        after["items"].append(new_item)
        check("start_extraction.py", "each item belongs to one run",
              [i["item_id"] for i in cm.run_items(after, "RUN-2026-01")] == ["MDA-EU-2099-001-0001"]
              and [i["item_id"] for i in cm.run_items(after, "RUN-2026-02")] == ["MDA-EU-2099-001-0002"])
        r = run(proj, "start_extraction.py", "MDA-EU-2099-001", "--run", "RUN-2026-02")
        check("start_extraction.py", "refuses to start the same run twice", r.returncode != 0)
        after["earlier_extractions"][0]["item_ids"].append("MDA-EU-2099-001-0009")
        mx.write_text(json.dumps(after), encoding="utf-8")
        r = run(proj, "validate_data.py")
        check("validate_data.py", "earlier extraction listing an unknown item is an error", "lists unknown item MDA-EU-2099-001-0009" in r.stdout + r.stderr)
        mx.unlink()

        # verify_quotes
        ev = proj / "evidence" / "MKD" / f"{sid}.json"
        ev.write_text(json.dumps(evidence(sid, [
            item(f"{sid}-0001", "The country has some level of preparation in this area.", page=1),
            item(f"{sid}-0002", "Limited progress was made on the long-term strategy during the reporting period.", page=1),
            item(f"{sid}-0003", "Limited progress was made on the longterm strategy during the reporting period.", page=1),
            item(f"{sid}-0004", "The country has some level of preparation in this area.", page=2),
            item(f"{sid}-0005", "The country has sоme level of preparation in this area.", page=1),  # Cyrillic о
            item(f"{sid}-0006", "In the coming year, the country should in particular complete the technical preparations for connecting to EESSI.", page=2),
        ]), ensure_ascii=False), encoding="utf-8")
        r = run(proj, "verify_quotes.py", str(ev))
        res = {i["item_id"][-4:]: i["quote_verified"] for i in json.loads(ev.read_text(encoding="utf-8"))["items"]}
        check("verify_quotes.py", "exact quote on cited page passes", res.get("0001") is True)
        check("verify_quotes.py", "quote across a line-break hyphen passes (hyphen kept)", res.get("0002") is True)
        check("verify_quotes.py", "quote across a line-break hyphen passes (hyphen removed)", res.get("0003") is True)
        check("verify_quotes.py", "quote on the wrong page fails", res.get("0004") is False)
        check("verify_quotes.py", "Cyrillic look-alike letter is not accepted", res.get("0005") is False)
        check("verify_quotes.py", "quote spanning a line break passes", res.get("0006") is True)
        # A quote must start and end on a word boundary (1.3.0, PC-30, ALN-0038); a footnote mark running on is not a cut.
        mw = proj / "evidence" / "MKD" / "MKD-EU-2023-001.json"
        (text_dir / "MKD-EU-2023-001.txt").write_text("=== PAGE 1 ===\nThe country has some level of preparation in this area27. More\ntext follows here.\n", encoding="utf-8")
        mw.write_text(json.dumps(evidence("MKD-EU-2023-001", [
            item("MKD-EU-2023-001-0001", "he country has some level", page=1), item("MKD-EU-2023-001-0002", "The country has some lev", page=1),
            item("MKD-EU-2023-001-0003", "The country has some level of preparation in this area", page=1),
            item("MKD-EU-2023-001-0004", "More text follows here.", page=1)])), encoding="utf-8")
        r = run(proj, "verify_quotes.py", str(mw))
        mres = [i["quote_verified"] for i in json.loads(mw.read_text(encoding="utf-8"))["items"]]
        mrep = (proj / "review" / "RUN-2026-01" / "quote_checks" / "MKD-EU-2023-001.csv").read_text(encoding="utf-8")
        check("verify_quotes.py", "quote cut mid-word at its start or end fails with a clear message; footnote mark after the last word passes (1.3.0)",
              mres == [False, False, True, True] and "cut mid-word at its start" in mrep and "cut mid-word at its end" in mrep, str(mres) + mrep)
        mw.unlink()
        (proj / "review" / "RUN-2026-01" / "quote_checks" / "MKD-EU-2023-001.csv").unlink()
        # Quote over a page break with a printed page number and running header in between (rules 0.2, R4).
        pb_sid = "MKD-EU-2024-001"
        pb_lines = "\n".join(f"=== PAGE {n} ===\nReport header\n{n}\nFiller text on page {n}." for n in range(1, 4))
        pb_lines = pb_lines.replace("Filler text on page 1.", "Filler text on page 1. The law on digital services was adopted by").replace("=== PAGE 2 ===\nReport header\n2\n", "=== PAGE 2 ===\nReport header\n2\nthe Assembly in March.\n")
        (text_dir / f"{pb_sid}.txt").write_text(pb_lines, encoding="utf-8")
        pb = proj / "evidence" / "MKD" / f"{pb_sid}.json"
        good_item = item(f"{pb_sid}-0001", "The law on digital services was adopted by the Assembly in March.", page=1)
        good_item["location"]["page_end"] = 2
        bad_item = item(f"{pb_sid}-0002", "The law on digital services was adopted by 2 the Assembly in March.", page=1)
        bad_item["location"]["page_end"] = 2
        pb.write_text(json.dumps(evidence(pb_sid, [good_item, bad_item])), encoding="utf-8")
        run(proj, "verify_quotes.py", str(pb))
        pbres = [i["quote_verified"] for i in json.loads(pb.read_text(encoding="utf-8"))["items"]]
        check("verify_quotes.py", "quote across a page break passes; printed page number inside the quote fails", pbres == [True, False], str(pbres))
        # Header carrying the page number, and footnotes at the foot of the first page.
        pb2 = "\n".join(f"=== PAGE {n} ===\nAudit team: auditor {n}\nBody line one on page {n}.\nBody line two on page {n}.\nBody line three on page {n}." for n in range(1, 5))
        pb2 = pb2.replace("Body line three on page 1.", "The register of AI systems was not\n12 Footnote text about the register.\n13 Another footnote.").replace("=== PAGE 2 ===\nAudit team: auditor 2\n", "=== PAGE 2 ===\nAudit team: auditor 2\nestablished by the ministry.\n")
        (text_dir / f"{pb_sid}.txt").write_text(pb2, encoding="utf-8")
        it3 = item(f"{pb_sid}-0003", "The register of AI systems was not established by the ministry.", page=1)
        it3["location"]["page_end"] = 2
        pb.write_text(json.dumps(evidence(pb_sid, [it3])), encoding="utf-8")
        run(proj, "verify_quotes.py", str(pb))
        ok3 = json.loads(pb.read_text(encoding="utf-8"))["items"][0]["quote_verified"]
        check("verify_quotes.py", "page break with numbered running header and footnotes between the pages passes", ok3 is True)
        pb.unlink()
        check("verify_quotes.py", "exit status 1 when any quote fails", r.returncode == 1)
        check("verify_quotes.py", "report written", (proj / "review" / "RUN-2026-01" / "quote_checks" / f"{sid}.csv").exists())
        web_sid = "MKD-GOV-2025-001"
        wt = proj / "sources" / "MKD" / "GOV" / "text"
        wt.mkdir(parents=True)
        shutil.copy(samples / "page.txt", wt / f"{web_sid}.txt")
        wev = proj / "evidence" / "MKD" / f"{web_sid}.json"
        wev.write_text(json.dumps(evidence(web_sid, [
            item(f"{web_sid}-0001", "The law on personal data protection is aligned.", section="Data protection"),
            item(f"{web_sid}-0002", "The law on personal data protection is aligned.", section="Digital agenda")])), encoding="utf-8")
        run(proj, "verify_quotes.py", str(wev))
        wres = [i["quote_verified"] for i in json.loads(wev.read_text(encoding="utf-8"))["items"]]
        check("verify_quotes.py", "webpage: quote in cited section passes, other section fails", wres == [True, False], str(wres))

        # validate_data
        good = json.loads(ev.read_text(encoding="utf-8"))
        good["items"] = [i for i in good["items"] if i["quote_verified"]]
        ev.write_text(json.dumps(good, ensure_ascii=False), encoding="utf-8")
        wev.unlink()
        # Reset the copied registers that refer to real sources, so the sample project is self-contained.
        shutil.copy2(ROOT / "registers" / "source_register.csv", proj / "registers" / "source_register.csv")
        r = run(proj, "validate_data.py")
        check("validate_data.py", "clean sample project passes", r.returncode == 0, r.stdout[-800:])
        bad = json.loads(ev.read_text(encoding="utf-8"))
        bad["items"][0]["themes"] = ["TECH-NOPE"]
        bad["items"][0]["pass2"]["reform_issue_ids"] = ["RI-FMW-999"]
        bad["items"].append(dict(bad["items"][1]))
        ev.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
        r = run(proj, "validate_data.py")
        check("validate_data.py", "unknown theme code detected", "unknown theme code TECH-NOPE" in r.stdout)
        check("validate_data.py", "unknown reform issue detected", "unknown reform issue RI-FMW-999" in r.stdout)
        check("validate_data.py", "duplicate item ID detected", "duplicate item ID" in r.stdout)
        long_q = json.loads(ev.read_text(encoding="utf-8"))
        long_q["items"][0]["stated_text"] = "One claim. Two claims. Three claims. Four claims."
        ev.write_text(json.dumps(long_q, ensure_ascii=False), encoding="utf-8")
        r = run(proj, "validate_data.py")
        check("validate_data.py", "quote longer than three sentences gives a warning", "quote has about 4 sentences" in r.stdout, r.stdout[-300:])
        ev.write_text(json.dumps(good, ensure_ascii=False), encoding="utf-8")
        rr = proj / "taxonomy" / "reform_issues.csv"
        orig_hdr = rr.read_text(encoding="utf-8")
        rr.write_text(orig_hdr.replace(",themes,", ","), encoding="utf-8")
        r = run(proj, "validate_data.py")
        check("validate_data.py", "CSV header mismatch with data dictionary detected", "reform_issues.csv: header does not match" in r.stdout)
        rr.write_text(orig_hdr, encoding="utf-8")
        jpath = proj / "judgements" / "judgements.csv"
        hdr = jpath.read_text(encoding="utf-8").strip()
        row = f"JDG-000001,evidence_confidence,item,{sid}-0001,,High,Stated directly.,{sid}-0001,Sofia,validated,,Sofia,2026-10-29,,,1.2,0.1b,,RUN-2026-01"
        jpath.write_text(hdr + "\n" + row + "\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(proj)], check=True)
        subprocess.run(["git", "-C", str(proj), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(proj), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "t"], check=True)
        jpath.write_text(hdr + "\n" + row.replace(",High,", ",Low,") + "\n", encoding="utf-8")
        r = run(proj, "validate_data.py")
        check("validate_data.py", "change to a validated judgement is flagged", "JDG-000001 is validated but its value has changed" in r.stdout, r.stdout[-500:])
        # 1.6.0: judgement values by type (PC-22 adds 'replaced'), reviewed rows must be validated, no row lost since the last commit (PC-32)
        jrows = [row.replace(",evidence_confidence,item,", ",implementation_status,item,").replace(",High,", ",replaced,"),
                 row.replace("JDG-000001", "JDG-000002").replace(",High,", ",Vanished,"), row.replace("JDG-000001", "JDG-000003").replace(",validated,", ",proposed,")]
        jpath.write_text(hdr + "\n" + "\n".join(jrows) + "\n", encoding="utf-8")
        r = run(proj, "validate_data.py")
        check("validate_data.py", "implementation status 'replaced' accepted, unknown judgement value rejected (1.6.0, PC-22)",
              "JDG-000001 has implementation_status value" not in r.stdout and "JDG-000002 has evidence_confidence value 'Vanished'" in r.stdout, r.stdout[-500:])
        check("validate_data.py", "judgement with reviewer and review date but still proposed is an error (1.6.0, PC-32)",
              "JDG-000003 has reviewer and review date but review_status 'proposed'" in r.stdout, r.stdout[-500:])
        jpath.write_text(hdr + "\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(proj), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam", "reset judgements"], check=True)
        lim_path, dl_path = proj / "registers" / "limits_log.csv", proj / "decisions" / "decision_log.md"
        lim_before, dl_before = lim_path.read_text(encoding="utf-8"), dl_path.read_text(encoding="utf-8")
        lim_lines = lim_before.splitlines(keepends=True)
        lim_path.write_text("".join(lim_lines[:2] + lim_lines[3:]), encoding="utf-8")
        dl_path.write_text(dl_before.split("## Change history")[0], encoding="utf-8")
        r = run(proj, "validate_data.py")
        check("validate_data.py", "a register row or decision log entry lost since the last commit is an error (1.6.0, PC-32)",
              "limits_log.csv: 1 row(s) present at the last commit are missing" in r.stdout and "decision_log.md: change history has 0 entries" in r.stdout and r.returncode == 1,
              " | ".join(l for l in r.stdout.splitlines() if l.startswith("error"))[-600:])
        lim_path.write_text(lim_before, encoding="utf-8")
        dl_path.write_text(dl_before, encoding="utf-8")
        # Register country 'multi' (PC-26) and the optional run columns (PC-27): accepted, and read by the run helpers
        reg_p = proj / "registers" / "source_register.csv"
        reg_before = reg_p.read_text(encoding="utf-8")
        reg_cols = reg_before.splitlines()[0].split(",")
        mrow = {"source_id": "MKD-EU-2098-001", "source_family": "EU", "country": "multi", "role": "target", "added_in_run": "RUN-2026-01", "used_in_runs": "RUN-2026-01;RUN-2026-02"}
        reg_p.write_text(reg_before + ",".join(mrow.get(c, "") for c in reg_cols) + "\n", encoding="utf-8")
        r = run(proj, "validate_data.py")
        ok_multi = "MKD-EU-2098-001" not in r.stdout
        reg_p.write_text(reg_before + ",".join({**mrow, "used_in_runs": "RUN-2026-02;RUN-2099-09"}.get(c, "") for c in reg_cols) + "\n", encoding="utf-8")
        r = run(proj, "validate_data.py")
        check("validate_data.py", "register country 'multi' and used_in_runs accepted; unknown run or a list not starting with added_in_run is an error (1.6.0)",
              ok_multi and "unknown run RUN-2099-09 in used_in_runs" in r.stdout and "used_in_runs must start with added_in_run" in r.stdout, r.stdout[-500:])
        reg_p.write_text(reg_before, encoding="utf-8")
        check("common.py", "register_role follows used_in_runs when filled, and counts a horizontal ('multi') document for a later run",
              cm.register_role({"role": "comparator;target", "used_in_runs": "RUN-2026-01;RUN-2026-02", "added_in_run": "RUN-2026-01"}, "RUN-2026-02", "MDA") == "target"
              and cm.register_role({"role": "target", "used_in_runs": "RUN-2026-01", "added_in_run": "RUN-2026-01"}, "RUN-2026-02", "MDA") is None
              and cm.register_role({"role": "comparator;target", "country": "multi", "added_in_run": "RUN-2026-01"}, "RUN-2026-02", "MDA") == "target")
        check("common.py", "run_requirements follows run_ids when filled",
              [x["requirement_id"] for x in cm.run_requirements(proj, "RUN-2026-02", [{"requirement_id": "REQ-1", "run_ids": "RUN-2026-01;RUN-2026-02"},
                                                                                     {"requirement_id": "REQ-2", "run_ids": "RUN-2026-01", "country": "MDA", "role": "target"}])] == ["REQ-1"])
        # The optional columns may be absent: a header without run_ids still matches the data dictionary
        rq_p = proj / "registers" / "source_requirements.csv"
        rq_before = rq_p.read_text(encoding="utf-8")
        rq_rows = list(csv.reader(io.StringIO(rq_before)))
        k_run = rq_rows[0].index("run_ids") if "run_ids" in rq_rows[0] else None
        if k_run is not None:
            buf = io.StringIO()
            csv.writer(buf, lineterminator="\n").writerows([r_[:k_run] + r_[k_run + 1:] for r_ in rq_rows])
            rq_p.write_text(buf.getvalue(), encoding="utf-8")
        r = run(proj, "validate_data.py")
        check("validate_data.py", "registers without the optional run columns still match the data dictionary (1.6.0)", "source_requirements.csv: header" not in r.stdout, r.stdout[-400:])
        rq_p.write_text(rq_before, encoding="utf-8")
        ri_path = proj / "taxonomy" / "reform_issues.csv"
        ri_before = ri_path.read_text(encoding="utf-8")
        ri_path.write_text(ri_before + "RI-TST-002,Test theme issue,A test definition.,,,TECH-AI,,,,draft,,,RUN-2026-01,\n", encoding="utf-8")
        r = run(proj, "validate_data.py")
        check("validate_data.py", "theme issue with no classified items gives a warning only", "RI-TST-002: theme issue has no classified items yet" in r.stdout and r.returncode == 0,
              " | ".join(l for l in r.stdout.splitlines() if l.startswith("error") or "RI-TST" in l)[-600:])
        th = json.loads(ev.read_text(encoding="utf-8"))
        th["items"][0]["pass2"]["reform_issue_ids"] = ["RI-TST-002"]
        th["items"][0]["pass2"]["classification_status"] = "auto"
        ev.write_text(json.dumps(th, ensure_ascii=False), encoding="utf-8")
        r = run(proj, "validate_data.py")
        check("validate_data.py", "theme issue with items but no recommendation is an error", "RI-TST-002: theme issue has 1 in-scope item(s) but no recommendation" in r.stdout and r.returncode == 1, r.stdout[-400:])
        th["items"][0]["information_type"] = "recommendation"
        ev.write_text(json.dumps(th, ensure_ascii=False), encoding="utf-8")
        r = run(proj, "validate_data.py")
        check("validate_data.py", "theme issue supported by a recommendation passes", "RI-TST-002" not in r.stdout, r.stdout[-400:])
        ri_path.write_text(ri_before, encoding="utf-8")
        ev.write_text(json.dumps(good, ensure_ascii=False), encoding="utf-8")

        # lessons files: from RUN-2026-02 a run keeps runs/<run_id>/learning_log.csv; runs/_template is not a run (E19)
        alpha_ll = (proj / "runs" / "RUN-2026-01" / "alpha_learning_log.csv").read_text(encoding="utf-8").splitlines()
        r2 = proj / "runs" / "RUN-2099-02"
        r2.mkdir(parents=True)
        (r2 / "run_record.md").write_text("# Run record: RUN-2099-02 (test)\n", encoding="utf-8")
        (r2 / "learning_log.csv").write_text(alpha_ll[0] + "\n", encoding="utf-8")
        r = run(proj, "next_id.py", "lesson", "--run", "RUN-2099-02")
        want = f"ALN-{max(highest(str(f.relative_to(proj)), 'lesson_id', 'ALN-') for f in proj.glob('runs/RUN-*/*learning_log.csv')) + 1:04d}"
        check("next_id.py", "next lesson in a new run continues after the highest in any run", r.stdout.strip() == want, r.stdout + r.stderr[-300:])
        r = run(proj, "validate_data.py")
        check("validate_data.py", "new run's learning_log.csv checked; template folder skipped",
              r.returncode == 0 and "_template" not in r.stdout and "RUN-2099-02/learning_log.csv: file missing" not in r.stdout,
              " | ".join(l for l in r.stdout.splitlines() if l.startswith("error"))[-600:])
        (r2 / "learning_log.csv").write_text(alpha_ll[0] + "\n" + alpha_ll[1] + "\n", encoding="utf-8")
        r = run(proj, "validate_data.py")
        check("validate_data.py", "lesson ID reused across runs is an error", "is already used in runs/RUN-2026-01/alpha_learning_log.csv" in r.stdout and r.returncode == 1, r.stdout[-400:])
        shutil.rmtree(r2)

        # near_duplicates (a separate small project: three sources, two versions of one document)
        nd = Path(tmp) / "nd"
        (nd / "registers").mkdir(parents=True)
        reg_hdr = (ROOT / "registers" / "source_register.csv").read_text(encoding="utf-8").splitlines()[0]
        cols = reg_hdr.split(",")
        def reg_row(sid, title, version_of=""):
            vals = {"source_id": sid, "title": title, "country": "MNE", "version_of": version_of}
            return ",".join(vals.get(c, "") for c in cols)
        (nd / "registers" / "source_register.csv").write_text("\n".join([reg_hdr, reg_row("MNE-EU-2024-001", "Screening report (Commission version)"),
                                                                       reg_row("MNE-EU-2024-002", "Screening report (Council version)"),
                                                                       reg_row("MNE-EU-2024-003", "Unrelated report")]) + "\n", encoding="utf-8")
        ndt = nd / "sources" / "MNE" / "EU" / "text"
        ndt.mkdir(parents=True)
        import random
        rnd = random.Random(7)
        vocab = [f"word{n}" for n in range(400)]
        base = [" ".join(rnd.choice(vocab) for _ in range(12)) + "." for _ in range(150)]
        other = [" ".join(rnd.choice(vocab) for _ in range(12)) + "." for _ in range(150)]
        (ndt / "MNE-EU-2024-001.txt").write_text("=== PAGE 1 ===\n" + "\n".join(base) + "\n", encoding="utf-8")
        (ndt / "MNE-EU-2024-002.txt").write_text("=== PAGE 1 ===\nCOUNCIL OF THE EUROPEAN UNION\n=== PAGE 2 ===\n" + "\n".join(base[:140]) + "\n", encoding="utf-8")
        (ndt / "MNE-EU-2024-003.txt").write_text("=== PAGE 1 ===\n" + "\n".join(other) + "\n", encoding="utf-8")
        ndr = subprocess.run([sys.executable, str(proj / "tools" / "near_duplicates.py"), "--run", "RUN-TEST", "--root", str(nd)], capture_output=True, text=True)
        rows = list(csv.DictReader((nd / "review" / "RUN-TEST" / "near_duplicates.csv").open(encoding="utf-8"))) if ndr.returncode == 0 else []
        check("near_duplicates.py", "two versions of one document reported, unrelated source not",
              [(x["source_a"], x["source_b"], x["already_recorded"]) for x in rows] == [("MNE-EU-2024-001", "MNE-EU-2024-002", "no")], ndr.stdout + ndr.stderr[-300:])
        reg_txt = (nd / "registers" / "source_register.csv").read_text(encoding="utf-8")
        (nd / "registers" / "source_register.csv").write_text(reg_txt.replace(reg_row("MNE-EU-2024-002", "Screening report (Council version)"),
                                                                              reg_row("MNE-EU-2024-002", "Screening report (Council version)", "MNE-EU-2024-001")), encoding="utf-8")
        ndr = subprocess.run([sys.executable, str(proj / "tools" / "near_duplicates.py"), "--run", "RUN-TEST", "--root", str(nd)], capture_output=True, text=True)
        rows = list(csv.DictReader((nd / "review" / "RUN-TEST" / "near_duplicates.csv").open(encoding="utf-8")))
        check("near_duplicates.py", "pair already recorded with version_of is marked as recorded", rows and rows[0]["already_recorded"] == "yes", str(rows))

        # export_review
        for gate, name in (("G0", "G0_run_setup.xlsx"), ("G1", "G1_source_requirements.xlsx"), ("G2", "G2_source_review.xlsx")):
            r = run(proj, "export_review.py", gate, "--run", "RUN-2026-01")
            out = proj / "review" / "RUN-2026-01" / name
            ok = r.returncode == 0 and out.exists()
            if ok:
                from openpyxl import load_workbook
                wb = load_workbook(out)
                ok = len(wb.sheetnames) >= 3 and wb.worksheets[0].max_row >= 1
            check("export_review.py", f"{gate} package builds", ok, r.stderr[-300:])
        from openpyxl import load_workbook
        wb = load_workbook(proj / "review" / "RUN-2026-01" / "G0_run_setup.xlsx")
        first = wb.worksheets[0]
        check("export_review.py", "G0: decisions needed come first, freeze date at the top",
              wb.sheetnames[0] == "Decisions needed" and first.cell(2, 1).value == "Evidence freeze date")

        rv = proj / "review" / "RUN-2026-01"
        (rv / "G3_passages.csv").write_text("passage_id,source_id,page,start_text,end_text,why\nP1,MKD-EU-2025-001,1,The country has,,test\n", encoding="utf-8")
        (rv / "G3_sample.csv").write_text("source_id,pages,reason\nMKD-EU-2025-001,whole,test\n", encoding="utf-8")
        reg_lines = (proj / "registers" / "source_register.csv").read_text(encoding="utf-8").splitlines()
        (proj / "registers" / "source_register.csv").write_text(reg_lines[0] + "\nMKD-EU-2025-001,EU,European Commission,,Test report" + "," * 20 + "\n", encoding="utf-8")
        r = run(proj, "export_review.py", "G3-handcoding", "--run", "RUN-2026-01")
        ok = r.returncode == 0 and (rv / "G3_handcoding.xlsx").exists()
        if ok:
            wb = load_workbook(rv / "G3_handcoding.xlsx")
            psg = wb["Passages"].cell(2, 6).value or ""
            ok = wb.sheetnames == ["Instructions", "Passages", "Hand-coded items"] and psg.startswith("The country has some level") \
                and [c.value for c in wb["Hand-coded items"][1]] == ["passage_id", "item_no", "information_type", "stated_text", "scope", "note"]
        check("export_review.py", "G3 hand-coding workbook: passage text taken from the cited page", ok, r.stderr[-300:])
        (rv / "sample_0.1").mkdir(parents=True, exist_ok=True)
        earlier = json.loads(ev.read_text(encoding="utf-8"))
        earlier["items"].append(item(f"{sid}-0099", "A removed claim.", page=1))
        (rv / "sample_0.1" / f"{sid}.json").write_text(json.dumps(earlier), encoding="utf-8")
        r = run(proj, "export_review.py", "G3", "--run", "RUN-2026-01")
        ok = r.returncode == 0 and (rv / "G3_sample_review.xlsx").exists()
        if ok:
            wbc = load_workbook(rv / "G3_sample_review.xlsx")
            removed_ids = [c.value for c in wbc["Removed items"]["A"][1:]]
            check("export_review.py", "G3: comparison with the earlier sample lists removed items", removed_ids == [f"{sid}-0099"], str(removed_ids))
        if ok:
            wb = load_workbook(rv / "G3_sample_review.xlsx")
            shown = [c.value for c in wb["Sample items"]["A"][1:]]
            comp = [row for row in wb["Hand-coding comparison"].iter_rows(min_row=2, values_only=True)]
            ok = f"{sid}-0001" not in shown and comp and comp[0][1] == "awaiting hand-coding"
        check("export_review.py", "G3: agent items in a passage are withheld until it is hand-coded", ok, r.stderr[-300:])
        r = run(proj, "export_review.py", "G3-handcoding", "--run", "RUN-2026-01")
        check("export_review.py", "hand-coding workbook is not overwritten without --force", r.returncode != 0 and "--force" in r.stdout + r.stderr)
        r = run(proj, "export_review.py", "G3-review-sample", "--run", "RUN-2026-01")
        ok = r.returncode == 0 and (rv / "G3_review_sample.xlsx").exists()
        if ok:
            ws = load_workbook(rv / "G3_review_sample.xlsx")
            kept_ids = [c.value for c in ws["Kept items"]["B"][1:]]
            ok = ws.sheetnames == ["Start here", "Kept items", "Removed items", "Missed items"] and f"{sid}-0001" not in kept_ids and len(kept_ids) > 0
        check("export_review.py", "review sample builds, leaves out passage items not yet hand-coded", ok, r.stderr[-300:])
        hw = load_workbook(rv / "G3_handcoding.xlsx")
        ws = hw["Hand-coded items"]
        ws.cell(2, 3).value = "finding"
        ws.cell(2, 4).value = "The country has some level of preparation in this area."
        ws.cell(3, 3).value = "recommendation"
        ws.cell(3, 4).value = "The country should adopt a law on something not in the agent output."
        hw.save(rv / "G3_handcoding.xlsx")
        r = run(proj, "export_review.py", "G3", "--run", "RUN-2026-01")
        wb = load_workbook(rv / "G3_sample_review.xlsx")
        res = [row[1] for row in wb["Hand-coding comparison"].iter_rows(min_row=2, values_only=True)]
        shown = [c.value for c in wb["Sample items"]["A"][1:]]
        check("export_review.py", "G3: comparison finds matched, missed and extra items once hand-coded",
              "matched" in res and "missed by the agent" in res and "extra in the agent output" in res and f"{sid}-0001" in shown, str(res))
        (rv / "G3_sample_review.xlsx").unlink()

        (rv / "G4_issue_mapping.csv").write_text(f"item_id,issue_ids,note\n{sid}-0001,RI-TST-001,\n{sid}-0006,,no issue fits\n", encoding="utf-8")
        with (proj / "taxonomy" / "reform_issues.csv").open("a", encoding="utf-8") as fh:
            fh.write("RI-TST-001,Test issue,A test definition.,2,02,,MEC-01,,,draft,,,RUN-2026-01,\n")
        r = run(proj, "export_review.py", "G4", "--run", "RUN-2026-01")
        ok = r.returncode == 0 and (rv / "G4_taxonomy.xlsx").exists()
        if ok:
            wb4 = load_workbook(rv / "G4_taxonomy.xlsx")
            ok = wb4.sheetnames[0] == "Reform issues" and wb4["Reform issues"].cell(2, 15).value == "1" and wb4["Items fitting no issue"].cell(2, 1).value == f"{sid}-0006"
        check("export_review.py", "G4 package: issues with item counts and items fitting no issue", ok, r.stderr[-300:] + r.stdout[-300:])
        (rv / "G4_taxonomy.xlsx").unlink(missing_ok=True)
        (rv / "G4_decisions.csv").write_text("decision_id,decision_needed\nG4-D01,Test decision\n", encoding="utf-8")
        r = run(proj, "export_review.py", "G4", "--run", "RUN-2026-01")
        ok = r.returncode == 0 and (rv / "G4_taxonomy.xlsx").exists()
        if ok:
            wb4 = load_workbook(rv / "G4_taxonomy.xlsx")
            ok = wb4.sheetnames[:2] == ["Decisions needed", "Reform issues"] and wb4["Decisions needed"].cell(2, 1).value == "G4-D01"
        check("export_review.py", "G4 package: decisions needed come first when listed", ok, r.stderr[-300:] + r.stdout[-300:])
        (rv / "second_pass").mkdir(exist_ok=True)
        (rv / "second_pass" / f"{sid}.csv").write_text(f"item_id,action,detail\n{sid}-0006,added,x\n{sid}-0001,added_missed,y\n", encoding="utf-8")
        (rv / "stage7").mkdir(exist_ok=True)
        (rv / "stage7" / "candidate_issues.csv").write_text("candidate_id,label\nCI-01,Test candidate\n", encoding="utf-8")
        r = run(proj, "export_review.py", "G4", "--run", "RUN-2026-01")
        ok = r.returncode == 0
        if ok:
            wb4 = load_workbook(rv / "G4_taxonomy.xlsx")
            sp_rows = {row[0]: row[1] for row in wb4["Second-pass check"].iter_rows(min_row=2, values_only=True)}
            ok = "Candidate new issues" in wb4.sheetnames and wb4["Candidate new issues"].cell(2, 1).value == "CI-01" and str(sp_rows.get(sid)) == "2"
        check("export_review.py", "G4 package: candidate issues sheet; second pass counts added and added_missed (1.15.0)", ok, r.stderr[-300:] + r.stdout[-300:])
        (rv / "second_pass" / f"{sid}.csv").unlink()
        (rv / "stage7" / "candidate_issues.csv").unlink()
        (rv / "G4_decisions.csv").unlink()
        r = run(proj, "export_review.py", "G5", "--run", "RUN-2026-01")
        ok = r.returncode == 0 and (rv / "G5_classification.xlsx").exists()
        if ok:
            wb5 = load_workbook(rv / "G5_classification.xlsx")
            ok = {"Ambiguous queue", "Unmatched queue", "Spot check", "Contradictions", "Out of scope"} <= set(wb5.sheetnames)
        check("export_review.py", "G5 package: queues, spot check, contradictions and out-of-scope items", ok, r.stderr[-300:] + r.stdout[-300:])
        (rv / "G5_classification.xlsx").unlink(missing_ok=True)
        # G5 lists are scoped to the run (1.17.0, scaling note S10): another run's out-of-scope item and queue row stay out
        mdx = proj / "evidence" / "MDA" / "MDA-EU-2098-001.json"
        mdx.parent.mkdir(parents=True, exist_ok=True)
        md_item = item("MDA-EU-2098-001-0001", "Another run's claim.", page=1)
        md_item["country"] = "MDA"
        md_item["pass2"]["classification_status"] = "out_of_scope"
        md_ev = evidence("MDA-EU-2098-001", [md_item])
        md_ev["extraction"].update({"run_id": "RUN-2026-02", "run_country": "MDA", "role": "target"})
        mdx.write_text(json.dumps(md_ev), encoding="utf-8")
        uqp = proj / "taxonomy" / "unmatched_queue.csv"
        uq_before = uqp.read_text(encoding="utf-8")
        uqp.write_text(uq_before.rstrip("\n") + "\n9001,MDA-EU-2098-001-0001,Test label,Test definition.,,open,,\n", encoding="utf-8")
        (rv.parent / "RUN-2026-02").mkdir(exist_ok=True)
        r1 = run(proj, "export_review.py", "G5", "--run", "RUN-2026-01")
        r2 = run(proj, "export_review.py", "G5", "--run", "RUN-2026-02")
        ok = r1.returncode == 0 and r2.returncode == 0
        if ok:
            w1, w2 = load_workbook(rv / "G5_classification.xlsx"), load_workbook(rv.parent / "RUN-2026-02" / "G5_classification.xlsx")
            ids = lambda wb, sh: [row[0] for row in wb[sh].iter_rows(min_row=2, values_only=True)]
            ok = ("MDA-EU-2098-001-0001" not in ids(w1, "Out of scope") and 9001 not in ids(w1, "Unmatched queue") and "9001" not in ids(w1, "Unmatched queue")
                  and ids(w2, "Out of scope") == ["MDA-EU-2098-001-0001"] and [str(x) for x in ids(w2, "Unmatched queue")] == ["9001"]
                  and "Second-pass yield" in w2.sheetnames and "Classification summary" in w2.sheetnames)
        check("export_review.py", "G5 package lists only the run's items, queue rows and links (1.17.0)", ok, r1.stderr[-300:] + r2.stderr[-300:])
        uqp.write_text(uq_before, encoding="utf-8")
        mdx.unlink()
        (rv / "G5_classification.xlsx").unlink(missing_ok=True)
        (rv.parent / "RUN-2026-02" / "G5_classification.xlsx").unlink(missing_ok=True)
        ri = proj / "taxonomy" / "reform_issues.csv"
        drafted = ri.read_text(encoding="utf-8")
        ri.write_text(drafted.replace(",draft,", ",approved,"), encoding="utf-8")
        r = run(proj, "export_review.py", "G1b", "--run", "RUN-2026-01")
        ok = r.returncode == 0 and "Comparator source lines" in load_workbook(rv / "G1b_comparators.xlsx").sheetnames
        check("export_review.py", "G1b package: countries checked and comparator source lines", ok, r.stderr[-300:] + r.stdout[-300:])
        (rv / "G1b_comparators.xlsx").unlink(missing_ok=True)
        r = run(proj, "export_review.py", "G6b", "--run", "RUN-2026-01")
        ok = r.returncode == 0 and {"Cases", "Lessons and transferability", "Success and attribution", "Gaps in sources"} <= set(load_workbook(rv / "G6b_comparators.xlsx").sheetnames)
        check("export_review.py", "G6b package: cases, lessons, success and attribution, and gaps", ok, r.stderr[-300:] + r.stdout[-300:])
        (rv / "G6b_comparators.xlsx").unlink(missing_ok=True)
        r = run(proj, "export_review.py", "G6", "--run", "RUN-2026-01")
        ri.write_text(drafted, encoding="utf-8")
        ok = r.returncode == 0 and (rv / "G6_issue_dossiers.xlsx").exists()
        if ok:
            wb6 = load_workbook(rv / "G6_issue_dossiers.xlsx")
            ok = {"Issue index", "Tier 3 judgements", "Tier 2 by exception", "RI-TST-001"} <= set(wb6.sheetnames)
        check("export_review.py", "G6 package: one dossier per issue, tier 3 and tier 2 sheets", ok, r.stderr[-300:] + r.stdout[-300:])
        (rv / "G6_issue_dossiers.xlsx").unlink(missing_ok=True)
        # G6-refresh (1.16.0): a proposed row superseding a validated one, a link from a refresh item, decisions first
        jp, lp = proj / "judgements" / "judgements.csv", proj / "links" / "links.csv"
        j_before, l_before = jp.read_text(encoding="utf-8"), lp.read_text(encoding="utf-8")
        jp.write_text(j_before.rstrip("\n") + "\n"
                      f"JDG-900001,direction_of_travel,issue_country,RI-TST-001@MKD,,persistent,Old reason.,{sid}-0001,agent,validated,yes,Sofia,2026-10-30,,,1.2,0.4,1.1,RUN-2026-01\n"
                      f"JDG-900002,direction_of_travel,issue_country,RI-TST-001@MKD,,improving,New reason.,{sid}-0001;{sid}-0002,agent,proposed,,,,,JDG-900001,1.2,0.4,1.1,RUN-2026-01\n", encoding="utf-8")
        lp.write_text(l_before.rstrip("\n") + f"\nLNK-900001,{sid}-0002,{sid}-0001,contradicts,Test basis.,agent,proposed,RUN-2026-01,0.3\n", encoding="utf-8")
        (rv / "G6_refresh_decisions.csv").write_text("decision_id,decision_needed,kind,what_the_files_show,agent_recommendation,what_changes\nG6R-D01,Test?,safe,x,y,z\n", encoding="utf-8")
        r = run(proj, "export_review.py", "G6-refresh", "--run", "RUN-2026-01", "--sources", sid)
        ok = r.returncode == 0 and (rv / "G6_refresh.xlsx").exists()
        if ok:
            wbr = load_workbook(rv / "G6_refresh.xlsx")
            ch = [row for row in wbr["Judgement changes"].iter_rows(min_row=2, values_only=True)]
            lk = [row for row in wbr["Links new confirmed contradicts"].iter_rows(min_row=2, values_only=True)]
            ok = (wbr.sheetnames[:2] == ["Decisions needed", "Judgement changes"] and ch and ch[0][2:7] == ("JDG-900001", "persistent", "JDG-900002", "improving", "value")
                  and lk and lk[0][5] == "contradicts")
        check("export_review.py", "G6-refresh package: decisions first, old against new judgement, contradictions first (1.16.0)", ok, r.stderr[-300:] + r.stdout[-300:])
        # G7-refresh (1.18.0): outputs with their state and flags, proposed statuses beside the previous ones, ratings by exception
        jp.write_text(j_before.rstrip("\n") + "\n"
                      "JDG-900003,implementation_status,intervention,INT-TST-0001,2026-10-29,adopted,Old status.,,agent,validated,,Sofia,2026-10-30,,,1.2,0.4,1.1,RUN-2026-01\n"
                      "JDG-900004,implementation_status,intervention,INT-TST-0001,2026-11-05,implemented,New status.,,agent,proposed,,,,,,1.2,0.4,1.1,RUN-2026-01\n"
                      f"JDG-900005,evidence_confidence,item,{sid}-0001,,High,Rule.,{sid}-0001,agent,proposed,,,,,,1.2,0.4,1.1,RUN-2026-01\n"
                      f"JDG-900006,evidence_confidence,item,{sid}-0002,,Medium,Contested.,{sid}-0002,agent,proposed,,,,,JDG-900003,1.2,0.4,1.1,RUN-2026-01\n", encoding="utf-8")
        (rv / "G7_refresh_decisions.csv").write_text("decision_id,decision_needed,kind,what_the_files_show,agent_recommendation,what_changes\nG7R-D01,Test?,safe,x,y,z\n", encoding="utf-8")
        (rv / "refresh").mkdir(parents=True, exist_ok=True)
        (rv / "refresh" / "output_flags.csv").write_text("output,flag\ncomparator_brief_RI-TST-001.md,Review at G7\n", encoding="utf-8")
        od = proj / "outputs" / "RUN-2026-01"
        had_outputs = (proj / "outputs").exists()
        od.mkdir(parents=True, exist_ok=True)
        (od / "issue_brief_RI-TST-001.md").write_text("**Status: Draft, rebuilt after G7 (GATE-0012).** High (proposed)\n", encoding="utf-8")
        (od / "comparator_brief_RI-TST-001.md").write_text("**Status: Validated at G7 (GATE-0012), internal output.**\n", encoding="utf-8")
        r = run(proj, "export_review.py", "G7-refresh", "--run", "RUN-2026-01")
        ok = r.returncode == 0 and (rv / "G7_refresh.xlsx").exists()
        if ok:
            wb7 = load_workbook(rv / "G7_refresh.xlsx")
            outs = [row for row in wb7["Outputs"].iter_rows(min_row=2, values_only=True)]
            imp7 = [row for row in wb7["Implementation status"].iter_rows(min_row=2, values_only=True)]
            rat7 = [row for row in wb7["Confidence and relevance"].iter_rows(min_row=2, values_only=True)]
            ok = (wb7.sheetnames[0] == "Decisions needed" and outs and outs[0][0] == "comparator_brief_RI-TST-001.md" and outs[0][5] == "Review at G7"
                  and any(o[0] == "issue_brief_RI-TST-001.md" and o[2] == "rebuilt (Draft)" and o[3] == "1" for o in outs)
                  and imp7 and imp7[0][2] == "JDG-900003" and imp7[0][7] == "implemented" and imp7[0][8] == "changed"
                  and rat7 and rat7[0][0] == "JDG-900006")
        check("export_review.py", "G7-refresh package: flagged outputs first, proposed status beside the previous one, superseding ratings first (1.18.0)", ok, r.stderr[-300:] + r.stdout[-300:])
        for name in ("G7_refresh.xlsx", "G7_refresh_decisions.csv", "refresh/output_flags.csv"):
            (rv / name).unlink(missing_ok=True)
        for name in ("issue_brief_RI-TST-001.md", "comparator_brief_RI-TST-001.md"):
            (od / name).unlink(missing_ok=True)
        if not had_outputs:
            shutil.rmtree(proj / "outputs", ignore_errors=True)  # later tests read the absence of outputs as "before G7"
        jp.write_text(j_before, encoding="utf-8")
        lp.write_text(l_before, encoding="utf-8")
        for name in ("G6_refresh.xlsx", "G6_refresh_decisions.csv"):
            (rv / name).unlink(missing_ok=True)
        (rv / "G4_taxonomy.xlsx").unlink(missing_ok=True)
        lines = (proj / "taxonomy" / "reform_issues.csv").read_text(encoding="utf-8").splitlines()
        (proj / "taxonomy" / "reform_issues.csv").write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")

        # build_review_page
        out_html = Path(tmp) / "index.html"
        r = run(proj, "build_review_page.py", "--run", "RUN-2026-01", "--output", str(out_html), "--date", "2026-10-29")
        page = out_html.read_text(encoding="utf-8") if r.returncode == 0 else ""
        check("build_review_page.py", "page builds", bool(page), r.stderr[-300:])
        check("build_review_page.py", "G0 shown as pending review while its package awaits decision", ">G0</td>" in page and "Pending review" in page)
        check("build_review_page.py", "hand-coding workbook is not treated as a G3 package", "<dt>Gate package awaiting decision</dt><dd>G3" not in page)
        check("build_review_page.py", "no external scripts, fonts or stylesheets", "<script" not in page and "http" not in page.split("<body>")[1].split("<footer>")[0] and "<link" not in page)
        check("build_review_page.py", "extraction section shows the sample", "Evidence items" in page)
        with (proj / "registers" / "gate_log.csv").open("a", encoding="utf-8") as fh:
            fh.write("GATE-0001,RUN-2026-01,G0,2026-11-10,Sofia,pass,,G0_run_setup.xlsx,,\n")
        run(proj, "build_review_page.py", "--run", "RUN-2026-01", "--output", str(out_html), "--date", "2026-11-10")
        page = out_html.read_text(encoding="utf-8")
        check("build_review_page.py", "after a pass, G0 shown as validated", 'class="label validated">Validated</span> pass, 2026-11-10' in page)
        from html.parser import HTMLParser

        class P(HTMLParser):
            def __init__(self):
                super().__init__()
                self.stack, self.ok = [], True

            def handle_starttag(self, tag, attrs):
                if tag not in ("meta", "br", "link", "img", "input"):
                    self.stack.append(tag)

            def handle_endtag(self, tag):
                if not self.stack or self.stack.pop() != tag:
                    self.ok = False
        hp = P()
        hp.feed(page)
        check("build_review_page.py", "HTML tags balanced", hp.ok and not hp.stack)
        check("build_review_page.py", "review page links to the country page and the regional page", 'href="analysis/MKD.html"' in page and 'href="analysis.html"' in page)
        cpath = Path(tmp) / "analysis" / "MKD.html"
        apage = cpath.read_text(encoding="utf-8") if cpath.exists() else ""
        hp2 = P()
        hp2.feed(apage)
        check("build_review_page.py", "country page (before G7) builds in analysis/, balanced, self-contained", bool(apage) and hp2.ok and not hp2.stack and "<script" not in apage and "<link" not in apage)
        check("build_review_page.py", "country page shows quotes with item IDs and placeholders for later sections",
              f"{sid}-0001" in apage and "Reform issues" in apage and "layout only" in apage)
        check("build_review_page.py", "country page links back one folder up, to its own run's review page", ('href="../index.html"' in apage or 'href="../review_RUN-2026-01.html"' in apage) and 'href="../analysis.html"' in apage)
        rpage = (Path(tmp) / "analysis.html").read_text(encoding="utf-8") if (Path(tmp) / "analysis.html").exists() else ""
        hp3 = P()
        hp3.feed(rpage)
        check("build_review_page.py", "regional page builds, balanced, no external files", bool(rpage) and hp3.ok and not hp3.stack and "<link" not in rpage and " src=" not in rpage)
        check("build_review_page.py", "regional page lists the planned countries and shows no judgement that is not validated",
              "Montenegro" in rpage and "Kosovo" in rpage and "Not started" in rpage and "Priority <b>" not in rpage)  # the sample project has no judgements
        with (rv / "G3_passages.csv").open("a", encoding="utf-8") as fh:
            fh.write("P2,MKD-EU-2025-001,2,In the coming year,,test\n")
        run(proj, "build_review_page.py", "--run", "RUN-2026-01", "--output", str(out_html), "--date", "2026-11-10")
        apage = cpath.read_text(encoding="utf-8")
        check("build_review_page.py", "country page leaves out items in a passage not yet hand-coded, keeps hand-coded ones",
              f"{sid}-0006" not in apage and f"{sid}-0001" in apage and "left out until the analyst has hand-coded them" in apage)

        # acquire: a local web server only, never the real internet
        import http.server
        import os
        import threading
        pdf_bytes = minimal_pdf([["Test report on Chapter 2."]])

        class H(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                if self.path == "/robots.txt":
                    body, code, ctype = b"User-agent: *\nDisallow: /private/\n", 200, "text/plain"
                elif self.path in ("/doc.pdf", "/private/doc.pdf"):
                    body, code, ctype = pdf_bytes, 200, "application/pdf"
                elif self.path == "/secret.pdf":
                    body, code, ctype = b"Forbidden", 403, "text/plain"
                elif self.path == "/report":
                    self.send_response(302)
                    self.send_header("Location", "/account/login?next=/report")
                    self.end_headers()
                    return
                elif self.path.startswith("/account/login"):
                    body, code, ctype = b"<html><form><input type='password' name='p'></form></html>", 200, "text/html"
                else:
                    body, code, ctype = b"Not found", 404, "text/plain"
                self.send_response(code)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        base_url = f"http://127.0.0.1:{srv.server_address[1]}"
        aq = Path(tmp) / "aq"
        (aq / "registers").mkdir(parents=True)
        (aq / "registers" / "source_register.csv").write_text(reg_hdr + "\n", encoding="utf-8")
        env = {**os.environ, "NO_PROXY": "127.0.0.1,localhost", "no_proxy": "127.0.0.1,localhost"}
        for k in ("HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy", "ALL_PROXY", "all_proxy"):
            env.pop(k, None)

        def acquire(*args):
            return subprocess.run([sys.executable, str(proj / "tools" / "acquire.py"), *args, "--run", "RUN-TEST", "--country", "MNE", "--family", "EU",
                                   "--year", "2026", "--root", str(aq)], capture_output=True, text=True, env=env)
        orig_dir = aq / "sources" / "MNE" / "EU" / "originals"
        r = acquire(f"{base_url}/doc.pdf", "--slug", "EC Montenegro Report 2026")
        saved = orig_dir / "MNE-EU-2026-001_EC-Montenegro-Report-2026.pdf"
        check("acquire.py", "download filed under the naming convention, read-only, with its SHA-256",
              r.returncode == 0 and saved.exists() and not os.access(saved, os.W_OK) and hashlib.sha256(pdf_bytes).hexdigest() in r.stdout
              and saved.read_bytes() == pdf_bytes, r.stdout + r.stderr[-300:])
        r = acquire(f"{base_url}/doc.pdf", "--slug", "Again", "--source-id", "MNE-EU-2026-001")
        check("acquire.py", "refuses to overwrite an existing original", r.returncode == 2 and saved.read_bytes() == pdf_bytes, r.stdout + r.stderr[-300:])
        with (aq / "registers" / "source_register.csv").open("a", encoding="utf-8") as fh:
            fh.write(",".join({"source_id": "MNE-EU-2026-001", "content_hash": hashlib.sha256(pdf_bytes).hexdigest()}.get(c, "") for c in cols) + "\n")
        r = acquire(f"{base_url}/doc.pdf", "--slug", "Copy")
        check("acquire.py", "exact duplicate of a registered file is not saved",
              r.returncode == 3 and "MNE-EU-2026-001" in r.stdout and not list(orig_dir.glob("MNE-EU-2026-002*")), r.stdout + r.stderr[-300:])
        r = acquire(f"{base_url}/secret.pdf", "--slug", "Secret")
        check("acquire.py", "403 recorded as a retrieval failure, nothing saved", r.returncode == 1 and "access forbidden" in r.stdout and not list(orig_dir.glob("MNE-EU-2026-002*")), r.stdout + r.stderr[-300:])
        r = acquire(f"{base_url}/report", "--slug", "Behind login")
        check("acquire.py", "redirect to a login page is refused", r.returncode == 1 and "login" in r.stdout, r.stdout + r.stderr[-300:])
        r = acquire(f"{base_url}/private/doc.pdf", "--slug", "Private")
        check("acquire.py", "robots.txt disallow is respected", r.returncode == 1 and "robots.txt" in r.stdout, r.stdout + r.stderr[-300:])
        inbox = aq / "sources" / "_inbox"
        inbox.mkdir(parents=True)
        (inbox / "hand.pdf").write_bytes(minimal_pdf([["Saved by hand by the analyst."]]))
        r = acquire("--manual", str(inbox / "hand.pdf"), "--slug", "Manual Copy", "--convert")
        hand = orig_dir / "MNE-EU-2026-002_Manual-Copy.pdf"
        txt_hand = aq / "sources" / "MNE" / "EU" / "text" / "MNE-EU-2026-002.txt"
        check("acquire.py", "manual route: inbox file copied, inbox kept, converted to text",
              r.returncode == 0 and hand.exists() and (inbox / "hand.pdf").exists() and txt_hand.exists() and "Saved by hand" in txt_hand.read_text(encoding="utf-8"),
              r.stdout + r.stderr[-300:])
        (samples / "outside.pdf").write_bytes(b"%PDF-1.4")
        r = acquire("--manual", str(samples / "outside.pdf"), "--slug", "Outside")
        check("acquire.py", "manual route only accepts files from sources/_inbox/", r.returncode != 0 and "_inbox" in r.stderr, r.stderr[-300:])
        (inbox / "limite.pdf").write_bytes(minimal_pdf([["Council of the European Union", "LIMITE", "EU common position"]]))
        r = acquire("--manual", str(inbox / "limite.pdf"), "--slug", "Restricted")
        check("acquire.py", "document marked LIMITE is refused and not filed (LIM-0045)",
              r.returncode == 4 and "LIMITE" in r.stdout and not list(orig_dir.glob("MNE-EU-2026-003*")), r.stdout + r.stderr[-300:])
        alog = list(csv.DictReader((aq / "review" / "RUN-TEST" / "acquisition_log.csv").open(encoding="utf-8")))
        check("acquire.py", "every attempt logged with its result", [x["result"] for x in alog] == ["saved", "refused", "duplicate", "failed", "failed", "failed", "saved", "refused"], str([x["result"] for x in alog]))
        srv.shutdown()

        # build_outputs: rebuild the validated RUN-2026-01 outputs from a copy of the real data and compare
        bo = Path(tmp) / "bo"
        for name in ("evidence", "registers", "taxonomy", "entities", "links", "judgements", "runs", "tools", "schemas"):
            shutil.copytree(ROOT / name, bo / name)
        for name in ("stage12", "run1b"):
            shutil.copytree(ROOT / "review" / "RUN-2026-01" / name, bo / "review" / "RUN-2026-01" / name)
        r = subprocess.run([sys.executable, str(bo / "tools" / "build_outputs.py"), "--run", "RUN-2026-01", "--root", str(bo)], capture_output=True, text=True)
        built, ref = bo / "outputs" / "RUN-2026-01", ROOT / "outputs" / "RUN-2026-01"
        # The coverage report lists the limits as they now stand (the log grew after G7), so it is compared by structure only.
        # After the refresh (E18) the committed outputs are the 41 briefs rebuilt for the refresh G7 and the rest as signed off at G7.
        # A file still signed off at G7 that a full rebuild would now mark "rebuilt after G7" is awaiting the refresh G7
        # (scope overview, comparator briefs and two briefs whose interventions have new statuses: review/RUN-2026-01/refresh/output_flags.csv),
        # so it is listed and skipped; every other file must rebuild byte for byte.
        same = sorted(f.name for f in ref.glob("*.md") if f.name != "coverage_and_limits_report.md")
        pending = [n for n in same if (built / n).exists() and "Validated at G7" in (ref / n).read_text(encoding="utf-8").split("\n\n", 2)[1][:400]
                   and "rebuilt after G7" in (built / n).read_text(encoding="utf-8")[:600]]
        flagged = {row["output"] for row in csv.DictReader((ROOT / "review" / "RUN-2026-01" / "refresh" / "output_flags.csv").open(encoding="utf-8"))} \
            if (ROOT / "review" / "RUN-2026-01" / "refresh" / "output_flags.csv").exists() else set()
        # build_outputs 1.4.0 (PC-31): a brief whose shared issue changed after the run's taxonomy version carries a taxonomy note, and
        # issues added by a later run with no evidence in this run (empty rows in the signed-off scope overview) are left out.
        later_issues = {r["issue_id"] for r in csv.DictReader((bo / "taxonomy" / "reform_issues.csv").open(encoding="utf-8")) if r["created_in_run"] > "RUN-2026-01"}

        def norm_built(t):
            return "".join(l for l in t.splitlines(keepends=True) if not l.startswith("*Taxonomy note:")).replace("\n\n\n", "\n\n")

        def norm_ref(t):
            return "".join(l for l in t.splitlines(keepends=True) if not (l.startswith("| RI-") and l.split(" | ")[0][2:] in later_issues and "| 0 items, 0 sources" in l))
        diff = [n for n in same if n not in pending and (not (built / n).exists() or norm_built((built / n).read_text(encoding="utf-8")) != norm_ref((ref / n).read_text(encoding="utf-8")))]
        import build_outputs as bo_mod
        run_tv = max((r["taxonomy_version"] for r in csv.DictReader((bo / "judgements" / "judgements.csv").open(encoding="utf-8")) if r["run_id"] == "RUN-2026-01"), key=bo_mod.vkey)
        newer_issues = [r["issue_id"] for r in csv.DictReader((bo / "taxonomy" / "reform_issues.csv").open(encoding="utf-8"))
                        if (built / f"issue_brief_{r['issue_id']}.md").exists() and bo_mod.vkey(r["taxonomy_version"]) > bo_mod.vkey(run_tv)]
        noted = sorted(f.name for f in built.glob("issue_brief_*.md") if "*Taxonomy note:" in f.read_text(encoding="utf-8"))
        check("build_outputs.py", "taxonomy note only in briefs whose shared issue changed after the run's taxonomy version (1.4.0)",
              noted == sorted(f"issue_brief_{x}.md" for x in newer_issues), str(noted))
        check("build_outputs.py", "rebuilds the G7 and refresh issue, scope and comparator briefs byte for byte", r.returncode == 0 and same and not diff,
              (r.stderr[-300:] or "") + f" differ: {diff[:5]}")
        check("build_outputs.py", "every output awaiting the refresh G7 is flagged for review", set(pending) <= flagged, f"not flagged: {sorted(set(pending) - flagged)}")
        r2 = subprocess.run([sys.executable, str(bo / "tools" / "build_outputs.py"), "--run", "RUN-2026-01", "--root", str(bo), "--issues", "RI-TEC-036"], capture_output=True, text=True)
        check("build_outputs.py", "--issues rebuilds only the named brief (1.3.0)", r2.returncode == 0 and "wrote 1 issue briefs" in r2.stdout
              and (built / "issue_brief_RI-TEC-036.md").read_bytes() == (ref / "issue_brief_RI-TEC-036.md").read_bytes(), r2.stdout + r2.stderr[-300:])
        cov = (built / "coverage_and_limits_report.md").read_text(encoding="utf-8") if (built / "coverage_and_limits_report.md").exists() else ""
        check("build_outputs.py", "coverage and limits report builds with its sections", all(h in cov for h in ("## Source requirements", "## Reliance on machine translation", "## Active limits")))
        import re as _re
        raw_id = _re.compile(r"\b[A-Z]{3}-(?:EU|GOV|CSO|IO|RES)-\d{4}-\d{3}-\d{4}\b")
        leaks = [f.name for f in built.glob("*.md") if raw_id.search(f.read_text(encoding="utf-8").split("## Annex")[0])]
        check("build_outputs.py", "evidence item IDs appear only in the annex, not in the running text", not leaks, str(leaks[:5]))
        annex_ok = True
        evid = {}
        for f in (bo / "evidence").glob("*/*.json"):
            for it in json.loads(f.read_text(encoding="utf-8"))["items"]:
                evid[it["item_id"]] = it["stated_text"].replace("\n", " ").strip()
        for f in list(built.glob("issue_brief_*.md"))[:5]:
            for line in f.read_text(encoding="utf-8").split("## Annex")[-1].splitlines():
                m = _re.match(r"^\[\d+\] \*\*(\S+)\*\*\. .*?\"(.*?)\"(?: Machine translation:|$)", line)
                if m and evid.get(m.group(1)) != m.group(2):
                    annex_ok = False
        check("build_outputs.py", "annex quotes each item word for word", annex_ok)
        gl = bo / "registers" / "gate_log.csv"
        gl.write_text("\n".join(l for l in gl.read_text(encoding="utf-8").splitlines() if ",G7," not in l) + "\n", encoding="utf-8")
        r = subprocess.run([sys.executable, str(bo / "tools" / "build_outputs.py"), "--run", "RUN-2026-01", "--root", str(bo)], capture_output=True, text=True)
        anyb = next(iter(sorted(built.glob("issue_brief_*.md"))), None)
        check("build_outputs.py", "status line reads Draft when G7 has not passed",
              r.returncode == 0 and anyb is not None and "Draft, prepared at stage 12 for sign-off at G7" in anyb.read_text(encoding="utf-8"), r.stderr[-300:])
        shutil.rmtree(bo / "review" / "RUN-2026-01" / "stage12" / "factpacks", ignore_errors=True)
        r = subprocess.run([sys.executable, str(bo / "tools" / "build_outputs.py"), "--run", "RUN-2026-01", "--root", str(bo), "--factpacks"], capture_output=True, text=True)
        n_issues = len(list(built.glob("issue_brief_*.md")))
        packs = list((bo / "review" / "RUN-2026-01" / "stage12" / "factpacks").glob("*.md"))
        check("build_outputs.py", "one fact pack per issue brief of the run (1.4.0: issues added by a later run without evidence are left out)", r.returncode == 0 and len(packs) == n_issues, f"{len(packs)} packs, {n_issues} issues")

        # Two-run fixture (PC-31, ALN-0035, ALN-0043, G7-D04): rebuild the closed runs' outputs, pages and gate packages, let a later
        # run add records on their shared entities, rebuild, and check nothing the closed runs show has changed. The later run
        # gets no run record, so the active run (and with it index.html) stays the same: only the effect of its records is tested.
        tr = Path(tmp) / "tr"
        for name in ("evidence", "registers", "taxonomy", "entities", "links", "judgements", "runs", "tools", "schemas", "decisions"):
            shutil.copytree(ROOT / name, tr / name)
        for rn in ("RUN-2026-01", "RUN-2026-02"):
            for name in ("stage12", "run1b"):
                if (ROOT / "review" / rn / name).exists():
                    shutil.copytree(ROOT / "review" / rn / name, tr / "review" / rn / name)
        for name in ("alpha_summary.html",):
            if (ROOT / name).exists():
                shutil.copy2(ROOT / name, tr / name)

        def tr_run(tool, *args):
            return subprocess.run([sys.executable, str(tr / "tools" / tool), *args, "--root", str(tr)], capture_output=True, text=True)

        def tr_build(tag):
            """Outputs and pages of both closed runs, and three gate packages of the alpha, copied to tr/<tag>/."""
            errs = []
            snap = tr / tag
            for rn in ("RUN-2026-01", "RUN-2026-02"):
                r = tr_run("build_outputs.py", "--run", rn)
                errs += [r.stderr[-300:]] if r.returncode else []
                shutil.copytree(tr / "outputs" / rn, snap / "outputs" / rn)
                pg = snap / "pages" / rn
                pg.mkdir(parents=True, exist_ok=True)
                r = tr_run("build_review_page.py", "--run", rn, "--date", "2026-11-06", "--output", str(pg / "review.html"),
                           "--analysis-output", str(pg / "country.html"), "--regional-output", str(pg / "regional.html"))
                errs += [r.stderr[-300:]] if r.returncode else []
            for gate, name in (("G5", "G5_classification.xlsx"), ("G6", "G6_issue_dossiers.xlsx"), ("G6b", "G6b_comparators.xlsx")):
                r = tr_run("export_review.py", gate, "--run", "RUN-2026-01")
                errs += [r.stderr[-300:]] if r.returncode else []
                wb = load_workbook(tr / "review" / "RUN-2026-01" / name) if r.returncode == 0 else None
                sheets = {ws.title: [list(row) for row in ws.iter_rows(values_only=True)] for ws in wb.worksheets if ws.title != "Validation"} if wb else {}
                (snap / "packages").mkdir(parents=True, exist_ok=True)
                (snap / "packages" / f"{gate}.json").write_text(json.dumps(sheets, default=str, ensure_ascii=False), encoding="utf-8")
            return errs
        errs = tr_build("before")
        # The later run's records, on the closed runs' entities: a Montenegro run that uses North Macedonia as a comparator.
        later, gate1, gate2 = "RUN-2099-03", "GATE-9001", "GATE-9002"
        alpha_items = [i for f in sorted((tr / "evidence" / "MKD").glob("MKD-*.json")) for i in cm.run_items(json.loads(f.read_text(encoding="utf-8")), "RUN-2026-01")]
        mkd_case = next(r for r in csv.DictReader((tr / "entities" / "comparator_cases.csv").open(encoding="utf-8"))
                        if r["country"] == "MKD" and any(r["reform_issue_id"] in i["pass2"]["reform_issue_ids"] for i in alpha_items))
        mkd_int = cm.split_list(mkd_case["intervention_ids"])[0]
        mkd_item = next(i["item_id"] for i in alpha_items if mkd_case["reform_issue_id"] in i["pass2"]["reform_issue_ids"])
        mkd_actor = next(r["actor_id"] for r in csv.DictReader((tr / "entities" / "actors.csv").open(encoding="utf-8")) if r["country"] == "MKD")
        nsid = "MNE-EU-2099-001"
        it1 = item(f"{nsid}-0001", "Montenegro adopted the law on foreigners.", page=1)
        it1.update(country="MNE")
        it1["pass2"].update(reform_issue_ids=["RI-FMW-001", "RI-TST-901"], classification_status="auto", chain_link="country_response")
        it2 = item(f"{nsid}-0002", "North Macedonia's e-services portal serves most users.", page=1)
        it2.update(country="MKD", role="comparator")
        it2["speaker"] = {"name_as_stated": "Government", "actor_id": mkd_actor}
        it2["subjects"] = [{"name_as_stated": "Later run body", "actor_id": "ACT-MKD-9001"}]
        it2["pass2"].update(reform_issue_ids=[mkd_case["reform_issue_id"]], intervention_ids=[mkd_int, "INT-MKD-9001"], classification_status="auto", chain_link="outcome")
        ev3 = evidence(nsid, [it1, it2])
        ev3["extraction"].update(run_id=later, run_country="MNE", role="target")
        (tr / "evidence" / "MNE").mkdir(parents=True, exist_ok=True)
        (tr / "evidence" / "MNE" / f"{nsid}.json").write_text(json.dumps(ev3, ensure_ascii=False), encoding="utf-8")

        def append(rel, values):
            path = tr / rel
            hdr = next(csv.reader(path.open(encoding="utf-8", newline="")))
            nl = "\r\n" if path.read_bytes().splitlines(keepends=True)[0].endswith(b"\r\n") else "\n"
            buf = io.StringIO()
            csv.writer(buf, lineterminator=nl).writerow([values.get(h, "") for h in hdr])
            with path.open("a", encoding="utf-8", newline="") as fh:
                fh.write(buf.getvalue())
        append("registers/gate_log.csv", {"gate_decision_id": gate1, "run_id": later, "gate": "G0", "date": "2099-01-01", "reviewers": "Sofia", "decision": "pass"})
        append("registers/gate_log.csv", {"gate_decision_id": gate2, "run_id": later, "gate": "G1b", "date": "2099-01-02", "reviewers": "Sofia", "decision": "pass"})
        append("registers/source_register.csv", {"source_id": nsid, "source_family": "EU", "title": "Later run report", "country": "MNE", "role": "target",
                                                 "status": "available", "added_in_run": later, "used_in_runs": later})
        append("registers/source_register.csv", {"source_id": "MKD-EU-2099-001", "source_family": "EU", "title": "Horizontal document", "country": "multi",
                                                 "role": "target", "status": "available", "added_in_run": later, "used_in_runs": later})
        append("registers/source_requirements.csv", {"requirement_id": "REQ-9001", "country": "MKD", "role": "comparator", "status": "open", "run_ids": later})
        append("registers/limits_log.csv", {"limit_id": "LIM-9001", "run_id": later, "limit_type": "evidence", "description": "Later run limit", "status": "active"})
        append("taxonomy/reform_issues.csv", {"issue_id": "RI-TST-901", "label": "Later run issue", "definition": "Added by a later run.", "chapters": "02",
                                              "status": "approved", "taxonomy_version": "9.9", "created_in_run": later})
        append("taxonomy/unmatched_queue.csv", {"queue_id": "9901", "item_id": f"{nsid}-0002", "proposed_label": "Later", "status": "open"})
        append("entities/interventions.csv", {"intervention_id": "INT-MKD-9001", "country": "MKD", "name": "Later run measure", "first_item_id": f"{nsid}-0002"})
        append("entities/actors.csv", {"actor_id": "ACT-MKD-9001", "country": "MKD", "name": "Later run body", "actor_type": "government"})
        append("entities/comparator_cases.csv", {"case_id": "CMP-9001", "country": "MKD", "reform_issue_id": mkd_case["reform_issue_id"], "intervention_ids": mkd_int,
                                                 "description": "Later run case.", "selected_at": gate2})
        lk = {"created_by": "agent", "review_status": "validated", "run_id": later, "rules_version": "0.6"}
        append("links/links.csv", {"link_id": "LNK-900001", "from_id": mkd_int, "to_id": f"{nsid}-0002", "link_type": "leads_to", "basis": "Later run link.", **lk})
        append("links/links.csv", {"link_id": "LNK-900002", "from_id": f"{nsid}-0002", "to_id": mkd_item, "link_type": "contradicts", "basis": "Later run conflict.", **lk})
        jd = {"made_by": "agent", "review_status": "validated", "reviewer": "Sofia", "review_date": "2099-01-03", "codebook_version": "9", "rules_version": "9",
              "taxonomy_version": "9.9", "run_id": later, "reason": "Later run.", "evidence_item_ids": f"{nsid}-0002"}
        for n, (t, ot, oid, ctx, v) in enumerate([
                ("implementation_status", "intervention", mkd_int, "2099-01-01", "replaced"), ("success", "link", "LNK-900001", "", "worked"),
                ("attribution", "link", "LNK-900001", "", "High"), ("priority", "issue_country", "RI-FMW-001@MNE", "", "High"),
                ("comparator_relevance", "issue_comparator", "CMP-9001", "", "High"), ("evidence_confidence", "item", f"{nsid}-0002", "", "Low"),
                ("relevance", "item", f"{nsid}-0002", mkd_case["reform_issue_id"], "Low"), ("evidence_confidence", "item", mkd_item, "", "Low")], start=1):
            append("judgements/judgements.csv", {"judgement_id": f"JDG-9{n:05d}", "judgement_type": t, "object_type": ot, "object_id": oid, "context_id": ctx, "value": v, **jd})
        for n, sid_ in enumerate(sorted({mkd_item.rsplit("-", 1)[0], nsid}), start=1):
            append("judgements/source_quality.csv", {"sq_id": f"SQ-9{n:04d}", "source_id": sid_, "topic": "02", "overall": "Low", "reason": "Later run.",
                                                     "made_by": "agent", "review_status": "validated", "reviewer": "Sofia", "review_date": "2099-01-03", "run_id": later})
        errs += tr_build("after")
        changed = []
        for f in sorted((tr / "before").rglob("*")):
            if f.is_file():
                g = tr / "after" / f.relative_to(tr / "before")
                if f.name == "regional.html":
                    continue  # the regional page is shared by all runs and lists every shared issue by design (E19); checked below
                if not g.exists() or g.read_bytes() != f.read_bytes():
                    changed.append(str(f.relative_to(tr / "before")))
        n_files = sum(1 for f in (tr / "before").rglob("*") if f.is_file())
        check("two-run fixture", "closed runs' outputs, pages and G5, G6 and G6b packages unchanged after a later run adds records on their entities (PC-31)",
              not errs and n_files > 100 and not changed, f"{n_files} files; changed: {changed[:6]}; errors: {errs[:2]}")
        reg_b, reg_a = [(tr / t / "pages" / "RUN-2026-02" / "regional.html").read_text(encoding="utf-8") for t in ("before", "after")]
        check("two-run fixture", "regional page: the later run's shared issue is added as not assessed, nothing else changes",
              "RI-TST-901" in reg_a and "RI-TST-901" not in reg_b and reg_a.count("Not assessed") == reg_b.count("Not assessed") + 2)
        r = tr_run("validate_data.py")
        check("two-run fixture", "later run's records (multi country, used_in_runs, run_ids, replaced status) pass validate_data",
              not [l for l in r.stdout.splitlines() if l.startswith("error") and ("9001" in l or "9002" in l or "multi" in l or "replaced" in l or "RUN-2099" in l)],
              " | ".join(l for l in r.stdout.splitlines() if l.startswith("error"))[-600:])

    passed = sum(r[2] == "pass" for r in results)
    print(f"\n{passed}/{len(results)} tests passed")
    if a.report:
        with open(a.report, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["tool", "test", "result", "detail"])
            w.writerows(results)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
