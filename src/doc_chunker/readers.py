"""Readers: turn one file into a list of Sections.

Build order: read_markdown -> read_html -> read_pdf -> read_file.
Run one reader's tests at a time, e.g.:  uv run pytest tests/test_readers.py -k markdown -v
"""

import re
from pathlib import Path

from bs4 import BeautifulSoup
from pypdf import PdfReader

from doc_chunker.models import Section

SUPPORTED_SUFFIXES = {".md", ".markdown", ".html", ".htm", ".pdf"}

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FENCE_STARTS = ("```", "~~~")


class UnsupportedFileError(ValueError):
    """Raised by read_file() for a file type this tool doesn't handle."""


class _SectionBuilder:
    """Collects lines under a nested heading path and turns them into Sections."""

    def __init__(self) -> None:
        self.stack: list[tuple[int, str]] = []  # [(level, title), ...]
        self.lines: list[str] = []  # content lines for the current section
        self.sections: list[Section] = []  # finished sections

    def add_line(self, line: str) -> None:
        self.lines.append(line)

    def start_heading(self, level: int, title: str) -> None:
        self.flush()  # close the previous section
        while self.stack and self.stack[-1][0] >= level:  # drop same-or-deeper headings
            self.stack.pop()
        self.stack.append((level, title))

    def flush(self) -> None:
        text = "\n".join(self.lines).strip()
        if text:  # skip empty sections
            heading = " > ".join(title for _, title in self.stack)
            self.sections.append(Section(heading, text))
        self.lines.clear()


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
    builder = _SectionBuilder()
    in_code = False

    for line in text.splitlines():
        if line.lstrip().startswith(FENCE_STARTS):
            in_code = not in_code  # entering or leaving a code block

        match = None if in_code else HEADING.match(line)  # no headings inside code
        if match:
            builder.start_heading(len(match.group(1)), match.group(2))
        else:
            builder.add_line(line)

    builder.flush()  # the last section
    return builder.sections


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
    soup = BeautifulSoup(html, "html.parser")

    tag_list = ["script", "style", "nav", "header", "footer"]

    for tag in soup.find_all(tag_list):
        tag.decompose()

    builder = _SectionBuilder()

    for tag in soup.find_all(["h1", "h2", "h3", "p", "li", "pre"]):
        text = " ".join(tag.get_text(" ").split())
        if tag.name in ("h1", "h2", "h3"):
            builder.start_heading(int(tag.name[1]), text)
        elif text:
            builder.add_line(text)

    builder.flush()
    return builder.sections


def read_pdf(path: Path) -> list[Section]:
    """One Section per PDF page that has text.

    Contract:
      - Use pypdf.PdfReader. Heading is "page N", with N starting at 1.
      - Page text is stripped. Pages with no text (blank or scanned images) are left out,
        but page numbers still count them: a blank page 2 means the next section is "page 3".
    """
    sections = []
    for number, page in enumerate(PdfReader(path).pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            sections.append(Section(f"page {number}", text))
    return sections


def read_file(path: Path) -> list[Section]:
    """Pick the right reader by file extension (case-insensitive).

    Contract:
      - .md / .markdown -> read_markdown, .html / .htm -> read_html (read text as UTF-8)
      - .pdf -> read_pdf
      - anything else -> raise UnsupportedFileError naming the file.
    """
    # TODO
    if not Path.exists(path):
        raise ValueError("Wrong path has been provided to the system")

    extension = path.suffix
    extension = extension.lower()

    if extension == ".md" or extension == ".markdown":
        return read_markdown(path.read_text(encoding="utf-8"))
    elif extension == ".htm" or extension == ".html":
        return read_html(path.read_text(encoding="utf-8"))
    elif extension == ".pdf":
        return read_pdf(path)
    else:
        raise UnsupportedFileError(f"cannot read {path}")
