"""Command-line entry point.

    doc-chunker ./docs --size 500 --overlap 50 --out chunks.jsonl

Run its tests with:  uv run pytest tests/test_cli.py -v
"""

import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="doc-chunker",
        description="Turn Markdown, HTML and PDF files into JSONL chunks.",
    )
    parser.add_argument("path", help="a file, or a folder to walk recursively")
    parser.add_argument("--size", type=int, default=500, help="max characters per chunk")
    parser.add_argument("--overlap", type=int, default=50, help="characters shared between chunks")
    parser.add_argument("--out", help="output .jsonl file (default: stdout)")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI. Returns an exit code: 0 on success, 1 on error.

    Contract:
      - If `path` doesn't exist: print an error to stderr, return 1.
      - If `path` is a folder: process every file under it (recursively), sorted by path.
        Files with unsupported extensions are skipped with a warning on stderr.
      - If `path` is a single file: process just that file.
      - Each Chunk is written as one JSON line (json.dumps(chunk.to_dict())) to --out,
        or to stdout when --out is not given.
      - `source` is the file path as a string.
      - Bad --size / --overlap (split_text raises ValueError): print the error to stderr,
        return 1. Tip: validate them BEFORE writing any output.
    """
    args = build_parser().parse_args(argv)
    # TODO
    raise NotImplementedError(f"TODO: implement main (path={args.path!r})")


if __name__ == "__main__":
    sys.exit(main())
