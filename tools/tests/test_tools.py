#!/usr/bin/env python3
"""Stage 0 tests for the helper tools, run on small generated sample files in a temporary copy of the project.

Usage: python3 tools/tests/test_tools.py [--report tools/tests/last_report.csv]
Never touches the real project data: everything runs in a temporary folder.
"""

import argparse
import csv
import hashlib
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
        for rel in ("taxonomy/reform_issues.csv", "taxonomy/unmatched_queue.csv", "taxonomy/ambiguous_queue.csv", "links/links.csv", "entities/interventions.csv", "entities/actors.csv", "judgements/judgements.csv"):
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
        want = f"ALN-{highest('runs/RUN-2026-01/alpha_learning_log.csv', 'lesson_id', 'ALN-') + 1:04d}"
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
        jpath.write_text(hdr + "\n", encoding="utf-8")

        # export_review
        for gate, name in (("G0", "G0_run_setup.xlsx"), ("G1", "G1_source_requirements.xlsx"), ("G2", "G2_source_review.xlsx")):
            r = run(proj, "export_review.py", gate)
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
        r = run(proj, "export_review.py", "G3-handcoding")
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
        r = run(proj, "export_review.py", "G3")
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
        r = run(proj, "export_review.py", "G3-handcoding")
        check("export_review.py", "hand-coding workbook is not overwritten without --force", r.returncode != 0 and "--force" in r.stdout + r.stderr)
        r = run(proj, "export_review.py", "G3-review-sample")
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
        r = run(proj, "export_review.py", "G3")
        wb = load_workbook(rv / "G3_sample_review.xlsx")
        res = [row[1] for row in wb["Hand-coding comparison"].iter_rows(min_row=2, values_only=True)]
        shown = [c.value for c in wb["Sample items"]["A"][1:]]
        check("export_review.py", "G3: comparison finds matched, missed and extra items once hand-coded",
              "matched" in res and "missed by the agent" in res and "extra in the agent output" in res and f"{sid}-0001" in shown, str(res))
        (rv / "G3_sample_review.xlsx").unlink()

        (rv / "G4_issue_mapping.csv").write_text(f"item_id,issue_ids,note\n{sid}-0001,RI-TST-001,\n{sid}-0006,,no issue fits\n", encoding="utf-8")
        with (proj / "taxonomy" / "reform_issues.csv").open("a", encoding="utf-8") as fh:
            fh.write("RI-TST-001,Test issue,A test definition.,2,02,,MEC-01,,,draft,,,RUN-2026-01,\n")
        r = run(proj, "export_review.py", "G4")
        ok = r.returncode == 0 and (rv / "G4_taxonomy.xlsx").exists()
        if ok:
            wb4 = load_workbook(rv / "G4_taxonomy.xlsx")
            ok = wb4.sheetnames[0] == "Reform issues" and wb4["Reform issues"].cell(2, 15).value == "1" and wb4["Items fitting no issue"].cell(2, 1).value == f"{sid}-0006"
        check("export_review.py", "G4 package: issues with item counts and items fitting no issue", ok, r.stderr[-300:] + r.stdout[-300:])
        (rv / "G4_taxonomy.xlsx").unlink(missing_ok=True)
        (rv / "G4_decisions.csv").write_text("decision_id,decision_needed\nG4-D01,Test decision\n", encoding="utf-8")
        r = run(proj, "export_review.py", "G4")
        ok = r.returncode == 0 and (rv / "G4_taxonomy.xlsx").exists()
        if ok:
            wb4 = load_workbook(rv / "G4_taxonomy.xlsx")
            ok = wb4.sheetnames[:2] == ["Decisions needed", "Reform issues"] and wb4["Decisions needed"].cell(2, 1).value == "G4-D01"
        check("export_review.py", "G4 package: decisions needed come first when listed", ok, r.stderr[-300:] + r.stdout[-300:])
        (rv / "G4_decisions.csv").unlink()
        r = run(proj, "export_review.py", "G5")
        ok = r.returncode == 0 and (rv / "G5_classification.xlsx").exists()
        if ok:
            wb5 = load_workbook(rv / "G5_classification.xlsx")
            ok = {"Ambiguous queue", "Unmatched queue", "Spot check", "Contradictions", "Out of scope"} <= set(wb5.sheetnames)
        check("export_review.py", "G5 package: queues, spot check, contradictions and out-of-scope items", ok, r.stderr[-300:] + r.stdout[-300:])
        (rv / "G5_classification.xlsx").unlink(missing_ok=True)
        ri = proj / "taxonomy" / "reform_issues.csv"
        drafted = ri.read_text(encoding="utf-8")
        ri.write_text(drafted.replace(",draft,", ",approved,"), encoding="utf-8")
        r = run(proj, "export_review.py", "G1b")
        ok = r.returncode == 0 and "Comparator source lines" in load_workbook(rv / "G1b_comparators.xlsx").sheetnames
        check("export_review.py", "G1b package: countries checked and comparator source lines", ok, r.stderr[-300:] + r.stdout[-300:])
        (rv / "G1b_comparators.xlsx").unlink(missing_ok=True)
        r = run(proj, "export_review.py", "G6")
        ri.write_text(drafted, encoding="utf-8")
        ok = r.returncode == 0 and (rv / "G6_issue_dossiers.xlsx").exists()
        if ok:
            wb6 = load_workbook(rv / "G6_issue_dossiers.xlsx")
            ok = {"Issue index", "Tier 3 judgements", "Tier 2 by exception", "RI-TST-001"} <= set(wb6.sheetnames)
        check("export_review.py", "G6 package: one dossier per issue, tier 3 and tier 2 sheets", ok, r.stderr[-300:] + r.stdout[-300:])
        (rv / "G6_issue_dossiers.xlsx").unlink(missing_ok=True)
        (rv / "G4_taxonomy.xlsx").unlink(missing_ok=True)
        lines = (proj / "taxonomy" / "reform_issues.csv").read_text(encoding="utf-8").splitlines()
        (proj / "taxonomy" / "reform_issues.csv").write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")

        # build_review_page
        out_html = Path(tmp) / "index.html"
        r = run(proj, "build_review_page.py", "--output", str(out_html), "--date", "2026-10-29")
        page = out_html.read_text(encoding="utf-8") if r.returncode == 0 else ""
        check("build_review_page.py", "page builds", bool(page), r.stderr[-300:])
        check("build_review_page.py", "G0 shown as pending review while its package awaits decision", ">G0</td>" in page and "Pending review" in page)
        check("build_review_page.py", "hand-coding workbook is not treated as a G3 package", "<dt>Gate package awaiting decision</dt><dd>G3" not in page)
        check("build_review_page.py", "no external scripts, fonts or stylesheets", "<script" not in page and "http" not in page.split("<body>")[1].split("<footer>")[0] and "<link" not in page)
        check("build_review_page.py", "extraction section shows the sample", "Evidence items" in page)
        with (proj / "registers" / "gate_log.csv").open("a", encoding="utf-8") as fh:
            fh.write("GATE-0001,RUN-2026-01,G0,2026-11-10,Sofia,pass,,G0_run_setup.xlsx,,\n")
        run(proj, "build_review_page.py", "--output", str(out_html), "--date", "2026-11-10")
        page = out_html.read_text(encoding="utf-8")
        check("build_review_page.py", "after a pass, G0 shown as validated", 'class="label validated">Validated</span> pass, 2026-11-10' in page)
        from html.parser import HTMLParser

        class P(HTMLParser):
            def __init__(self):
                super().__init__()
                self.stack, self.ok = [], True

            def handle_starttag(self, tag, attrs):
                if tag not in ("meta", "br", "link", "img"):
                    self.stack.append(tag)

            def handle_endtag(self, tag):
                if not self.stack or self.stack.pop() != tag:
                    self.ok = False
        hp = P()
        hp.feed(page)
        check("build_review_page.py", "HTML tags balanced", hp.ok and not hp.stack)
        check("build_review_page.py", "review page links to the analysis page", 'href="analysis.html"' in page)
        apage = (Path(tmp) / "analysis.html").read_text(encoding="utf-8") if (Path(tmp) / "analysis.html").exists() else ""
        hp2 = P()
        hp2.feed(apage)
        check("build_review_page.py", "analysis page builds, balanced, self-contained", bool(apage) and hp2.ok and not hp2.stack and "<script" not in apage and "<link" not in apage)
        check("build_review_page.py", "analysis page shows quotes with item IDs and placeholders for later sections",
              f"{sid}-0001" in apage and "Reform issues" in apage and "layout only" in apage)
        with (rv / "G3_passages.csv").open("a", encoding="utf-8") as fh:
            fh.write("P2,MKD-EU-2025-001,2,In the coming year,,test\n")
        run(proj, "build_review_page.py", "--output", str(out_html), "--date", "2026-11-10")
        apage = (Path(tmp) / "analysis.html").read_text(encoding="utf-8")
        check("build_review_page.py", "analysis page leaves out items in a passage not yet hand-coded, keeps hand-coded ones",
              f"{sid}-0006" not in apage and f"{sid}-0001" in apage and "left out until the analyst has hand-coded them" in apage)

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
