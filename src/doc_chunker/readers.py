"""Readers: turn one file into a list of Sections.

Build order: read_markdown -> read_html -> read_pdf -> read_file.
Run one reader's tests at a time, e.g.:  uv run pytest tests/test_readers.py -k markdown -v
"""

from pathlib import Path

from doc_chunker.models import Section

SUPPORTED_SUFFIXES = {".md", ".markdown", ".html", ".htm", ".pdf"}


class UnsupportedFileError(ValueError):
    """Raised by read_file() for a file type this tool doesn't handle."""


def read_markdown(text: str) -> list[Section]:
    """Split Markdown into sections by ATX headings (# ... ######).

    Contract:
      - A heading line is 1-6 '#' characters, then at least one space, then the title.
        "#NoSpace" is NOT a heading; it's ordinary text.
      - Headings nest by level into a path joined with " > ":
          "# Installation" then "## Linux"  -> "Installation > Linux"
          a later "## Windows"              -> "Installation > Windows"
          a later "# Usage"                 -> "Usage"
      - Lines inside fenced code blocks (between ``` or ~~~ fences) are never headings,
        even if they start with '#'. The fence lines themselves stay in the text.
      - Text before the first heading gets heading "".
      - A section's text is its lines joined with "\\n", then stripped.
      - Sections whose text is empty after stripping are left out.
    """
    # TODO
    raise NotImplementedError("TODO: implement read_markdown")


def read_html(html: str) -> list[Section]:
    """Split HTML into sections by <h1>, <h2> and <h3>.

    Contract:
      - Parse with BeautifulSoup(html, "html.parser").
      - First remove <script>, <style>, <nav>, <header> and <footer> elements entirely.
      - Walk <h1>, <h2>, <h3>, <p>, <li> and <pre> elements in document order:
          - headings build a path with " > ", exactly like read_markdown (levels 1-3);
          - <p>, <li> and <pre> each contribute one line of text to the current section.
      - Normalize whitespace inside each line: any run of whitespace becomes one space,
        and each line is stripped.
      - A section's text is its lines joined with "\\n". Text before any heading gets "".
      - Sections with no text are left out.
    """
    # TODO
    raise NotImplementedError("TODO: implement read_html")


def read_pdf(path: Path) -> list[Section]:
    """One Section per PDF page that has text.

    Contract:
      - Use pypdf.PdfReader. Heading is "page N", with N starting at 1.
      - Page text is stripped. Pages with no text (blank or scanned images) are left out,
        but page numbers still count them: a blank page 2 means the next section is "page 3".
    """
    # TODO
    raise NotImplementedError("TODO: implement read_pdf")


def read_file(path: Path) -> list[Section]:
    """Pick the right reader by file extension (case-insensitive).

    Contract:
      - .md / .markdown -> read_markdown, .html / .htm -> read_html (read text as UTF-8)
      - .pdf -> read_pdf
      - anything else -> raise UnsupportedFileError naming the file.
    """
    # TODO
    raise NotImplementedError("TODO: implement read_file")
