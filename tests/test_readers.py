from pathlib import Path

import pytest

from doc_chunker.models import Section
from doc_chunker.readers import (
    UnsupportedFileError,
    read_file,
    read_html,
    read_markdown,
    read_pdf,
)

FIXTURES = Path(__file__).parent / "fixtures"


# --- Markdown ----------------------------------------------------------------


@pytest.fixture
def md_sections() -> list[Section]:
    return read_markdown((FIXTURES / "sample.md").read_text(encoding="utf-8"))


def test_markdown_heading_paths(md_sections):
    assert [s.heading for s in md_sections] == [
        "",
        "Installation",
        "Installation > Linux",
        "Installation > Windows",
        "Usage",
        "Usage > Deep option",
    ]


def test_markdown_preamble_and_simple_text(md_sections):
    assert md_sections[0] == Section("", "Intro paragraph before any heading.")
    assert md_sections[1] == Section("Installation", "Install with uv.")


def test_markdown_code_fence_is_not_a_heading(md_sections):
    linux = md_sections[2]
    assert "# this is a comment, not a heading" in linux.text
    assert linux.text.startswith("Run the script.")
    assert linux.text.endswith("```")


def test_markdown_hash_without_space_is_text(md_sections):
    assert md_sections[4] == Section("Usage", "#Not a heading because no space")


def test_markdown_empty_section_is_dropped(md_sections):
    assert all(s.text for s in md_sections)
    assert "Empty Section" not in [s.heading for s in md_sections]


def test_markdown_without_headings():
    assert read_markdown("just text\n\nmore text") == [Section("", "just text\n\nmore text")]


# --- HTML --------------------------------------------------------------------


@pytest.fixture
def html_sections() -> list[Section]:
    return read_html((FIXTURES / "sample.html").read_text(encoding="utf-8"))


def test_html_sections(html_sections):
    assert html_sections == [
        Section("", "Welcome text."),
        Section("Guide", "Guide intro."),
        Section("Guide > Setup", "Step one continues.\nItem A\nItem B"),
        Section("Guide > Setup > Advanced", "code here"),
        Section("Guide > FAQ", "Answer."),
    ]


@pytest.mark.parametrize("noise", ["Site header", "Home", "Copyright", "tracking", "color"])
def test_html_noise_is_removed(html_sections, noise):
    assert all(noise not in s.text for s in html_sections)


# --- PDF ---------------------------------------------------------------------


def test_pdf_one_section_per_page_with_text():
    assert read_pdf(FIXTURES / "sample.pdf") == [
        Section("page 1", "Hello from page one."),
        Section("page 3", "Final page text."),
    ]


# --- read_file ---------------------------------------------------------------


@pytest.mark.parametrize("name", ["sample.md", "sample.html", "sample.pdf"])
def test_read_file_dispatches_by_suffix(name):
    sections = read_file(FIXTURES / name)
    assert sections
    assert all(isinstance(s, Section) for s in sections)


def test_read_file_suffix_is_case_insensitive(tmp_path):
    f = tmp_path / "NOTES.MD"
    f.write_text("# Title\n\nBody", encoding="utf-8")
    assert read_file(f) == [Section("Title", "Body")]


def test_read_file_rejects_unknown_suffix(tmp_path):
    f = tmp_path / "notes.txt"
    f.write_text("hello", encoding="utf-8")
    with pytest.raises(UnsupportedFileError, match="notes.txt"):
        read_file(f)
