"""Command-line entry point.

doc-chunker ./docs --size 500 --overlap 50 --out chunks.jsonl
"""

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO

from doc_chunker.readers import SUPPORTED_SUFFIXES, read_file
from doc_chunker.splitter import chunk_sections, split_text


def write_chunks(files: list[Path], out: TextIO, size: int, overlap: int) -> None:
    """Write every chunk of every supported file to `out`, one JSON object per line."""
    for file in files:
        if file.suffix.lower() not in SUPPORTED_SUFFIXES:
            print(f"warning: skipping unsupported file {file}", file=sys.stderr)
            continue
        out.writelines(json.dumps(chunk.to_dict()) + "\n" for chunk in chunk_sections(read_file(file), str(file), size, overlap))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="doc-chunker",
        description="Turn Markdown, HTML and PDF files into JSONL chunks.",
    )
    parser.add_argument("path", help="a file, or a folder to walk recursively")
    parser.add_argument(
        "--size", type=int, default=500, help="max characters per chunk"
    )
    parser.add_argument(
        "--overlap", type=int, default=50, help="characters shared between chunks"
    )
    parser.add_argument("--out", help="output .jsonl file (default: stdout)")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI. Returns an exit code: 0 on success, 1 on error."""
    args = build_parser().parse_args(argv)
    root = Path(args.path)

    # 1. The path must exist
    if not root.exists():
        print(f"error: {root} does not exist", file=sys.stderr)
        return 1

    # 2. Validate size/overlap before creating any output file
    try:
        split_text("x", args.size, args.overlap)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    # 3. Which files?
    if root.is_dir():
        files = sorted(p for p in root.rglob("*") if p.is_file())
    else:
        files = [root]

    # 4. Where to write?
    # 4. Write to a file (closed automatically) or to the terminal
    if args.out:
        with open(args.out, "w", encoding="utf-8") as out:
            write_chunks(files, out, args.size, args.overlap)
    else:
        write_chunks(files, sys.stdout, args.size, args.overlap)

    return 0


if __name__ == "__main__":
    sys.exit(main())
