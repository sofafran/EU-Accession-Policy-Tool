#!/usr/bin/env python3
"""Convert an original source file to a text file with page or section markers."""

import argparse
import csv
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import nfc  # noqa: E402

__version__ = "1.2.0"
MIN_CHARS = 25  # a PDF page with fewer non-space characters than this is treated as scanned
THIN_CHARS = 200  # a page with fewer non-space characters than this is reported as thin (PC-17, ALN-0021)
THIN_SHARE = 0.25  # a document with more than this share of thin pages is reported as a whole


def ocr_pdf_page(pdf, page_no, langs, dpi):
    if not shutil.which("pdftoppm") or not shutil.which("tesseract"):
        raise SystemExit("error: text recognition needs pdftoppm (poppler-utils) and tesseract")
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "p"
        subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(page_no), "-l", str(page_no), "-png", str(pdf), str(base)],
                       check=True, capture_output=True)
        image = next(Path(tmp).glob("p*.png"))
        out = subprocess.run(["tesseract", str(image), "stdout", "-l", langs], check=True, capture_output=True, text=True)
        return out.stdout


def page_has_image(page):
    """True if the PDF page draws at least one image, directly or inside a form XObject."""
    def scan(res, depth=0):
        try:
            xobjs = (res or {}).get("/XObject") or {}
            for ref in xobjs.values():
                x = ref.get_object()
                if x.get("/Subtype") == "/Image":
                    return True
                if x.get("/Subtype") == "/Form" and depth < 3 and scan(x.get("/Resources"), depth + 1):
                    return True
        except Exception:  # damaged resources: treat as no image rather than fail the conversion
            return False
        return False
    try:
        return scan(page.get("/Resources"))
    except Exception:
        return False


def chars(text):
    return len("".join(text.split()))


def convert_pdf(path, langs, dpi, force_ocr, ocr_pages_wanted=()):
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    parts, ocr_pages, density = [], [], []
    for i, page in enumerate(reader.pages, start=1):
        text = "" if (force_ocr or i in ocr_pages_wanted) else (page.extract_text() or "")
        if chars(text) < MIN_CHARS:
            text = ocr_pdf_page(path, i, langs, dpi)
            ocr_pages.append(i)
        density.append((i, chars(text), page_has_image(page), i in ocr_pages))
        parts.append(f"=== PAGE {i} ===\n{text.strip()}\n")
    return "\n".join(parts), ocr_pages, len(reader.pages), density


def density_of_text(text):
    """Characters per page from the '=== PAGE n ===' markers of a converted text (formats with no images to compare)."""
    pages, cur, n = [], None, 0
    for line in text.splitlines():
        if line.startswith("=== PAGE ") and line.endswith(" ==="):
            if cur is not None:
                pages.append((cur, n, False, False))
            cur, n = int(line[9:-4]), 0
        elif not line.startswith("=== SECTION: "):
            n += chars(line)
    if cur is not None:
        pages.append((cur, n, False, False))
    return pages


def report_density(density, report_path=None):
    """Print thin pages (likely text held in an image, or a failed extraction) and optionally write all pages to a CSV."""
    thin = [d for d in density if d[1] < THIN_CHARS]
    counts = sorted(d[1] for d in density)
    median = counts[len(counts) // 2] if counts else 0
    print(f"density: {len(density)} page(s), median {median} characters per page; {len(thin)} thin page(s) under {THIN_CHARS} characters")
    for page, n, image, ocr in thin:
        why = "page has an image: text may be in the image; rerun with --ocr-pages" if image and not ocr else (
            "after text recognition" if ocr else "no image found: check the page by eye")
        print(f"density: thin page {page}: {n} characters ({why})")
    if density and len(thin) / len(density) > THIN_SHARE:
        print(f"density: WARNING document is thin: {len(thin)} of {len(density)} pages under {THIN_CHARS} characters; report at G2")
    if report_path:
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["page", "characters", "has_image", "ocr", "thin"])
            for page, n, image, ocr in density:
                w.writerow([page, n, "yes" if image else "no", "yes" if ocr else "no", "yes" if n < THIN_CHARS else "no"])


def convert_html(path):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(Path(path).read_bytes(), "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "form"]):
        tag.decompose()
    body = soup.body or soup
    lines = ["=== PAGE 1 ==="]
    for el in body.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "td", "th", "blockquote", "pre"]):
        if el.find(["p", "li", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6"]):
            continue  # take text from the innermost block only
        text = " ".join(el.get_text(" ").split())
        if not text:
            continue
        if el.name.startswith("h"):
            lines.append(f"=== SECTION: {text} ===")
        else:
            lines.append(text)
    return "\n".join(lines) + "\n", [], 1


def convert_docx(path):
    import docx
    d = docx.Document(str(path))
    lines = ["=== PAGE 1 ==="]
    for para in d.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        style = (para.style.name or "").lower() if para.style is not None else ""
        lines.append(f"=== SECTION: {text} ===" if style.startswith(("heading", "title")) else text)
    for t in d.tables:
        for row in t.rows:
            lines.append(" | ".join(c.text.strip() for c in row.cells))
    return "\n".join(lines) + "\n", [], 1


def convert_doc(path):
    """Legacy Word (.doc) through catdoc. No page or heading information survives, so the text is one page."""
    if not shutil.which("catdoc"):
        raise SystemExit("error: .doc files need catdoc")
    out = subprocess.run(["catdoc", "-d", "utf-8", "-w", str(path)], check=True, capture_output=True, text=True)
    lines = [l.strip() for l in out.stdout.splitlines()]
    return "=== PAGE 1 ===\n" + "\n".join(l for l in lines if l) + "\n", [], 1


def convert_xlsx(path):
    from openpyxl import load_workbook
    wb = load_workbook(str(path), read_only=True, data_only=True)
    parts = []
    for i, ws in enumerate(wb.worksheets, start=1):
        rows = [" | ".join("" if v is None else str(v) for v in row) for row in ws.iter_rows(values_only=True)]
        parts.append(f"=== PAGE {i} ===\n=== SECTION: {ws.title} ===\n" + "\n".join(r for r in rows if r.strip(" |")) + "\n")
    return "\n".join(parts), [], len(wb.worksheets)


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Convert a PDF, HTML, DOCX, DOC or XLSX original to UTF-8 text (NFC). Writes '=== PAGE n ===' before each page; "
                    "webpages and Word files (DOCX and legacy DOC) have no pages, so they get one page marker and '=== SECTION: heading ===' lines for headings. "
                    "PDF pages with no usable text are run through text recognition, and the tool reports which pages. "
                    "It also reports characters per page and flags thin pages (under 200 characters), noting PDF pages that carry an image, "
                    "where the text may sit in the image; the converted text itself is not changed by this check.")
    p.add_argument("original", help="original file (never modified)")
    p.add_argument("output", help="text file to write")
    p.add_argument("--ocr-langs", default="eng+mkd+sqi", help="tesseract languages for scanned pages (default eng+mkd+sqi, as in the run record)")
    p.add_argument("--dpi", type=int, default=300, help="resolution for text recognition (default 300)")
    p.add_argument("--force-ocr", action="store_true", help="run text recognition on every PDF page")
    p.add_argument("--ocr-pages", default="", help="comma-separated PDF pages to run through text recognition, for example thin pages with an image")
    p.add_argument("--density-report", help="also write characters per page to this CSV (page, characters, has_image, ocr, thin)")
    p.add_argument("--version", action="version", version=__version__)
    a = p.parse_args(argv)
    src = Path(a.original)
    ext = src.suffix.lower()
    wanted = {int(x) for x in a.ocr_pages.split(",") if x.strip()}
    density = None
    if ext == ".pdf":
        text, ocr_pages, pages, density = convert_pdf(src, a.ocr_langs, a.dpi, a.force_ocr, wanted)
    elif ext in (".html", ".htm"):
        text, ocr_pages, pages = convert_html(src)
    elif ext == ".docx":
        text, ocr_pages, pages = convert_docx(src)
    elif ext == ".doc":
        text, ocr_pages, pages = convert_doc(src)
    elif ext == ".xlsx":
        text, ocr_pages, pages = convert_xlsx(src)
    else:
        p.error(f"unsupported format: {ext}")
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(nfc(text), encoding="utf-8")
    print(f"wrote {out}: {pages} page(s)")
    if ocr_pages:
        print(f"ocr: text recognition used on page(s) {', '.join(map(str, ocr_pages))} ({a.ocr_langs}); note 'ocr' in the register")
    report_density(density if density is not None else density_of_text(text), a.density_report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
