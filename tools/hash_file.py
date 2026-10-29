#!/usr/bin/env python3
"""Compute the SHA-256 fingerprint of one or more files."""

import argparse
import hashlib
import sys

__version__ = "1.0.0"


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def main(argv=None):
    p = argparse.ArgumentParser(description="Print the SHA-256 fingerprint of each file, one per line: '<hash>  <path>'. Used at stage 2 to fill content_hash in the source register and to detect exact duplicates.")
    p.add_argument("files", nargs="+", help="files to fingerprint")
    p.add_argument("--version", action="version", version=__version__)
    args = p.parse_args(argv)
    status = 0
    for path in args.files:
        try:
            print(f"{sha256(path)}  {path}")
        except OSError as e:
            print(f"error: {path}: {e}", file=sys.stderr)
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
