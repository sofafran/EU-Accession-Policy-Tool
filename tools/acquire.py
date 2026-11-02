#!/usr/bin/env python3
"""Acquire one source: download it (or take a file the analyst saved by hand), file it, fingerprint it and print a register-ready summary.

Procedure P1 stage 2; PC-03 and PC-17 (ALN-0008). The file is saved to sources/<country>/<family>/originals/
as <source_id>_<slug>.<ext> and made read-only. The tool never bypasses a login, paywall, robots.txt rule or
other access restriction: on such a response it records a retrieval failure and stops, and the source is
recorded as inaccessible (or retrieved by hand and added with --manual). It never overwrites an original and
does not keep an exact duplicate of a registered file. Every attempt is logged in review/<run>/acquisition_log.csv.
It does not write to the source register: the agent adds the register row from the summary."""

import argparse
import datetime as dt
import hashlib
import mimetypes
import os
import re
import shutil
import stat
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import FAMILIES, SOURCE_ID_RE, project_root, read_csv, write_csv  # noqa: E402

__version__ = "1.0.0"
USER_AGENT = f"EU-Accession-Policy-Tool/{__version__} (research; public documents only)"
BLOCKED = {401: "login required", 402: "payment required", 403: "access forbidden", 407: "proxy login required",
           429: "too many requests (rate limit)", 451: "unavailable for legal reasons"}
LOGIN_URL = re.compile(r"(login|signin|sign-in|sso|auth|subscribe|paywall)", re.I)
LOGIN_PAGE = re.compile(rb"<input[^>]+type=[\"']?password|paywall|subscribe to (read|continue)", re.I)
EXT = {"application/pdf": ".pdf", "text/html": ".html", "application/msword": ".doc",
       "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx"}
LOG_HEADER = ["date", "source_id", "url_or_file", "result", "http_status", "local_file", "content_hash", "detail"]


class Refused(Exception):
    def __init__(self, status, detail):
        super().__init__(detail)
        self.status, self.detail = status, detail


def slugify(text):
    s = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-")
    return s[:80] or "source"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def next_source_id(root, country, family, year):
    """Next free source ID, counting the register, evidence files and originals already filed (so two acquisitions
    before the register is updated do not get the same ID)."""
    prefix = f"{country}-{family}-{year}-"
    seen = [r["source_id"] for r in read_csv(root / "registers" / "source_register.csv")[1] if r.get("source_id", "").startswith(prefix)]
    seen += [p.stem for p in (root / "evidence" / country).glob(f"{prefix}*.json")]
    seen += [p.name.split("_")[0] for p in (root / "sources" / country / family / "originals").glob(f"{prefix}*")]
    n = max([int(s[len(prefix):]) for s in seen if re.fullmatch(r"\d{3}", s[len(prefix):])], default=0)
    return f"{prefix}{n + 1:03d}"


def robots_allows(url):
    parts = urllib.parse.urlsplit(url)
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"{parts.scheme}://{parts.netloc}/robots.txt")
    try:
        req = urllib.request.Request(rp.url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as r:
            rp.parse(r.read().decode("utf-8", "replace").splitlines())
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return False  # robots.txt itself is restricted: treat the site as disallowing automated access
        return True       # no robots.txt (404 and similar): nothing disallowed
    except (urllib.error.URLError, OSError):
        return True
    return rp.can_fetch(USER_AGENT, url)


def download(url, dest_dir):
    if not robots_allows(url):
        raise Refused("", "robots.txt disallows automated access; retrieve by hand and add with --manual, or record as inaccessible")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            final, ctype, status = r.geturl(), (r.headers.get_content_type() or ""), r.status
            data = r.read()
    except urllib.error.HTTPError as e:
        raise Refused(str(e.code), BLOCKED.get(e.code, f"HTTP error {e.code}"))
    except (urllib.error.URLError, OSError) as e:
        raise Refused("", f"network error: {e}")
    if final != url and LOGIN_URL.search(urllib.parse.urlsplit(final).path + "?" + urllib.parse.urlsplit(final).query):
        raise Refused(str(status), f"redirected to what looks like a login or subscription page ({final})")
    if ctype == "text/html" and LOGIN_PAGE.search(data[:200000]):
        raise Refused(str(status), "the page asks for a login or subscription")
    tmp = Path(tempfile.mkstemp(dir=dest_dir, prefix=".acq-")[1])
    tmp.write_bytes(data)
    ext = Path(urllib.parse.urlsplit(final).path).suffix.lower()
    if ext not in (".pdf", ".html", ".htm", ".doc", ".docx", ".xlsx"):
        ext = EXT.get(ctype) or mimetypes.guess_extension(ctype) or ".bin"
    return tmp, ext, str(status)


def log(root, run, row):
    path = root / "review" / run / "acquisition_log.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = read_csv(path)[1] if path.exists() else []
    write_csv(path, LOG_HEADER, rows + [row])


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("url", nargs="?", help="URL of the document (omit with --manual)")
    p.add_argument("--manual", help="file the analyst saved by hand in sources/_inbox/ (PC-03 manual retrieval route); copied, not moved")
    p.add_argument("--run", required=True, help="run ID, for the acquisition log")
    p.add_argument("--country", required=True, help="country code, for example MNE")
    p.add_argument("--family", required=True, choices=FAMILIES, help="source family")
    p.add_argument("--year", required=True, help="publication year")
    p.add_argument("--slug", required=True, help="short file-name label, for example 'EC-Montenegro-Report-2026'")
    p.add_argument("--source-id", help="use this source ID instead of the next free one")
    p.add_argument("--convert", action="store_true", help="also convert to sources/<country>/<family>/text/<source_id>.txt")
    p.add_argument("--ocr-langs", default="eng", help="tesseract languages for --convert, as listed in the run record (default eng)")
    p.add_argument("--root", help="project root (default: the folder above tools/)")
    p.add_argument("--version", action="version", version=__version__)
    a = p.parse_args(argv)
    if bool(a.url) == bool(a.manual):
        p.error("give either a URL or --manual FILE")
    root = project_root(a.root)
    sid = a.source_id or next_source_id(root, a.country, a.family, a.year)
    m = SOURCE_ID_RE.match(sid)
    if not m or (m.group(1), m.group(2), m.group(3)) != (a.country, a.family, a.year):
        p.error(f"source ID {sid} does not match country {a.country}, family {a.family} and year {a.year}")
    originals = root / "sources" / a.country / a.family / "originals"
    originals.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    where = a.url or a.manual
    clash = sorted(originals.glob(f"{sid}_*")) + sorted(originals.glob(f"{sid}.*"))
    if clash:
        log(root, a.run, {"date": today, "source_id": sid, "url_or_file": where, "result": "refused", "detail": f"an original already exists: {clash[0].name}"})
        print(f"refused: an original for {sid} already exists ({clash[0].name}); originals are never overwritten")
        return 2

    if a.manual:
        src = Path(a.manual).resolve()
        inbox = (root / "sources" / "_inbox").resolve()
        if inbox not in src.parents or not src.is_file():
            p.error(f"--manual must name a file in {inbox}")
        tmp = Path(tempfile.mkstemp(dir=originals, prefix=".acq-")[1])
        shutil.copyfile(src, tmp)
        ext, status, route = src.suffix.lower() or ".bin", "", "manual"
    else:
        try:
            tmp, ext, status = download(a.url, originals)
        except Refused as e:
            log(root, a.run, {"date": today, "source_id": sid, "url_or_file": a.url, "result": "failed", "http_status": e.status, "detail": e.detail})
            print(f"failed: {e.detail}" + (f" (HTTP {e.status})" if e.status else ""))
            print(f"record the source as inaccessible (status_reason: {e.detail}), or retrieve it by hand and rerun with --manual")
            return 1
        route = "download"

    digest = sha256(tmp)
    reg = read_csv(root / "registers" / "source_register.csv")[1]
    dup = next((r["source_id"] for r in reg if r.get("content_hash") == digest), None)
    if dup:
        tmp.unlink()
        log(root, a.run, {"date": today, "source_id": sid, "url_or_file": where, "result": "duplicate", "http_status": status, "content_hash": digest,
                          "detail": f"exact duplicate of registered source {dup}; not saved"})
        print(f"duplicate: the file is identical to registered source {dup} (SHA-256 {digest}); not saved")
        return 3
    name = f"{sid}_{slugify(a.slug)}{ext}"
    final = originals / name
    os.replace(tmp, final)
    final.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    rel = final.relative_to(root).as_posix()
    log(root, a.run, {"date": today, "source_id": sid, "url_or_file": where, "result": "saved", "http_status": status, "local_file": rel,
                      "content_hash": digest, "detail": route})
    print(f"saved {rel} (read-only)")
    print("register fields:")
    for k, v in (("source_id", sid), ("source_family", a.family), ("country", a.country), ("url", a.url or ""),
                 ("retrieval_date", today), ("local_file", rel), ("file_format", ext.lstrip(".")), ("content_hash", digest),
                 ("status", "available"), ("notes", "retrieved by hand (manual route)" if a.manual else "")):
        print(f"  {k}: {v}")
    if a.convert:
        import convert_to_text
        out = root / "sources" / a.country / a.family / "text" / f"{sid}.txt"
        return convert_to_text.main([str(final), str(out), "--ocr-langs", a.ocr_langs])
    return 0


if __name__ == "__main__":
    sys.exit(main())
